import json
import requests
from langchain.tools import tool

@tool
def custom_api(input: str) -> str:
    """
    Calls your internal .NET microservice.
    Example endpoint: http://localhost:5000/api/summarise
    """
    endpoint = "http://localhost:5000/api/summarise"  # You can modify this line to use a dynamic endpoint
    payload = {"input": input}
    resp = requests.post(endpoint, json=payload)
    resp.raise_for_status()
    # Return the body as a string so the agent can read/use it.
    return json.dumps(resp.json(), indent=2)
