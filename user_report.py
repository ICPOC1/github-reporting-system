import json
import os


# ============================================================
# 1. Configuration
# ============================================================

DATA_FILE = os.path.join("data", "commits.json")


# ============================================================
# 2. Load stored commits
# ============================================================

def load_commits():
    """
    Load all previously stored GitHub commits
    from data/commits.json.
    """

    print()
    print("Loading GitHub commit data...")

    if not os.path.exists(DATA_FILE):
        print("Commit data file not found.")
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        commits = data.get("commits", [])

        print(f"Commits loaded: {len(commits)}")

        return commits

    except json.JSONDecodeError:
        print("Error: commits.json contains invalid JSON.")
        return []

    except Exception as error:
        print(f"Error loading commit data: {error}")
        return []


# ============================================================
# 3. Generate user-wise summary
# ============================================================

def generate_user_report(commits):
    """
    Generate statistics for every GitHub user.

    The report includes:
        - Total commits
        - Total additions
        - Total deletions
        - Total changes
        - Files changed
        - Complete commit history
    """

    users = {}

    for commit in commits:

        author = commit.get("author", {})
        username = author.get("name", "Unknown")
        email = author.get("email", "Unknown")

        statistics = commit.get("statistics", {})

        additions = statistics.get("additions", 0)
        deletions = statistics.get("deletions", 0)
        total_changes = statistics.get(
            "total_changes",
            additions + deletions
        )

        files = commit.get("files", [])

        # ----------------------------------------------------
        # Create user if not already present
        # ----------------------------------------------------

        if username not in users:

            users[username] = {
                "username": username,
                "email": email,
                "total_commits": 0,
                "total_additions": 0,
                "total_deletions": 0,
                "total_changes": 0,
                "files_changed": 0,
                "commits": []
            }

        # ----------------------------------------------------
        # Update user statistics
        # ----------------------------------------------------

        users[username]["total_commits"] += 1

        users[username]["total_additions"] += additions

        users[username]["total_deletions"] += deletions

        users[username]["total_changes"] += total_changes

        users[username]["files_changed"] += len(files)

        # ----------------------------------------------------
        # Store detailed commit information
        # ----------------------------------------------------

        commit_details = {
            "sha": commit.get("sha", "Unknown"),
            "date": commit.get("date", "Unknown"),
            "message": commit.get("message", "No commit message"),
            "additions": additions,
            "deletions": deletions,
            "total_changes": total_changes,
            "files": files
        }

        users[username]["commits"].append(commit_details)

    return users


# ============================================================
# 4. Display user summary
# ============================================================

def display_user_report(users):
    """
    Display summary information for every developer/admin.
    """

    print()
    print("=" * 80)
    print("USER-WISE SUMMARY REPORT")
    print("=" * 80)

    if not users:
        print("No user data available.")
        return

    for username, user in users.items():

        print()
        print(f"## USER: {username}")

        print()
        print(f"Email             : {user['email']}")
        print(f"Total Commits     : {user['total_commits']}")
        print(f"Total Additions   : {user['total_additions']}")
        print(f"Total Deletions   : {user['total_deletions']}")
        print(f"Total Changes     : {user['total_changes']}")
        print(f"Files Changed     : {user['files_changed']}")

        print("-" * 80)


# ============================================================
# 5. Display detailed developer activity
# ============================================================

def display_detailed_user_report(users):
    """
    Display complete commit history for every developer/admin.
    """

    print()
    print("=" * 80)
    print("DEVELOPER-WISE DETAILED ACTIVITY REPORT")
    print("=" * 80)

    if not users:
        print("No developer activity available.")
        return

    for username, user in users.items():

        print()
        print("=" * 80)
        print(f"DEVELOPER: {username}")
        print("=" * 80)

        print()
        print(f"Email             : {user['email']}")
        print(f"Total Commits     : {user['total_commits']}")
        print(f"Total Additions   : {user['total_additions']}")
        print(f"Total Deletions   : {user['total_deletions']}")
        print(f"Total Changes     : {user['total_changes']}")
        print(f"Files Changed     : {user['files_changed']}")

        print()
        print("-" * 80)
        print("COMMIT HISTORY")
        print("-" * 80)

        # ----------------------------------------------------
        # Display every commit made by this user
        # ----------------------------------------------------

        for index, commit in enumerate(
            user["commits"],
            start=1
        ):

            print()
            print(f"COMMIT #{index}")
            print("-" * 80)

            print(f"SHA         : {commit['sha']}")
            print(f"Date        : {commit['date']}")
            print(f"Message     : {commit['message']}")
            print(f"Additions   : {commit['additions']}")
            print(f"Deletions   : {commit['deletions']}")
            print(f"Changes     : {commit['total_changes']}")

            print()
            print("FILES CHANGED")
            print("-" * 80)

            files = commit.get("files", [])

            if not files:
                print("No file information available.")
                continue

            for file in files:

                filename = file.get(
                    "filename",
                    "Unknown"
                )

                status = file.get(
                    "status",
                    "Unknown"
                )

                additions = file.get(
                    "additions",
                    0
                )

                deletions = file.get(
                    "deletions",
                    0
                )

                changes = file.get(
                    "changes",
                    additions + deletions
                )

                print()
                print(f"File       : {filename}")
                print(f"Status     : {status}")
                print(f"Additions  : {additions}")
                print(f"Deletions  : {deletions}")
                print(f"Changes     : {changes}")

            print()
            print("-" * 80)

        print()


# ============================================================
# 6. Main execution
# ============================================================

if __name__ == "__main__":

    commits = load_commits()

    users = generate_user_report(commits)

    display_user_report(users)

    display_detailed_user_report(users)