import os
import dspy
import re
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

# Import our local tools
from agent.tools.sqlite_tool import SQLiteDB
from agent.rag.retrieval import SimpleRetriever
from agent.dspy_signatures import RouterSignature, GenerateSQLSignature, SynthesizerSignature

# -------------------------------------------------------------------------
# Setup
# -------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), 'data', 'northwind.sqlite')
DOCS_PATH = os.path.join(os.path.dirname(BASE_DIR), 'docs')

db_tool = SQLiteDB(DB_PATH)
retriever_tool = SimpleRetriever(DOCS_PATH)

router = dspy.Predict(RouterSignature)
sql_generator = dspy.Predict(GenerateSQLSignature)
synthesizer = dspy.Predict(SynthesizerSignature)

# -------------------------------------------------------------------------
# State
# -------------------------------------------------------------------------
class AgentState(TypedDict):
    id: str
    question: str
    format_hint: str
    tool_choice: str
    retrieved_docs: List[Dict]
    sql_query: str
    sql_results: List[Dict]
    sql_error: str
    final_answer: Any
    explanation: str
    citations: List[str]
    retry_count: int

# -------------------------------------------------------------------------
# Helper: Resilience Patch for SQL
# -------------------------------------------------------------------------
def clean_sql_query(sql: str) -> str:
    """
    Auto-corrects common LLM mistakes for SQLite.
    """
    # 1. Remove markdown
    sql = sql.replace("```sql", "").replace("```", "").strip()
    
    # 2. Extract SELECT statement if buried in text
    match = re.search(r"(SELECT.*?(?:;|$))", sql, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()
        
    # 3. FIX: Replace YEAR(x) with strftime('%Y', x)
    # Regex finds YEAR(anything) and turns it into SQLite format
    sql = re.sub(r"YEAR\((.*?)\)", r"strftime('%Y', \1)", sql, flags=re.IGNORECASE)

    # 4. FIX: Replace MONTH(x) with strftime('%m', x)
    sql = re.sub(r"MONTH\((.*?)\)", r"strftime('%m', \1)", sql, flags=re.IGNORECASE)
    
    # 5. Ensure it ends with ;
    if not sql.endswith(";"): 
        sql += ";"
        
    return sql

# -------------------------------------------------------------------------
# Nodes
# -------------------------------------------------------------------------

def router_node(state: AgentState):
    """Decide tool with KEYWORD OVERRIDES."""
    print(f"--- [Router] Analyzing: {state['question'][:40]}... ---")
    question = state['question'].lower()
    
    try:
        pred = router(question=state['question'])
        text = pred.answer.lower()
        if 'sql' in text and 'rag' not in text: choice = 'sql'
        elif 'rag' in text and 'sql' not in text: choice = 'rag'
        else: choice = 'hybrid'
    except:
        choice = 'hybrid'

    # Logic Booster: Force Hybrid/SQL for math
    math_keywords = ['how many', 'quantity', 'revenue', 'count', 'total', 'average', 'margin', 'top', 'highest', 'best']
    if any(k in question for k in math_keywords):
        if choice == 'rag':
            print("--- [Router] Override: Detected math question. Forcing Hybrid. ---")
            choice = 'hybrid'

    return {"tool_choice": choice}

def retriever_node(state: AgentState):
    """Fetch docs."""
    print("--- [Retriever] Fetching docs... ---")
    docs = retriever_tool.retrieve(state['question'], k=3)
    return {"retrieved_docs": docs}

def sql_generator_node(state: AgentState):
    """Generate SQL and Apply Resilience Patch."""
    print("--- [SQL Gen] Generating Query... ---")
    
    schema = """
    Tables:
    - orders (OrderID, OrderDate, CustomerID)
    - order_items (OrderID, ProductID, UnitPrice, Quantity, Discount)
    - products (ProductID, ProductName, CategoryID, SupplierID)
    - categories (CategoryID, CategoryName)
    - customers (CustomerID, CompanyName)
    """
    
    doc_context = ""
    if state.get('retrieved_docs'):
        doc_context = "\nCONTEXT (Use dates/definitions from here!):" + "\n".join([f"- {d['text']}" for d in state['retrieved_docs']])
    
    full_input = f"Question: {state['question']}\n{schema}\n{doc_context}"
    
    if state.get('sql_error'):
        full_input += f"\nFIX PREVIOUS ERROR: {state['sql_error']}"

    try:
        pred = sql_generator(question=full_input, schema_context=schema)
        # Apply the cleaner function
        clean_sql = clean_sql_query(pred.sql_query)
    except:
        clean_sql = "SELECT 1;"

    return {"sql_query": clean_sql}

def sql_executor_node(state: AgentState):
    """Execute SQL."""
    query = state['sql_query']
    print(f"--- [Executor] Running: {query[:60]}... ---")
    result = db_tool.execute_query(query)
    
    if isinstance(result, str) and result.startswith("Error"):
        return {"sql_error": result, "sql_results": []}
    else:
        return {"sql_results": result, "sql_error": None}

def repair_check_node(state: AgentState):
    if state.get('sql_error'):
        return {"retry_count": state.get('retry_count', 0) + 1}
    return {}

def synthesizer_node(state: AgentState):
    """Synthesize answer."""
    print("--- [Synthesizer] formulating answer... ---")
    
    context = ""
    if state.get('sql_results'):
        context += f"DB RESULTS: {str(state['sql_results'])[:800]}\n"
    if state.get('retrieved_docs'):
        context += f"DOCS: {str([d['text'][:200] for d in state['retrieved_docs']])}\n"
    
    if not state.get('sql_results') and state.get('tool_choice') != 'rag':
         # If we expected SQL data but got none
         final_text = "Could not calculate (No data found matching criteria)."
    else:
        try:
            pred = synthesizer(question=state['question'], context=context)
            final_text = pred.answer.strip()
            if "Answer:" in final_text:
                final_text = final_text.split("Answer:")[-1].strip()
        except:
            final_text = "Could not determine."

    citations = []
    if state.get('retrieved_docs'):
        citations = [d['id'] for d in state['retrieved_docs']]
    if state.get('sql_results'):
        citations.append("Database")
        
    return {
        "final_answer": final_text,
        "explanation": "Derived from database and docs.",
        "citations": citations
    }

# -------------------------------------------------------------------------
# Graph Construction
# -------------------------------------------------------------------------
workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("sql_gen", sql_generator_node)
workflow.add_node("executor", sql_executor_node)
workflow.add_node("repair", repair_check_node)
workflow.add_node("synthesizer", synthesizer_node)

workflow.set_entry_point("router")

def route_decision(state):
    return "retriever" if state['tool_choice'] in ['rag', 'hybrid'] else "sql_gen"

workflow.add_conditional_edges("router", route_decision, {"retriever": "retriever", "sql_gen": "sql_gen"})

def post_retrieval(state):
    return "synthesizer" if state['tool_choice'] == 'rag' else "sql_gen"

workflow.add_conditional_edges("retriever", post_retrieval, {"synthesizer": "synthesizer", "sql_gen": "sql_gen"})

workflow.add_edge("sql_gen", "executor")
workflow.add_edge("executor", "repair")

def repair_logic(state):
    if state.get('sql_error') and state.get('retry_count', 0) < 2:
        return "retry"
    return "synthesizer"

workflow.add_conditional_edges("repair", repair_logic, {"retry": "sql_gen", "synthesizer": "synthesizer"})
workflow.add_edge("synthesizer", END)

app = workflow.compile()