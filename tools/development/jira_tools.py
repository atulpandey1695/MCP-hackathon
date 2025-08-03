"""
JIRA integration tools
"""
import json
import requests
from enhanced_context_manager import get_context_manager
from langchain.tools import tool
from tools.utils.faiss_converter import json_to_faiss

@tool
def jira_ticket_summarizer(domainUrl: str, userName: str, token: str, query: str) -> str:
    """
    Fetch JIRA tickets, summarize them into a PRD, and save the context in JSON format.
    """
    # Validate input parameters
    if not all([domainUrl, userName, token, query]):
        return "Missing required parameters. Please provide domainUrl, userName, token, and query."

    # Construct JIRA API URL and credentials dynamically
    jira_api_url = f"{domainUrl}/rest/api/latest/search"
    auth = (userName, token)

    # Step 1: Fetch JIRA tickets
    tickets = fetch_jira_tickets(jira_api_url, auth, query)

    print(f"Fetched {len(tickets)} JIRA tickets.")
    
    # Step 2: Summarize tickets into a PRD
    prd = summarize_tickets(tickets)
    
    # Step 3: Save the PRD to a JSON file
    save_prd_to_json(prd)

    convert_to_faiss()
    
    return "JIRA tickets summarized and saved to jira_tickets_stories_context.json."

def fetch_jira_tickets(jira_api_url: str, auth: tuple, query: str):
    """Fetch JIRA tickets using the JIRA API."""
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "jql": query,
        "fields": "*all"
    }
    response = requests.get(jira_api_url, headers=headers, auth=auth, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch JIRA tickets: {response.status_code} - {response.text}")

    data = response.json()
    issues = data.get("issues", [])
    total = data.get("total", 0)
    start_at = data.get("startAt", 0)
    max_results = data.get("maxResults", 50)

    # Fetch additional pages if needed
    while start_at + max_results < total:
        start_at += max_results
        params["startAt"] = start_at
        response = requests.get(jira_api_url, headers=headers, auth=auth, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch JIRA tickets: {response.status_code} - {response.text}")
        data = response.json()
        issues.extend(data.get("issues", []))
        max_results = data.get("maxResults", 50)

    return issues

def summarize_tickets(tickets):
    """Summarize JIRA tickets into a PRD format."""
    prd = {
        "title": "Product Requirements Document",
        "tickets": []
    }
    for ticket in tickets:
        prd["tickets"].append({
            "id": ticket["key"],
            "summary": ticket["fields"]["summary"],
            "description": ticket["fields"]["description"]
        })
    return prd

def save_prd_to_json(prd):
    """Save the PRD to a JSON file."""
    with open("tools/output/jira_tickets_stories_context.json", "w") as f:
        json.dump(prd, f, indent=2)

def convert_to_faiss():
    # Convert JSON to FAISS chunks
    json_file_path = "tools/output/jira_tickets_stories_context.json"
    faiss_index_path = "tools/output/jira_tickets_stories_faiss_index"
    faiss_index = json_to_faiss(json_file_path, faiss_index_path)
    print(f"FAISS index created {faiss_index}")
