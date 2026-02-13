"""
RAG Retriever
- Connects to the ChromaDB vector store
- Performs similarity search against user queries
- Returns relevant document chunks
"""

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")


def get_vector_store():
    """Connect to the existing ChromaDB vector store."""
    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    )
    vector_store = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="customer_support",
    )
    return vector_store


def retrieve(query: str, top_k: int = 3) -> str:
    """
    Search the vector store and return the top matching chunks as a string.

    Args:
        query: The user's question
        top_k: Number of results to return

    Returns:
        A formatted string of the most relevant document chunks
    """
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=top_k)

    if not results:
        return "No relevant information found in the knowledge base."

    context_parts = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        context_parts.append(f"[Source {i}: {source}]\n{doc.page_content}")

    return "\n\n---\n\n".join(context_parts)


if __name__ == "__main__":
    # Quick test
    test_query = "What is the refund policy?"
    print(f"Query: {test_query}\n")
    print(retrieve(test_query))
