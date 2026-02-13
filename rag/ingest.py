import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

def load_documents():
    docs = []
    for filename in ["faqs.md", "policies.md"]:
        filepath = os.path.join(DATA_DIR, filename)
        loader = TextLoader(filepath, encoding="utf-8")
        docs.extend(loader.load())
    print(f"Loaded {len(docs)} documents")
    return docs

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def create_vector_store(chunks):
    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    )
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name="customer_support",
    )
    print(f"Vector store created at {CHROMA_DIR} with {len(chunks)} vectors")
    return vector_store


def run_ingestion():
    """Run the full ingestion pipeline."""
    print("--- Starting RAG Ingestion ---")
    docs = load_documents()
    chunks = split_documents(docs)
    vector_store = create_vector_store(chunks)
    print("--- Ingestion Complete ---")
    return vector_store


if __name__ == "__main__":
    run_ingestion()