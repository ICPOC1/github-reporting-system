import os

import requests
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

OWNER = "PraharshaIncepteolabs"
REPOSITORY = "TEST"

API_URL = f"https://api.github.com/repos/{OWNER}/{REPOSITORY}/commits"


headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2026-03-10"
}


response = requests.get(
    API_URL,
    headers=headers,
    params={"per_page": 10},
    timeout=30
)


print("HTTP Status:", response.status_code)


if response.status_code == 200:
    commits = response.json()

    print(f"\nRepository: {OWNER}/{REPOSITORY}")
    print(f"Commits retrieved: {len(commits)}")
    print("-" * 60)

    for commit in commits:
        sha = commit["sha"]
        message = commit["commit"]["message"]
        author = commit["commit"]["author"]["name"]
        date = commit["commit"]["author"]["date"]

        print(f"SHA     : {sha}")
        print(f"Author  : {author}")
        print(f"Date    : {date}")
        print(f"Message : {message}")
        print("-" * 60)

else:
    print("GitHub API request failed.")
    print("Response:", response.text)