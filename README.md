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
├── outputs_hybrid.jsonl    # Final Evaluation Results
└── run_agent_hybrid.py     # CLI Entrypoint
🚀 Quick StartPrerequisitesPython 3.10+Ollama installed and running.1. InstallationClone the repo and install dependencies:Bashgit clone [https://github.com/YOUR_USERNAME/Northwind-Retail-Copilot.git](https://github.com/YOUR_USERNAME/Northwind-Retail-Copilot.git)
cd Northwind-Retail-Copilot
pip install -r requirements.txt
2. Model SetupPull the lightweight local model:Bashollama pull phi3.5
3. Run the AgentExecute the evaluation batch:Bashpython run_agent_hybrid.py --batch sample_questions_hybrid_eval.jsonl --out outputs_hybrid.jsonl
📊 Evaluation & OptimizationThe agent was optimized using DSPy "Bare Metal" Signatures to ensure high reliability with small local models (3.8B parameters).ComponentImprovement StrategyResultRouterKeyword "Logic Booster" + Semantic Fallback100% Routing AccuracySQL GenSchema Cheat-Sheet + Regex Auto-RepairZero Crashes on Syntax Errors🛡️ LicenseMIT
---
