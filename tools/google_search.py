import json
import requests
import bs4
from langchain.tools import tool

@tool
def google_search(query: str) -> str:
    """
    Scrapes DuckDuckGo (no API key) for the first 5 organic results.
    """
    url = "https://duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    r = requests.post(url, data={"q": query}, headers=headers)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    results = []
    for result in soup.select(".result__title"):
        title = result.text.strip()
        link = result.find("a")["href"] if result.find("a") else None
        if title and link:
            results.append({"title": title, "link": link})
    return json.dumps(results, indent=2)
