import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def summarize_text(text, model="mistralai/mistral-7b-instruct"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a concise and accurate summarizer."},
            {"role": "user", "content": f"Summarize this:\n\n{text}"}
        ],
        "temperature": 0.7
    }

    print("[+] Sending request to OpenRouter...")
    response = requests.post(url, headers=HEADERS, json=payload)

    print("[+] Got response:", response.status_code)
    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        return content
    else:
        print("[-] Failed. Response:")
        print(response.text)
        return "Error: Failed to summarize."

if __name__ == "__main__":
    test_text = "Ancient Bitcoin whale completes $9.53B selloff after 14 years, turns $132K into billions"
    summary = summarize_text(test_text)
    print("\nSummary:", summary)
