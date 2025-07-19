<<<<<<< HEAD
import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# API Key from .env
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Headers for OpenRouter
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Main summarization function
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

    try:
        print("[+] Sending request to OpenRouter...")
        response = requests.post(url, headers=HEADERS, json=payload)
        print("[+] Got response:", response.status_code)

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return content.strip()
        else:
            print("[-] Failed. Response:")
            print(response.text)
            return "Error: Failed to summarize."

    except Exception as e:
        print("[-] Exception occurred:", str(e))
        return "Error: Exception during summarization."

# Example test run
if __name__ == "__main__":
    test_text = "Ancient Bitcoin whale completes $9.53B selloff after 14 years, turns $132K into billions"
    summary = summarize_text(test_text)
    print("\nSummary:", summary)
=======
import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# API Key from .env
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Headers for OpenRouter
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Main summarization function
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

    try:
        print("[+] Sending request to OpenRouter...")
        response = requests.post(url, headers=HEADERS, json=payload)
        print("[+] Got response:", response.status_code)

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return content.strip()
        else:
            print("[-] Failed. Response:")
            print(response.text)
            return "Error: Failed to summarize."

    except Exception as e:
        print("[-] Exception occurred:", str(e))
        return "Error: Exception during summarization."

# Example test run
if __name__ == "__main__":
    test_text = "Ancient Bitcoin whale completes $9.53B selloff after 14 years, turns $132K into billions"
    summary = summarize_text(test_text)
    print("\nSummary:", summary)
>>>>>>> 39ef0634114b10de3a3ac524d795525f7ba964b4
