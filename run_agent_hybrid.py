import argparse
import json
import dspy
import os
from agent.graph_hybrid import app

# -------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------
# Ensure this matches the model you just pulled (phi3.5)
MODEL_NAME = 'phi3.5' 
API_BASE = 'http://localhost:11434'

def setup_dspy():
    """Configures DSPy to use the local Ollama model."""
    print(f"Connecting to Ollama model: {MODEL_NAME}...")
    lm = dspy.LM(model=f"ollama/{MODEL_NAME}", api_base=API_BASE, temperature=0)
    dspy.configure(lm=lm)
    return lm

def run_batch(input_file, output_file):
    print(f"Reading from {input_file}...")
    
    results = []
    
    with open(input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            if not line.strip(): continue
            item = json.loads(line)
            
            q_id = item['id']
            question = item['question']
            format_hint = item['format_hint']
            
            print(f"\nProcessing ID: {q_id}")
            
            # Initialize State
            initial_state = {
                "id": q_id,
                "question": question,
                "format_hint": format_hint,
                "retry_count": 0,
                "tool_choice": "",
                "sql_query": "",
                "sql_error": "",
                "sql_results": [],
                "retrieved_docs": [],
                "final_answer": None,
                "explanation": "",
                "citations": []
            }
            
            # Run Graph
            try:
                final_state = app.invoke(initial_state)
                
                # Construct Output Object per Contract
                output_obj = {
                    "id": q_id,
                    "final_answer": final_state.get('final_answer'),
                    "sql": final_state.get('sql_query', ""),
                    "confidence": 1.0 if not final_state.get('sql_error') else 0.5,
                    "explanation": final_state.get('explanation', "No explanation generated."),
                    "citations": final_state.get('citations', [])
                }
                
                results.append(output_obj)
                
            except Exception as e:
                print(f"ERROR processing {q_id}: {e}")
                # Fallback for error
                results.append({
                    "id": q_id,
                    "final_answer": "Error",
                    "sql": "",
                    "confidence": 0.0,
                    "explanation": str(e),
                    "citations": []
                })

    # Write Output
    print(f"\nWriting results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for res in results:
            f_out.write(json.dumps(res) + "\n")
    
    print("Batch processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Retail Analytics Copilot")
    parser.add_argument("--batch", required=True, help="Input JSONL file")
    parser.add_argument("--out", required=True, help="Output JSONL file")
    
    args = parser.parse_args()
    
    # 1. Setup LM
    setup_dspy()
    
    # 2. Run Batch
    run_batch(args.batch, args.out)