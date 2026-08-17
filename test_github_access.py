import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
ORGANIZATION = "ICPOC1"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2026-03-10"
}

print("=" * 70)
print("GITHUB ACCESS TEST")
print("=" * 70)

# ------------------------------------------------------------
# 1. Check token
# ------------------------------------------------------------

if not TOKEN:
    print("\nERROR: GITHUB_TOKEN is not loaded from .env")
    raise SystemExit(1)

print("\nGITHUB_TOKEN loaded: YES")


# ------------------------------------------------------------
# 2. Check authenticated GitHub user
# ------------------------------------------------------------

print("\nChecking authenticated GitHub user...")

response = requests.get(
    "https://api.github.com/user",
    headers=HEADERS,
    timeout=30
)

print("HTTP Status:", response.status_code)

if response.status_code != 200:
    print(response.text)
    raise SystemExit(1)

user_data = response.json()

print("Authenticated user:", user_data.get("login"))


# ------------------------------------------------------------
# 3. Check organization
# ------------------------------------------------------------

print("\nChecking organization:", ORGANIZATION)

response = requests.get(
    f"https://api.github.com/orgs/{ORGANIZATION}",
    headers=HEADERS,
    timeout=30
)

print("HTTP Status:", response.status_code)

if response.status_code != 200:
    print(response.text)
    raise SystemExit(1)

organization_data = response.json()

print("Organization name:", organization_data.get("login"))
print("Organization ID:", organization_data.get("id"))


print("\n" + "=" * 70)
print("GITHUB ACCESS TEST PASSED")
print("=" * 70)