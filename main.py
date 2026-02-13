"""
Main Entry Point
- Step 1: Run RAG ingestion (embed documents into ChromaDB)
- Step 2: Start the FastAPI server

Usage:
    python main.py ingest    # Ingest documents into vector store
    python main.py serve     # Start the API server
    python main.py test      # Run a quick test query
"""

import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()


def ingest():
    """Run the RAG ingestion pipeline."""
    from rag.ingest import run_ingestion
    run_ingestion()


def serve():
    """Start the FastAPI server."""
    import uvicorn
    print("Starting AI Customer Support API...")
    print("Docs available at: http://localhost:8000/docs")
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)


async def test_query():
    """Run a quick test to verify the system works end-to-end."""
    from agents.orchestrator import handle_customer_query

    test_queries = [
        "What is your refund policy?",
        "Where is my order #1234?",
        "My order #1238 hasn't arrived yet. What can I do?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"CUSTOMER: {query}")
        print(f"{'='*60}")
        response = await handle_customer_query(query)
        print(f"\nAGENT: {response}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py ingest   - Ingest documents into vector store")
        print("  python main.py serve    - Start the API server")
        print("  python main.py test     - Run test queries")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "ingest":
        ingest()
    elif command == "serve":
        serve()
    elif command == "test":
        asyncio.run(test_query())
    else:
        print(f"Unknown command: {command}")
        print("Available commands: ingest, serve, test")
        sys.exit(1)
