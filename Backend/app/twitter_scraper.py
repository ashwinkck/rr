import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

API_KEY = os.getenv("SERPER_API_KEY")

query = "Uniswap site:twitter.com"

response = requests.post(
    "https://google.serper.dev/search",
    headers={"X-API-KEY": API_KEY},
    json={"q": query}
)

if response.status_code == 200:
    results = response.json().get("organic", [])
    print(f"Found {len(results)} results:\n")
    for r in results[:5]:
        print(f"Title: {r.get('title')}")
        print(f"Snippet: {r.get('snippet')}")
        print(f"Link: {r.get('link')}\n")
else:
    print("Error:", response.text)