import json
import faiss
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
import pathlib
import importlib

# Load environment variables from .env file
load_dotenv()

def json_to_faiss(json_file_path: str, faiss_index_path: str):
    """
    Convert JSON data into FAISS chunks for querying with LLM.
    
    Args:
        json_file_path (str): Path to the JSON file.
        faiss_index_path (str): Path to save the FAISS index.
    
    Returns:
        FAISS: The FAISS index object.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
    # Try to read from settings.json
        settings_path = pathlib.Path(__file__).parent / "settings.json"
        if settings_path.exists():
            with open(settings_path, "r", encoding="utf-8") as f:
                try:
                    settings = json.load(f)
                    openai_api_key = settings.get("OPENAI_API_KEY")
                except Exception:
                    openai_api_key = None
        if not openai_api_key:
            openai_api_key = input("Enter your OpenAI API key: ").strip()
    #print(f"Using OpenAI API key: {api_key}")
    # Step 1: Load JSON data
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Step 2: Extract text chunks from JSON and add metadata
    from langchain_core.documents import Document
    documents = []
    for ticket in data.get("tickets", []):
        chunk = f"ID: {ticket['id']}\nSummary: {ticket['summary']}\nDescription: {ticket['description']}"
        metadata = {"id": str(ticket["id"])}
        documents.append(Document(page_content=chunk, metadata=metadata))
    
    # Step 3: Generate embeddings using OpenAI embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)  # Ensure your OpenAI API key is set in the environment
    
    # Step 4: Create FAISS index with documents and metadata
    faiss_index = FAISS.from_documents(documents, embeddings)
    
    # Step 5: Save the FAISS index
    faiss_index.save_local(faiss_index_path)
    print(f"FAISS index saved to {faiss_index_path}")
    
    return faiss_index