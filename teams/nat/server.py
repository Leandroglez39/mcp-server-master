# server.py
import os
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
from mcp.server.fastmcp import FastMCP

_ = load_dotenv(".env")  # Load environment variables from .env file


# Create an MCP server
mcp = FastMCP("Demo")


@mcp.tool()
def brave_search_and_extract(query: str, pages: int = 3, results_per_page: int = 20):
    """
    Perform a Brave Search for the given query, paginate through 'pages' pages,
    and extract full page text for each result.

    Args:
        query (str): The search query string.
        pages (int): Number of pages to retrieve (default 3).
        results_per_page (int): Number of results per page (max 50).

    Returns:
        dict: A mapping from each result URL to its extracted plain text.
    """
    # Load Brave API key from environment variable
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        raise ValueError("BRAVE_API_KEY environment variable is not set.")  # :contentReference[oaicite:15]{index=15}

    endpoint = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }

    # Container for all URLs to fetch
    all_urls = []

    # 1. Paginate through the Brave Search API
    for offset in range(pages):
        params = {
            "q": query,
            "count": results_per_page,  # :contentReference[oaicite:16]{index=16}
            "offset": offset,           # :contentReference[oaicite:17]{index=17}
        }
        response = requests.get(endpoint, headers=headers, params=params, timeout=30)  # :contentReference[oaicite:18]{index=18}
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()       # :contentReference[oaicite:19]{index=19}

        #print(data)
        print(f"Processing page {offset + 1} of results...")  # :contentReference[oaicite:20]{index=20}
        
        # Extract URLs from the response
        web_results = data.get("web", {}).get("results", [])

        print(f"Found {len(web_results)} results on page {offset + 1}.")  # :contentReference[oaicite:21]{index=21}
        for result in web_results:
            url = result.get("url")
            if url:
                all_urls.append(url)

        print(f"Total URLs collected so far: {len(all_urls)}")  # :contentReference[oaicite:22]{index=22}
        print(all_urls)
        # Respectful delay between API calls
        time.sleep(1)

    # 2. Fetch and extract text from each URL
    extracted_texts = {}
    # Bonus: set a custom header to mimic a real browser, avoiding potential blocking
    fetch_headers = {"User-Agent": "Mozilla/5.0 (compatible; Python script)"}

    for url in all_urls:
        try:
            page_resp = requests.get(url, headers=fetch_headers, timeout=30)  # :contentReference[oaicite:20]{index=20}
            page_resp.raise_for_status()
            soup = BeautifulSoup(page_resp.text, "html.parser")               # :contentReference[oaicite:21]{index=21}
            # Extract all visible text
            text = soup.get_text(separator="\n", strip=True)                  # :contentReference[oaicite:22]{index=22}
            extracted_texts[url] = text
        except Exception as e:
            # Skip URLs that time out or cause errors
            extracted_texts[url] = f"Error retrieving or parsing page: {e}"

        # Optional: small delay to avoid hammering servers
        time.sleep(0.5)

    return extracted_texts

if __name__ == "__main__":    
    # Start the MCP server
    mcp.run(transport="stdio")