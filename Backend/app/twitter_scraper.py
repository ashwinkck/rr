import requests

# Replace with your actual API key
API_KEY = "07a71ac759204c2fafccf9289fa46481bf8b252b"

# Define your search query
query = "Uniswap site:twitter.com"

# Perform the search
response = requests.post(
    "https://google.serper.dev/search",
    headers={"X-API-KEY": API_KEY},
    json={"q": query}
)

# Parse and print results
if response.status_code == 200:
    results = response.json().get("organic", [])
    print(f"Found {len(results)} results:\n")
    for r in results[:5]:  # Get top 5 tweets
        print(f"Title: {r.get('title')}")
        print(f"Snippet: {r.get('snippet')}")
        print(f"Link: {r.get('link')}\n")
else:
    print("Error:", response.text)
