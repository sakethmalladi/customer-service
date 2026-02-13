"""
RAG Agent
- Receives a user query
- Searches the knowledge base (FAQs, policies) using vector similarity
- Returns relevant context to the orchestrator
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.retriever import retrieve


def search_knowledge_base(query: str) -> str:
    """
    Search the knowledge base for information relevant to the query.

    Args:
        query: The user's question or search terms

    Returns:
        Relevant document excerpts from FAQs and policies
    """
    results = retrieve(query, top_k=3)
    return results


RAG_AGENT_SYSTEM_MESSAGE = """You are a Knowledge Base Agent. Your role is to search
the company's FAQ and policy documents to find relevant information.

When asked a question:
1. Use the search_knowledge_base function to find relevant information.
2. Return the retrieved context as-is — do NOT make up answers.
3. If no relevant information is found, say so clearly.

You only answer based on retrieved documents. Never fabricate information."""
