import os

import requests
from dotenv import load_dotenv


# ============================================================
# GitHub Usage & Access Reporting System
# Step 3 - Commit Collector Test
# ============================================================


# ------------------------------------------------------------
# 1. Load environment variables
# ------------------------------------------------------------

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# ------------------------------------------------------------
# 2. Validate GitHub token
# ------------------------------------------------------------

if not GITHUB_TOKEN:
    print("ERROR: GITHUB_TOKEN was not found.")
    print("Please check your .env file.")
    raise SystemExit(1)


# ------------------------------------------------------------
# 3. Repository configuration
# ------------------------------------------------------------

OWNER = "PraharshaIncepteolabs"
REPOSITORY = "TEST"


# ------------------------------------------------------------
# 4. GitHub API URL
# ------------------------------------------------------------

API_URL = f"https://api.github.com/repos/{OWNER}/{REPOSITORY}/commits"


# ------------------------------------------------------------
# 5. Request headers
# ------------------------------------------------------------

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2026-03-10"
}


# ------------------------------------------------------------
# 6. Request parameters
# ------------------------------------------------------------

params = {
    "per_page": 10
}


# ------------------------------------------------------------
# 7. Request commits from GitHub
# ------------------------------------------------------------

print()
print("=" * 70)
print("GitHub Usage & Access Reporting System")
print("=" * 70)

print()
print(f"Repository: {OWNER}/{REPOSITORY}")
print("Connecting to GitHub...")


try:

    response = requests.get(
        API_URL,
        headers=headers,
        params=params,
        timeout=30
    )

except requests.RequestException as error:

    print()
    print("ERROR: Could not connect to GitHub.")
    print(error)

    raise SystemExit(1)


# ------------------------------------------------------------
# 8. Check API response
# ------------------------------------------------------------

print()
print("HTTP Status:", response.status_code)


if response.status_code != 200:

    print()
    print("GitHub API request failed.")

    try:
        print("GitHub response:")
        print(response.json())

    except ValueError:
        print(response.text)

    raise SystemExit(1)


# ------------------------------------------------------------
# 9. Convert response to Python data
# ------------------------------------------------------------

commits = response.json()


# ------------------------------------------------------------
# 10. Validate response
# ------------------------------------------------------------

if not isinstance(commits, list):

    print()
    print("Unexpected response received from GitHub.")
    print(commits)

    raise SystemExit(1)


# ------------------------------------------------------------
# 11. Display summary
# ------------------------------------------------------------

print()
print("=" * 70)
print("COMMIT SUMMARY")
print("=" * 70)

print()
print(f"Total commits retrieved: {len(commits)}")


# ------------------------------------------------------------
# 12. Display individual commits
# ------------------------------------------------------------

for index, commit in enumerate(commits, start=1):

    sha = commit.get("sha", "Unknown")

    commit_data = commit.get("commit", {})

    message = commit_data.get(
        "message",
        "No commit message"
    )

    author_data = commit_data.get("author") or {}

    author_name = author_data.get(
        "name",
        "Unknown"
    )

    author_email = author_data.get(
        "email",
        "Unknown"
    )

    author_date = author_data.get(
        "date",
        "Unknown"
    )

    print()
    print("-" * 70)
    print(f"COMMIT #{index}")
    print("-" * 70)

    print("SHA         :", sha)
    print("Author      :", author_name)
    print("Email       :", author_email)
    print("Date        :", author_date)
    print("Message     :", message)


print()
print("=" * 70)
print("Commit retrieval completed successfully.")
print("=" * 70)