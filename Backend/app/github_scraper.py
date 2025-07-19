<<<<<<< HEAD
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_repo_info(owner, repo):
    base_url = f"https://api.github.com/repos/{owner}/{repo}"

    # Get basic repo details
    repo_resp = requests.get(base_url, headers=headers).json()
    contributors_resp = requests.get(f"{base_url}/contributors", headers=headers).json()
    commits_resp = requests.get(f"{base_url}/commits", headers=headers).json()
    print("COMMITS RESPONSE:", commits_resp)
    issues_resp = requests.get(f"{base_url}/issues?state=open", headers=headers).json()

    return {
        "name": repo_resp.get("full_name"),
        "description": repo_resp.get("description"),
        "stars": repo_resp.get("stargazers_count"),
        "forks": repo_resp.get("forks_count"),
        "open_issues": repo_resp.get("open_issues_count"),
        "license": repo_resp.get("license", {}).get("name"),
        "last_push": repo_resp.get("pushed_at"),
        "last_commit": commits_resp[0].get("commit", {}).get("author", {}).get("date") if commits_resp else None,
        "contributors_count": len(contributors_resp) if isinstance(contributors_resp, list) else 0,
        "days_since_last_commit": (
            (datetime.utcnow() - datetime.strptime(commits_resp[0]['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")).days
            if commits_resp else None
        )
    }

# Example usage
if __name__ == "__main__":
    data = get_repo_info("Uniswap", "uniswap-v3-core")
    print(data)
=======
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_repo_info(owner, repo):
    base_url = f"https://api.github.com/repos/{owner}/{repo}"

    # Get basic repo details
    repo_resp = requests.get(base_url, headers=headers).json()
    contributors_resp = requests.get(f"{base_url}/contributors", headers=headers).json()
    commits_resp = requests.get(f"{base_url}/commits", headers=headers).json()
    print("COMMITS RESPONSE:", commits_resp)
    issues_resp = requests.get(f"{base_url}/issues?state=open", headers=headers).json()

    return {
        "name": repo_resp.get("full_name"),
        "description": repo_resp.get("description"),
        "stars": repo_resp.get("stargazers_count"),
        "forks": repo_resp.get("forks_count"),
        "open_issues": repo_resp.get("open_issues_count"),
        "license": repo_resp.get("license", {}).get("name"),
        "last_push": repo_resp.get("pushed_at"),
        "last_commit": commits_resp[0].get("commit", {}).get("author", {}).get("date") if commits_resp else None,
        "contributors_count": len(contributors_resp) if isinstance(contributors_resp, list) else 0,
        "days_since_last_commit": (
            (datetime.utcnow() - datetime.strptime(commits_resp[0]['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")).days
            if commits_resp else None
        )
    }

# Example usage
if __name__ == "__main__":
    data = get_repo_info("Uniswap", "uniswap-v3-core")
    print(data)
>>>>>>> 39ef0634114b10de3a3ac524d795525f7ba964b4
