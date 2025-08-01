import json, requests

def custom_api(endpoint: str, payload: dict | None = None) -> str:
    """
    Calls your internal .NET microservice.
    Example endpoint: http://localhost:5000/api/summarise
    """
    resp = requests.post(endpoint, json=payload or {})
    resp.raise_for_status()
    # Return the body as a string so the agent can read/use it.
    return json.dumps(resp.json(), indent=2)
