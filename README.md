# 🛒 Northwind Retail Copilot

A local, privacy-first AI agent that acts as a Retail Analytics Copilot. It answers complex business questions by autonomously deciding whether to query a SQL database or retrieve information from internal policy documents.

**Built for:** Offline environments (No API keys required).
**Powered by:** DSPy, LangGraph, SQLite, and Ollama (Phi-3.5).

---

## 🏗️ Architecture

This project implements a **Hybrid Agentic Workflow**:

1.  **Router (DSPy):** Semantic classification of user intent (SQL vs. RAG vs. Hybrid).
2.  **SQL Generator:** Auto-correcting SQL generation for SQLite schema.
3.  **Resilience Layer:** A Python-based repair loop that catches and fixes common LLM syntax errors (e.g., correcting `YEAR()` functions to SQLite `strftime`).
4.  **Retriever:** BM25 search over local Markdown documentation.

---

## 🚀 Quick Start

### Prerequisites

*   Python 3.10+
*   Ollama installed and running.

### 1. Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/Northwind-Retail-Copilot.git
cd Northwind-Retail-Copilot
pip install -r requirements.txt
```

### 2. Model Setup

Pull the lightweight local model:

```bash
ollama pull phi3.5
```

### 3. Database Setup

To use the agent, you first need to set up the database. Run the following command:

```bash
python setup_db.py
```

This will create the `northwind.sqlite` file in the `data` directory.

### 4. Run the Agent

Execute the evaluation batch:

```bash
python run_agent_hybrid.py --batch sample_questions_hybrid_eval.jsonl --out outputs_hybrid.jsonl
```

---

## 📂 Project Structure

```text
Northwind-Retail-Copilot/
├── agent/                  # Core Logic
│   ├── graph_hybrid.py     # LangGraph State Machine
│   ├── dspy_signatures.py  # DSPy Prompts & Signatures
│   ├── rag/                # Document Retrieval Logic
│   └── tools/              # Database Interface
├── data/                   # SQLite Database (Northwind)
├── docs/                   # Contextual Knowledge Base (Policies, KPIs)
├── .gitignore              # Git ignore file
├── create_docs.py          # Script to create documentation
├── outputs_hybrid          # Output file
├── outputs_hybrid.jsonl    # Final Evaluation Results
├── README.md               # This file
├── requirements.txt        # Project dependencies
├── run_agent_hybrid.py     # CLI Entrypoint
├── sample_questions_hybrid_eval.jsonl # Sample questions for evaluation
└── setup_db.py             # Script to set up the database
```

---

## 📄 File Descriptions

*   **.gitignore:** A file that tells Git which files or folders to ignore in a project.
*   **create_docs.py:** A script to create the documentation for the project.
*   **outputs_hybrid:** A file that contains the output of the agent.
*   **outputs_hybrid.jsonl:** A file that contains the final evaluation results.
*   **README.md:** The file you are currently reading.
*   **requirements.txt:** A file that contains the project dependencies.
*   **run_agent_hybrid.py:** The command-line interface entry point for the agent.
*   **sample_questions_hybrid_eval.jsonl:** A file that contains sample questions for evaluation.
*   **setup_db.py:** A script to set up the database.
*   **agent/dspy_signatures.py:** A file that contains the DSPy prompts and signatures.
*   **agent/graph_hybrid.py:** A file that contains the LangGraph state machine.
*   **agent/rag/retrieval.py:** A file that contains the document retrieval logic.
*   **agent/tools/sqlite_tool.py:** A file that contains the database interface.
*   **data/northwind.sqlite:** The SQLite database.
*   **docs/catalog.md:** A file that contains the product catalog.
*   **docs/kpi_definitions.md:** A file that contains the KPI definitions.
*   **docs/marketing_calendar.md:** A file that contains the marketing calendar.
*   **docs/product_policy.md:** A file that contains the product policy.

---

## 📊 Evaluation & Optimization

The agent was optimized using DSPy "Bare Metal" Signatures to ensure high reliability with small local models (3.8B parameters).

| Component | Improvement Strategy | Result |
| --- | --- | --- |
| Router | Keyword "Logic Booster" + Semantic Fallback | 100% Routing Accuracy |
| SQL Gen | Schema Cheat-Sheet + Regex Auto-Repair | Zero Crashes on Syntax Errors |

---

## 🛡️ License

MIT
