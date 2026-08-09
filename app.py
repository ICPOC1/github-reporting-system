import json
import os

import requests
from dotenv import load_dotenv


# ============================================================
# GitHub Usage & Access Reporting System
# Step 5 - Historical Commit Tracking
# ============================================================


# ------------------------------------------------------------
# 1. Load environment variables
# ------------------------------------------------------------

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


if not GITHUB_TOKEN:
    print("ERROR: GITHUB_TOKEN was not found.")
    raise SystemExit(1)


# ------------------------------------------------------------
# 2. Repository configuration
# ------------------------------------------------------------

OWNER = "PraharshaIncepteolabs"
REPOSITORY = "TEST"


# ------------------------------------------------------------
# 3. File storage configuration
# ------------------------------------------------------------

DATA_FOLDER = "data"
HISTORY_FILE = os.path.join(
    DATA_FOLDER,
    "commits.json"
)


# ------------------------------------------------------------
# 4. GitHub API configuration
# ------------------------------------------------------------

BASE_URL = (
    f"https://api.github.com/repos/"
    f"{OWNER}/{REPOSITORY}"
)

COMMITS_URL = f"{BASE_URL}/commits"


headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2026-03-10"
}


# ------------------------------------------------------------
# 5. Create data folder if required
# ------------------------------------------------------------

os.makedirs(
    DATA_FOLDER,
    exist_ok=True
)


# ------------------------------------------------------------
# 6. Load historical commits
# ------------------------------------------------------------

def load_history():

    if not os.path.exists(HISTORY_FILE):

        return {
            "commits": []
        }


    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)


        if not isinstance(data, dict):
            return {"commits": []}


        if "commits" not in data:
            data["commits"] = []


        return data


    except (
        json.JSONDecodeError,
        OSError
    ):

        print(
            "WARNING: Could not read history file."
        )

        return {
            "commits": []
        }


# ------------------------------------------------------------
# 7. Save historical commits
# ------------------------------------------------------------

def save_history(data):

    try:

        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )


        return True


    except OSError as error:

        print(
            "ERROR: Could not save history."
        )

        print(error)

        return False


# ------------------------------------------------------------
# 8. Retrieve commits from GitHub
# ------------------------------------------------------------

def get_commits():

    try:

        response = requests.get(
            COMMITS_URL,
            headers=headers,
            params={
                "per_page": 100
            },
            timeout=30
        )


    except requests.RequestException as error:

        print(
            "ERROR: Could not connect to GitHub."
        )

        print(error)

        return []


    if response.status_code != 200:

        print(
            "GitHub API error:",
            response.status_code
        )


        try:

            print(
                response.json()
            )

        except ValueError:

            print(
                response.text
            )


        return []


    return response.json()


# ------------------------------------------------------------
# 9. Retrieve detailed commit information
# ------------------------------------------------------------

def get_commit_details(commit_sha):

    url = f"{COMMITS_URL}/{commit_sha}"


    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )


    except requests.RequestException as error:

        print(
            f"ERROR retrieving commit {commit_sha}"
        )

        print(error)

        return None


    if response.status_code != 200:

        print(
            f"GitHub API error for "
            f"{commit_sha}: "
            f"{response.status_code}"
        )

        return None


    return response.json()


# ------------------------------------------------------------
# 10. Convert GitHub commit into our report format
# ------------------------------------------------------------

def build_commit_record(commit):

    sha = commit.get(
        "sha",
        "Unknown"
    )


    details = get_commit_details(
        sha
    )


    if not details:

        return None


    commit_data = details.get(
        "commit",
        {}
    )


    author_data = (
        commit_data.get("author")
        or {}
    )


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


    message = commit_data.get(
        "message",
        "No message"
    )


    stats = details.get(
        "stats",
        {}
    )


    additions = stats.get(
        "additions",
        0
    )


    deletions = stats.get(
        "deletions",
        0
    )


    total_changes = stats.get(
        "total",
        0
    )


    files = []


    for file_data in details.get(
        "files",
        []
    ):

        files.append(
            {
                "filename": file_data.get(
                    "filename",
                    "Unknown"
                ),

                "status": file_data.get(
                    "status",
                    "Unknown"
                ),

                "additions": file_data.get(
                    "additions",
                    0
                ),

                "deletions": file_data.get(
                    "deletions",
                    0
                ),

                "changes": file_data.get(
                    "changes",
                    0
                )
            }
        )


    return {
        "sha": sha,

        "author": {
            "name": author_name,
            "email": author_email
        },

        "date": author_date,

        "message": message,

        "statistics": {
            "additions": additions,
            "deletions": deletions,
            "total_changes": total_changes
        },

        "files": files
    }


# ------------------------------------------------------------
# 11. Main program
# ------------------------------------------------------------

print()
print("=" * 80)
print("GITHUB USAGE & ACCESS REPORTING SYSTEM")
print("=" * 80)


print()
print(
    f"Repository: "
    f"{OWNER}/{REPOSITORY}"
)


print(
    "Checking GitHub for commits..."
)


# Load local history

history = load_history()

stored_commits = history.get(
    "commits",
    []
)


# Create a set of existing SHA values

existing_shas = {
    commit.get("sha")
    for commit in stored_commits
}


print()
print(
    f"Previously stored commits: "
    f"{len(stored_commits)}"
)


# Get current GitHub commits

github_commits = get_commits()


if not github_commits:

    print(
        "No commits retrieved from GitHub."
    )

    raise SystemExit(1)


print(
    f"Commits received from GitHub: "
    f"{len(github_commits)}"
)


# ------------------------------------------------------------
# 12. Detect new commits
# ------------------------------------------------------------

new_commits = []


for commit in github_commits:

    sha = commit.get(
        "sha"
    )


    if sha in existing_shas:

        continue


    print()
    print(
        f"New commit detected: {sha}"
    )


    detailed_record = build_commit_record(
        commit
    )


    if detailed_record:

        new_commits.append(
            detailed_record
        )


# ------------------------------------------------------------
# 13. Save new commits
# ------------------------------------------------------------

if new_commits:

    stored_commits.extend(
        new_commits
    )


    history["commits"] = stored_commits


    if save_history(history):

        print()
        print(
            f"New commits saved: "
            f"{len(new_commits)}"
        )


else:

    print()
    print(
        "No new commits detected."
    )


# ------------------------------------------------------------
# 14. Display historical report
# ------------------------------------------------------------

print()
print("=" * 80)
print("HISTORICAL COMMIT REPORT")
print("=" * 80)


print()
print(
    f"Total tracked commits: "
    f"{len(stored_commits)}"
)


for index, commit in enumerate(
    stored_commits,
    start=1
):

    print()
    print("-" * 80)

    print(
        f"COMMIT #{index}"
    )

    print("-" * 80)


    print(
        "SHA      :",
        commit.get("sha")
    )


    author = commit.get(
        "author",
        {}
    )


    print(
        "Author   :",
        author.get(
            "name",
            "Unknown"
        )
    )


    print(
        "Email    :",
        author.get(
            "email",
            "Unknown"
        )
    )


    print(
        "Date     :",
        commit.get(
            "date",
            "Unknown"
        )
    )


    print(
        "Message  :",
        commit.get(
            "message",
            "Unknown"
        )
    )


    statistics = commit.get(
        "statistics",
        {}
    )


    print()
    print(
        "Additions:",
        statistics.get(
            "additions",
            0
        )
    )


    print(
        "Deletions:",
        statistics.get(
            "deletions",
            0
        )
    )


    print(
        "Changes  :",
        statistics.get(
            "total_changes",
            0
        )
    )


    print()
    print(
        "Files:"
    )


    for file_data in commit.get(
        "files",
        []
    ):

        print(
            f"  - "
            f"{file_data.get('filename')} "
            f"[{file_data.get('status')}] "
            f"+{file_data.get('additions')} "
            f"-{file_data.get('deletions')}"
        )


print()
print("=" * 80)
print(
    "REPORT GENERATION COMPLETED"
)
print("=" * 80)