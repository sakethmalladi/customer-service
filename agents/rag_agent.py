import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.retriever import retrieve


def search_knowledge_base(query: str) -> str:
    results = retrieve(query, top_k=3)
    return results
