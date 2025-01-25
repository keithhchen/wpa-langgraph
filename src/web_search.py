from typing import List
from langchain_community.tools import DuckDuckGoSearchRun

def search_web(query: str, max_results: int = 3) -> List[dict]:
    """Search the web using DuckDuckGo and return relevant results."""
    try:
        query = query.strip()
        if not query:
            print("Error: Empty search query")
            return []
        
        keywords = query
        keywords = "a16z"
        print(f"Searching for: {keywords}")
            
        search = DuckDuckGoSearchRun()
        result = search.invoke(keywords)
        print(f"Raw search result: {result}")
        
        if not result:
            print(f"No search results found for keywords: {keywords}")
            return ""
            
        return result

    except Exception as e:
        print(f"Error during web search: {e}")
        return ""

def enrich_content(topic: str) -> str:
    """Search and compile relevant background information for a topic."""
    search_results = search_web(topic)
    return search_results