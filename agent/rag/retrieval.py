import os
import re
from rank_bm25 import BM25Okapi
from typing import List, Dict

class SimpleRetriever:
    def __init__(self, docs_path: str):
        self.docs_path = docs_path
        self.chunks = []
        self.bm25 = None
        self._load_and_chunk()
        self._build_index()

    def _load_and_chunk(self):
        """
        Reads all .md files in docs_path and splits them into chunks.
        Splits by markdown headers (##) to keep context together.
        """
        if not os.path.exists(self.docs_path):
            raise FileNotFoundError(f"Docs folder not found: {self.docs_path}")

        for filename in os.listdir(self.docs_path):
            if filename.endswith(".md"):
                filepath = os.path.join(self.docs_path, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Split by Level 2 headers (## Title)
                # We prepend the header back to the chunk so context isn't lost
                parts = re.split(r'(^##\s.*)', content, flags=re.MULTILINE)
                
                # The first part (index 0) is usually the title/intro before the first ##
                # subsequent parts are [header, content, header, content...]
                
                current_doc_name = filename.replace(".md", "")
                
                # Handle the intro part (before first ##)
                if parts[0].strip():
                    self.chunks.append({
                        "id": f"{current_doc_name}::intro",
                        "text": parts[0].strip(),
                        "source": filename
                    })

                # Handle the rest (header + body)
                for i in range(1, len(parts), 2):
                    header = parts[i].strip()
                    body = parts[i+1].strip() if i+1 < len(parts) else ""
                    full_text = f"{header}\n{body}"
                    
                    # specific ID for citation e.g., marketing_calendar::Summer Beverages 1997
                    # Clean header for ID
                    clean_header = re.sub(r'[^\w\s-]', '', header.replace("##", "").strip())
                    chunk_id = f"{current_doc_name}::{clean_header}"
                    
                    self.chunks.append({
                        "id": chunk_id,
                        "text": full_text,
                        "source": filename
                    })

    def _build_index(self):
        """
        Tokenizes chunks and builds the BM25 index.
        """
        tokenized_corpus = [chunk["text"].lower().split() for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        """
        Returns top k relevant chunks for the query.
        """
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Zip scores with chunks
        scored_chunks = []
        for i, score in enumerate(scores):
            scored_chunks.append({
                "score": score,
                "chunk": self.chunks[i]
            })
        
        # Sort by score descending and take top k
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return [item["chunk"] for item in scored_chunks[:k]]

# Quick test block
if __name__ == "__main__":
    # Adjust path assuming running from project root or agent/rag
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../docs"))
    print(f"Loading docs from: {base_path}")
    
    retriever = SimpleRetriever(base_path)
    print(f"Loaded {len(retriever.chunks)} chunks.")
    
    test_query = "return policy for beverages"
    print(f"\nQuery: {test_query}")
    results = retriever.retrieve(test_query, k=2)
    
    for r in results:
        print(f"--- {r['id']} ---\n{r['text'][:100]}...")