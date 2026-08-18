import os
import time
from pathlib import Path

import jwt
import requests
from dotenv import load_dotenv


load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")
INSTALLATION_ID = os.getenv("GITHUB_APP_INSTALLATION_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
ORG = os.getenv("GITHUB_ORG", "ICPOC1")

API_VERSION = "2026-03-10"
BASE_URL = "https://api.github.com"


def create_app_jwt():
    if not APP_ID:
        raise RuntimeError("GITHUB_APP_ID is missing from .env")

    if not PRIVATE_KEY_PATH:
        raise RuntimeError(
            "GITHUB_APP_PRIVATE_KEY_PATH is missing from .env"
        )

    key_path = Path(PRIVATE_KEY_PATH)

    if not key_path.is_absolute():
        key_path = Path(__file__).resolve().parent / key_path

    if not key_path.exists():
        raise FileNotFoundError(
            f"Private key not found: {key_path}"
        )

    private_key = key_path.read_text(encoding="utf-8")

    now = int(time.time())

    payload = {
        "iat": now - 60,
        "exp": now + 540,
        "iss": str(APP_ID),
    }

    return jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
    )


def create_installation_token():
    jwt_token = create_app_jwt()

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {jwt_token}",
        "X-GitHub-Api-Version": API_VERSION,
    }

    url = (
        f"{BASE_URL}/app/installations/"
        f"{INSTALLATION_ID}/access_tokens"
    )

    response = requests.post(
        url,
        headers=headers,
        timeout=30,
    )

    print("=" * 80)
    print("GITHUB APP INSTALLATION TOKEN TEST")
    print("=" * 80)

    print("HTTP Status:", response.status_code)

    if response.status_code != 201:
        print(response.text)
        return None

    data = response.json()

    token = data.get("token")

    print("Token generated: YES")
    print("Expires at:", data.get("expires_at"))
    print(
        "Repository selection:",
        data.get("repository_selection"),
    )

    repositories = data.get("repositories", [])

    print(
        "Repositories available:",
        len(repositories),
    )

    for repo in repositories:
        print(
            " -",
            repo.get("full_name"),
        )

    return token


def test_collaborators(token):
    owner = "ICPOC1"
    repo = "TEST"

    url = (
        f"{BASE_URL}/repos/"
        f"{owner}/{repo}/collaborators"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": API_VERSION,
    }

    params = {
        "affiliation": "all",
        "per_page": 100,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    print("\n" + "=" * 80)
    print("COLLABORATORS TEST")
    print("=" * 80)

    print("Repository:", f"{owner}/{repo}")
    print("HTTP Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return False

    collaborators = response.json()

    print(
        "Collaborators:",
        len(collaborators),
    )

    for collaborator in collaborators:
        print(
            " -",
            collaborator.get("login"),
        )

    return True


def test_repositories(token):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": API_VERSION,
    }

    url = f"{BASE_URL}/orgs/{ORG}/repos"

    params = {
        "per_page": 100,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    print("\n" + "=" * 80)
    print("ORGANIZATION REPOSITORY TEST")
    print("=" * 80)

    print("Organization:", ORG)
    print("HTTP Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return False

    repositories = response.json()

    print(
        "Repositories found:",
        len(repositories),
    )

    for repo in repositories:
        print(
            " -",
            repo.get("full_name"),
        )

    return True


def main():

    print("=" * 80)
    print("GITHUB APP AUTHENTICATION TEST")
    print("=" * 80)

    print("Organization:", ORG)
    print(
        "Installation ID:",
        INSTALLATION_ID,
    )

    token = create_installation_token()

    if not token:
        print("\nFAILED: Could not create installation token.")
        return

    repo_success = test_repositories(token)

    collaborator_success = test_collaborators(token)

    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)

    print(
        "Installation authentication:",
        "PASSED",
    )

    print(
        "Repository access:",
        "PASSED" if repo_success else "FAILED",
    )

    print(
        "Collaborator access:",
        "PASSED" if collaborator_success else "FAILED",
    )

    if repo_success and collaborator_success:
        print("\n🎉 GITHUB APP INTEGRATION TEST PASSED")
    else:
        print("\nGITHUB APP TEST NEEDS ATTENTION")


if __name__ == "__main__":
    main()