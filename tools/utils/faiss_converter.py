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

def json_to_faiss(json_file_path: str, faiss_index_path: str):
    """
    Convert JSON data into FAISS chunks for querying with LLM.
    
    Args:
        json_file_path (str): Path to the JSON file.
        faiss_index_path (str): Path to save the FAISS index.
    
    Returns:
        FAISS: The FAISS index object.
    """
 
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

def codebase_json_to_faiss(json_file_path: str, faiss_index_path: str):
    import json
    from langchain_core.documents import Document
    from langchain_openai.embeddings import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS

    # Load JSON data (list of dicts)
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Build documents from codebase_index.json
    documents = []
    for entry in data:
        # Compose a chunk from available fields
        chunk = ""
        if "file" in entry:
            chunk += f"File: {entry['file']}\n"
        if "name" in entry:
            chunk += f"Name: {entry['name']}\n"
        if "type" in entry:
            chunk += f"Type: {entry['type']}\n"
        if "doc" in entry and entry["doc"]:
            chunk += f"Doc: {entry['doc']}\n"
        if "comments" in entry and entry["comments"]:
            chunk += "Comments: " + "\n".join(entry["comments"]) + "\n"
        if "content" in entry and entry["content"]:
            chunk += f"Content: {entry['content']}\n"
        if not chunk:
            continue
        metadata = {k: v for k, v in entry.items() if k != "content"}
        documents.append(Document(page_content=chunk, metadata=metadata))

    # Generate embeddings and create FAISS index
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    faiss_index = FAISS.from_documents(documents, embeddings)
    faiss_index.save_local(faiss_index_path)
    print(f"FAISS index saved to {faiss_index_path}")
    return faiss_index

# Function to convert remote_git_history.json to FAISS index
def remote_git_history_to_faiss(json_file_path: str, faiss_index_path: str):
    """
    Convert remote_git_history.json git commit data into FAISS chunks for semantic search.
    Args:
        json_file_path (str): Path to the remote_git_history.json file.
        faiss_index_path (str): Path to save the FAISS index.
    Returns:
        FAISS: The FAISS index object.
    """
    from langchain_core.documents import Document
    # Load JSON data
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract commit data
    commits = data.get("commits", [])
    documents = []
    for commit in commits:
        chunk = f"SHA: {commit['sha']}\nMessage: {commit['message']}\nAuthor: {commit['author']['name']} <{commit['author']['email']}>\nAuthored: {commit['authored_date']}\nCommitted: {commit['committed_date']}\nChanged Files: {', '.join(commit.get('changed_files', []))}"
        metadata = {
            "sha": commit["sha"],
            "short_sha": commit.get("short_sha"),
            "author": commit["author"]["name"],
            "authored_date": commit["authored_date"],
            "committed_date": commit["committed_date"]
        }
        documents.append(Document(page_content=chunk, metadata=metadata))

    # Generate embeddings and create FAISS index
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    faiss_index = FAISS.from_documents(documents, embeddings)
    faiss_index.save_local(faiss_index_path)
    print(f"FAISS index saved to {faiss_index_path}")
    return faiss_index
