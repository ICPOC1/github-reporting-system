import json
import os
import shutil
from pathlib import Path

import requests
from dotenv import load_dotenv

from user_report import (
    generate_user_report,
    display_user_report,
    display_detailed_user_report,
)

# ============================================================
# GitHub Usage & Access Reporting System
# Multi-Repository Backend Synchronization
#
# Existing functionality is preserved:
# - commits + historical commit storage
# - pull requests
# - issues
# - branches
# - repository information
# - contributors
# - collaborators + permissions
# - user-wise console reports
# - synchronization from the dashboard
#
# New:
# - automatically discovers repositories accessible to the token
# - synchronizes every discovered repository
# - stores each repository in data/repositories/<repo>/
# - creates data/repository_index.json
# - keeps the configured repository mirrored in data/*.json for
#   backward compatibility with the previous single-repository app
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_FOLDER = BASE_DIR / "data"
REPOSITORIES_FOLDER = DATA_FOLDER / "repositories"
REPOSITORY_INDEX_FILE = DATA_FOLDER / "repository_index.json"

load_dotenv(BASE_DIR / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

OWNER = os.getenv(
    "GITHUB_REPO_OWNER",
    os.getenv("GITHUB_OWNER", "PraharshaIncepteolabs"),
)

DEFAULT_REPOSITORY = os.getenv(
    "GITHUB_REPO_NAME",
    os.getenv("GITHUB_REPOSITORY", "TEST"),
)

if not GITHUB_TOKEN:
    print("=" * 80)
    print("ERROR: GITHUB_TOKEN was not found.")
    print("=" * 80)
    print("Please check your .env file.")
    raise SystemExit(1)

DATA_FOLDER.mkdir(parents=True, exist_ok=True)
REPOSITORIES_FOLDER.mkdir(parents=True, exist_ok=True)

API_ROOT = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}

# Root-level files retained for compatibility with the original project.
ROOT_FILES = {
    "commits": DATA_FOLDER / "commits.json",
    "pull_requests": DATA_FOLDER / "pull_requests.json",
    "issues": DATA_FOLDER / "issues.json",
    "branches": DATA_FOLDER / "branches.json",
    "repository": DATA_FOLDER / "repository.json",
    "contributors": DATA_FOLDER / "contributors.json",
    "collaborators": DATA_FOLDER / "collaborators.json",
}


def safe_repository_folder(repository_name):
    """Create a safe local folder name for a repository."""
    safe = "".join(
        char if char.isalnum() or char in "._-" else "_"
        for char in repository_name
    )
    return safe or "repository"


def repository_folder(repository_name):
    return REPOSITORIES_FOLDER / safe_repository_folder(repository_name)


def repository_files(repository_name):
    folder = repository_folder(repository_name)
    folder.mkdir(parents=True, exist_ok=True)
    return {
        "commits": folder / "commits.json",
        "pull_requests": folder / "pull_requests.json",
        "issues": folder / "issues.json",
        "branches": folder / "branches.json",
        "repository": folder / "repository.json",
        "contributors": folder / "contributors.json",
        "collaborators": folder / "collaborators.json",
    }


def load_json_file(file_path, default):
    if not file_path.exists():
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        print(f"WARNING: Could not read {file_path}")
        return default


def save_json_file(file_path, data):
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except OSError as error:
        print(f"ERROR: Could not save {file_path}")
        print(error)
        return False


def github_get(url, params=None, timeout=30, quiet=False):
    """Perform a GitHub GET request and return JSON."""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=timeout,
        )
    except requests.RequestException as error:
        if not quiet:
            print("ERROR: Could not connect to GitHub.")
            print(error)
        return None

    if response.status_code != 200:
        if not quiet:
            print(f"GitHub API error: {response.status_code}")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text)
        return None

    try:
        return response.json()
    except ValueError:
        if not quiet:
            print("ERROR: GitHub returned invalid JSON.")
        return None


def github_get_all(url, params=None, max_pages=100, quiet=False):
    """Retrieve all pages from a list endpoint."""
    params = (params or {}).copy()
    params.setdefault("per_page", 100)

    all_items = []

    for page in range(1, max_pages + 1):
        params["page"] = page
        data = github_get(url, params=params, quiet=quiet)

        if data is None or not isinstance(data, list) or not data:
            break

        all_items.extend(data)

        if len(data) < params["per_page"]:
            break

    return all_items


def discover_repositories():
    """
    Discover repositories visible to the current token.

    /user/repos is intentionally used instead of hard-coding repository
    names. A fine-grained PAT must have access to a repository for it to
    appear here and for its data to be synchronized.
    """
    print("=" * 80)
    print("REPOSITORY DISCOVERY")
    print("=" * 80)

    repos = github_get_all(
        f"{API_ROOT}/user/repos",
        params={
            "visibility": "all",
            "affiliation": "owner,collaborator,organization_member",
            "sort": "updated",
            "direction": "desc",
        },
    )

    discovered = []

    if repos:
        for repo in repos:
            owner_data = repo.get("owner") or {}
            repo_owner = owner_data.get("login", "")

            if repo_owner.lower() != OWNER.lower():
                continue

            discovered.append(
                {
                    "id": repo.get("id"),
                    "name": repo.get("name"),
                    "full_name": repo.get(
                        "full_name",
                        f"{OWNER}/{repo.get('name', '')}",
                    ),
                    "owner": repo_owner,
                    "private": repo.get("private", False),
                    "visibility": repo.get("visibility", "unknown"),
                    "default_branch": repo.get("default_branch", "main"),
                    "html_url": repo.get("html_url", ""),
                    "description": repo.get("description"),
                    "updated_at": repo.get("updated_at"),
                    "pushed_at": repo.get("pushed_at"),
                }
            )

    # Always retain the configured repository as a fallback. This is useful
    # when the token can access a repository but /user/repos is restricted.
    if not any(
        item.get("name", "").lower() == DEFAULT_REPOSITORY.lower()
        for item in discovered
    ):
        fallback = github_get(
            f"{API_ROOT}/repos/{OWNER}/{DEFAULT_REPOSITORY}",
            quiet=True,
        )
        if fallback:
            discovered.append(
                {
                    "id": fallback.get("id"),
                    "name": fallback.get("name", DEFAULT_REPOSITORY),
                    "full_name": fallback.get(
                        "full_name",
                        f"{OWNER}/{DEFAULT_REPOSITORY}",
                    ),
                    "owner": (fallback.get("owner") or {}).get(
                        "login",
                        OWNER,
                    ),
                    "private": fallback.get("private", False),
                    "visibility": fallback.get("visibility", "unknown"),
                    "default_branch": fallback.get(
                        "default_branch",
                        "main",
                    ),
                    "html_url": fallback.get("html_url", ""),
                    "description": fallback.get("description"),
                    "updated_at": fallback.get("updated_at"),
                    "pushed_at": fallback.get("pushed_at"),
                }
            )

    # Remove duplicates and sort by repository name.
    unique = {}
    for repo in discovered:
        name = repo.get("name")
        if name:
            unique[name.lower()] = repo

    discovered = sorted(
        unique.values(),
        key=lambda item: item.get("name", "").lower(),
    )

    save_json_file(
        REPOSITORY_INDEX_FILE,
        {
            "owner": OWNER,
            "total": len(discovered),
            "repositories": discovered,
        },
    )

    print(f"Repositories discovered: {len(discovered)}")

    for repo in discovered:
        print(f"  - {repo.get('full_name', repo.get('name'))}")

    return discovered


def get_commit_details(repository_name, commit_sha):
    url = (
        f"{API_ROOT}/repos/{OWNER}/{repository_name}"
        f"/commits/{commit_sha}"
    )
    return github_get(url, quiet=True)


def load_commit_history(repository_name):
    files = repository_files(repository_name)

    data = load_json_file(
        files["commits"],
        {"commits": []},
    )

    if not isinstance(data, dict):
        data = {"commits": []}

    if not isinstance(data.get("commits"), list):
        data["commits"] = []

    return data


def build_commit_record(repository_name, commit):
    sha = commit.get("sha", "Unknown")
    details = get_commit_details(repository_name, sha)

    if not details:
        return None

    commit_data = details.get("commit") or {}
    author_data = commit_data.get("author") or {}
    stats = details.get("stats") or {}

    additions = int(stats.get("additions", 0) or 0)
    deletions = int(stats.get("deletions", 0) or 0)

    files = []
    for file_data in details.get("files", []) or []:
        files.append(
            {
                "filename": file_data.get("filename", "Unknown"),
                "status": file_data.get("status", "Unknown"),
                "additions": int(file_data.get("additions", 0) or 0),
                "deletions": int(file_data.get("deletions", 0) or 0),
                "changes": int(file_data.get("changes", 0) or 0),
            }
        )

    return {
        "sha": sha,
        "author": {
            "name": author_data.get("name", "Unknown"),
            "email": author_data.get("email", "Unknown"),
        },
        "date": author_data.get("date", "Unknown"),
        "message": commit_data.get(
            "message",
            "No commit message",
        ),
        "statistics": {
            "additions": additions,
            "deletions": deletions,
            "total_changes": int(
                stats.get(
                    "total",
                    additions + deletions,
                )
                or 0
            ),
        },
        "files": files,
    }


def sync_commits(repository_name):
    print("\n" + "=" * 80)
    print(f"COMMIT SYNCHRONIZATION: {repository_name}")
    print("=" * 80)

    history = load_commit_history(repository_name)
    stored_commits = history.get("commits", [])

    existing_shas = {
        commit.get("sha")
        for commit in stored_commits
        if commit.get("sha")
    }

    url = f"{API_ROOT}/repos/{OWNER}/{repository_name}/commits"
    github_commits = github_get_all(url)

    if github_commits is None:
        print("Unable to retrieve commits.")
        return stored_commits

    print(f"Previously stored commits: {len(stored_commits)}")
    print(f"Commits received from GitHub: {len(github_commits)}")

    new_commits = []

    for commit in github_commits:
        sha = commit.get("sha")
        if not sha or sha in existing_shas:
            continue

        detailed_record = build_commit_record(
            repository_name,
            commit,
        )

        if detailed_record:
            new_commits.append(detailed_record)

    if new_commits:
        stored_commits.extend(new_commits)
        history["commits"] = stored_commits
        save_json_file(
            repository_files(repository_name)["commits"],
            history,
        )
        print(f"New commits saved: {len(new_commits)}")
    else:
        print("No new commits detected.")

    return stored_commits


def sync_pull_requests(repository_name):
    print("\n" + "=" * 80)
    print(f"PULL REQUEST SYNCHRONIZATION: {repository_name}")
    print("=" * 80)

    url = f"{API_ROOT}/repos/{OWNER}/{repository_name}/pulls"

    pull_requests = github_get_all(
        url,
        params={
            "state": "all",
            "sort": "updated",
            "direction": "desc",
        },
    )

    if pull_requests is None:
        return []

    formatted = []

    for pr in pull_requests:
        user = pr.get("user") or {}
        head = pr.get("head") or {}
        base = pr.get("base") or {}

        formatted.append(
            {
                "number": pr.get("number"),
                "title": pr.get("title", "No title"),
                "state": pr.get("state", "unknown"),
                "draft": bool(pr.get("draft", False)),
                "merged": pr.get("merged_at") is not None,
                "author": user.get("login", "Unknown"),
                "author_url": user.get("html_url", ""),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "closed_at": pr.get("closed_at"),
                "merged_at": pr.get("merged_at"),
                "url": pr.get("html_url", ""),
                "head_branch": head.get("ref", ""),
                "base_branch": base.get("ref", ""),
            }
        )

    save_json_file(
        repository_files(repository_name)["pull_requests"],
        {
            "repository": f"{OWNER}/{repository_name}",
            "total": len(formatted),
            "pull_requests": formatted,
        },
    )

    print(f"Pull requests synchronized: {len(formatted)}")
    return formatted


def sync_issues(repository_name):
    print("\n" + "=" * 80)
    print(f"ISSUE SYNCHRONIZATION: {repository_name}")
    print("=" * 80)

    url = f"{API_ROOT}/repos/{OWNER}/{repository_name}/issues"

    issues = github_get_all(
        url,
        params={
            "state": "all",
            "sort": "updated",
            "direction": "desc",
        },
    )

    if issues is None:
        return []

    formatted = []

    for issue in issues:
        # /issues also returns pull requests.
        if "pull_request" in issue:
            continue

        user = issue.get("user") or {}

        labels = [
            label.get("name", "")
            for label in issue.get("labels", []) or []
        ]

        formatted.append(
            {
                "number": issue.get("number"),
                "title": issue.get("title", "No title"),
                "state": issue.get("state", "unknown"),
                "author": user.get("login", "Unknown"),
                "author_url": user.get("html_url", ""),
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
                "closed_at": issue.get("closed_at"),
                "comments": int(issue.get("comments", 0) or 0),
                "labels": labels,
                "url": issue.get("html_url", ""),
            }
        )

    save_json_file(
        repository_files(repository_name)["issues"],
        {
            "repository": f"{OWNER}/{repository_name}",
            "total": len(formatted),
            "issues": formatted,
        },
    )

    print(f"Issues synchronized: {len(formatted)}")
    return formatted


def sync_branches(repository_name, repository_info):
    print("\n" + "=" * 80)
    print(f"BRANCH SYNCHRONIZATION: {repository_name}")
    print("=" * 80)

    url = f"{API_ROOT}/repos/{OWNER}/{repository_name}/branches"
    branches = github_get_all(url)

    if branches is None:
        return []

    default_branch = (
        repository_info.get("default_branch", "")
        if repository_info
        else ""
    )

    formatted = []

    for branch in branches:
        branch_name = branch.get("name", "Unknown")
        commit_data = branch.get("commit") or {}

        formatted.append(
            {
                "name": branch_name,
                "default": branch_name == default_branch,
                "protected": bool(branch.get("protected", False)),
                "commit_sha": commit_data.get("sha", ""),
            }
        )

    save_json_file(
        repository_files(repository_name)["branches"],
        {
            "repository": f"{OWNER}/{repository_name}",
            "default_branch": default_branch,
            "total": len(formatted),
            "branches": formatted,
        },
    )

    print(f"Branches synchronized: {len(formatted)}")
    return formatted


def sync_repository_info(repository_name):
    url = f"{API_ROOT}/repos/{OWNER}/{repository_name}"
    repository_info = github_get(url)

    if repository_info is None:
        return None

    formatted = {
        "id": repository_info.get("id"),
        "name": repository_info.get("name", repository_name),
        "full_name": repository_info.get(
            "full_name",
            f"{OWNER}/{repository_name}",
        ),
        "description": repository_info.get("description"),
        "private": repository_info.get("private", False),
        "visibility": repository_info.get("visibility", "unknown"),
        "default_branch": repository_info.get(
            "default_branch",
            "main",
        ),
        "html_url": repository_info.get("html_url", ""),
        "clone_url": repository_info.get("clone_url", ""),
        "ssh_url": repository_info.get("ssh_url", ""),
        "language": repository_info.get("language"),
        "created_at": repository_info.get("created_at"),
        "updated_at": repository_info.get("updated_at"),
        "pushed_at": repository_info.get("pushed_at"),
        "size": repository_info.get("size", 0),
        "stars": repository_info.get("stargazers_count", 0),
        "forks": repository_info.get("forks_count", 0),
        "open_issues": repository_info.get(
            "open_issues_count",
            0,
        ),
        "watchers": repository_info.get(
            "watchers_count",
            0,
        ),
        "archived": repository_info.get("archived", False),
        "disabled": repository_info.get("disabled", False),
    }

    save_json_file(
        repository_files(repository_name)["repository"],
        formatted,
    )

    return formatted


def sync_contributors(repository_name):
    url = f"{API_ROOT}/repos/{OWNER}/{repository_name}/contributors"
    contributors = github_get_all(url)

    if contributors is None:
        return []

    formatted = []

    for contributor in contributors:
        formatted.append(
            {
                "login": contributor.get("login", "Unknown"),
                "id": contributor.get("id"),
                "contributions": int(
                    contributor.get("contributions", 0) or 0
                ),
                "type": contributor.get("type", "User"),
                "profile_url": contributor.get("html_url", ""),
                "avatar_url": contributor.get("avatar_url", ""),
            }
        )

    save_json_file(
        repository_files(repository_name)["contributors"],
        {
            "repository": f"{OWNER}/{repository_name}",
            "total": len(formatted),
            "contributors": formatted,
        },
    )

    print(f"Contributors synchronized: {len(formatted)}")
    return formatted


def sync_collaborators(repository_name):
    print("\n" + "=" * 80)
    print(f"COLLABORATOR / ACCESS SYNCHRONIZATION: {repository_name}")
    print("=" * 80)

    url = f"{API_ROOT}/repos/{OWNER}/{repository_name}/collaborators"

    collaborators = github_get_all(
        url,
        params={"affiliation": "all"},
    )

    if collaborators is None:
        print(
            "Collaborators could not be retrieved. "
            "The token may not have permission to read collaborator data."
        )
        return []

    formatted = []

    for collaborator in collaborators:
        permissions = collaborator.get("permissions") or {}

        formatted.append(
            {
                "login": collaborator.get("login", "Unknown"),
                "id": collaborator.get("id"),
                "type": collaborator.get("type", "User"),
                "role_name": collaborator.get(
                    "role_name",
                    "Unknown",
                ),
                "admin": bool(permissions.get("admin", False)),
                "maintain": bool(permissions.get("maintain", False)),
                "push": bool(permissions.get("push", False)),
                "triage": bool(permissions.get("triage", False)),
                "pull": bool(permissions.get("pull", False)),
                "profile_url": collaborator.get("html_url", ""),
            }
        )

    save_json_file(
        repository_files(repository_name)["collaborators"],
        {
            "repository": f"{OWNER}/{repository_name}",
            "total": len(formatted),
            "collaborators": formatted,
        },
    )

    print(f"Collaborators synchronized: {len(formatted)}")
    return formatted


def sync_one_repository(repository_name):
    """Synchronize every existing feature for one repository."""
    print("\n" + "=" * 80)
    print(f"SYNCHRONIZING REPOSITORY: {OWNER}/{repository_name}")
    print("=" * 80)

    repository_info = sync_repository_info(repository_name)

    if not repository_info:
        return None

    commits = sync_commits(repository_name)
    pull_requests = sync_pull_requests(repository_name)
    issues = sync_issues(repository_name)
    branches = sync_branches(
        repository_name,
        repository_info,
    )
    contributors = sync_contributors(repository_name)
    collaborators = sync_collaborators(repository_name)

    return {
        "repository": repository_info,
        "commits": commits,
        "pull_requests": pull_requests,
        "issues": issues,
        "branches": branches,
        "contributors": contributors,
        "collaborators": collaborators,
    }


def mirror_default_repository(repository_name):
    """
    Keep the original data/*.json layout working for existing code.
    """
    if repository_name.lower() != DEFAULT_REPOSITORY.lower():
        return

    files = repository_files(repository_name)

    for key, root_file in ROOT_FILES.items():
        source = files[key]
        if source.exists():
            try:
                shutil.copy2(source, root_file)
            except OSError as error:
                print(f"WARNING: Could not mirror {source}: {error}")


def display_commit_report(repository_name, commits):
    print("\n" + "=" * 80)
    print(f"HISTORICAL COMMIT REPORT: {repository_name}")
    print("=" * 80)
    print(f"Total tracked commits: {len(commits)}")

    for index, commit in enumerate(commits, start=1):
        author = commit.get("author") or {}
        stats = commit.get("statistics") or {}

        print("\n" + "-" * 80)
        print(f"COMMIT #{index}")
        print("-" * 80)
        print("SHA      :", commit.get("sha", "Unknown"))
        print("Author   :", author.get("name", "Unknown"))
        print("Email    :", author.get("email", "Unknown"))
        print("Date     :", commit.get("date", "Unknown"))
        print("Message  :", commit.get("message", "Unknown"))
        print("Additions:", stats.get("additions", 0))
        print("Deletions:", stats.get("deletions", 0))
        print("Changes  :", stats.get("total_changes", 0))

        print("Files:")
        for file_data in commit.get("files", []):
            print(
                f"  - {file_data.get('filename', 'Unknown')} "
                f"[{file_data.get('status', 'Unknown')}] "
                f"+{file_data.get('additions', 0)} "
                f"-{file_data.get('deletions', 0)}"
            )


def display_repository_summary(repository_name, result):
    print("\n" + "=" * 80)
    print(f"REPOSITORY SUMMARY: {repository_name}")
    print("=" * 80)
    print(f"Commits          : {len(result['commits'])}")
    print(f"Pull Requests    : {len(result['pull_requests'])}")
    print(f"Issues           : {len(result['issues'])}")
    print(f"Branches         : {len(result['branches'])}")
    print(f"Contributors     : {len(result['contributors'])}")
    print(f"Collaborators    : {len(result['collaborators'])}")


def main():
    print("\n" + "=" * 80)
    print("GITHUB USAGE & ACCESS REPORTING SYSTEM")
    print("MULTI-REPOSITORY SYNCHRONIZATION")
    print("=" * 80)
    print(f"Configured owner      : {OWNER}")
    print(f"Default repository    : {DEFAULT_REPOSITORY}")

    repositories = discover_repositories()

    if not repositories:
        print("\nNo accessible repositories were discovered.")
        print(
            "Check GITHUB_TOKEN permissions and the repository owner/name "
            "in .env."
        )
        return

    all_results = {}

    for repo in repositories:
        repository_name = repo.get("name")
        if not repository_name:
            continue

        result = sync_one_repository(repository_name)

        if result is None:
            continue

        all_results[repository_name] = result
        mirror_default_repository(repository_name)

        display_commit_report(
            repository_name,
            result["commits"],
        )

        display_repository_summary(
            repository_name,
            result,
        )

        # Preserve the existing user-wise report functionality.
        try:
            users = generate_user_report(result["commits"])
            display_user_report(users)
            display_detailed_user_report(users)
        except Exception as error:
            print(
                f"WARNING: User-wise report could not be generated for "
                f"{repository_name}: {error}"
            )

    # Update repository index with synchronization counts so the dashboard
    # can build repository-wise activity without making extra API calls.
    index = load_json_file(
        REPOSITORY_INDEX_FILE,
        {
            "owner": OWNER,
            "repositories": [],
        },
    )

    index_repositories = []

    for repo in repositories:
        name = repo.get("name")
        result = all_results.get(name)

        if not result:
            continue

        info = result["repository"]

        index_repositories.append(
            {
                "id": info.get("id"),
                "name": info.get("name", name),
                "full_name": info.get(
                    "full_name",
                    f"{OWNER}/{name}",
                ),
                "owner": OWNER,
                "private": info.get("private", False),
                "visibility": info.get("visibility", "unknown"),
                "default_branch": info.get(
                    "default_branch",
                    "main",
                ),
                "html_url": info.get("html_url", ""),
                "description": info.get("description"),
                "updated_at": info.get("updated_at"),
                "pushed_at": info.get("pushed_at"),
                "commits": len(result["commits"]),
                "pull_requests": len(result["pull_requests"]),
                "issues": len(result["issues"]),
                "branches": len(result["branches"]),
                "contributors": len(result["contributors"]),
                "collaborators": len(result["collaborators"]),
            }
        )

    index["owner"] = OWNER
    index["total"] = len(index_repositories)
    index["repositories"] = sorted(
        index_repositories,
        key=lambda item: item.get("name", "").lower(),
    )
    save_json_file(REPOSITORY_INDEX_FILE, index)

    print("\n" + "=" * 80)
    print("MULTI-REPOSITORY SYNCHRONIZATION SUMMARY")
    print("=" * 80)

    for repo in index["repositories"]:
        print(
            f"{repo['name']}: "
            f"{repo['commits']} commits | "
            f"{repo['pull_requests']} PRs | "
            f"{repo['issues']} issues | "
            f"{repo['branches']} branches | "
            f"{repo['contributors']} contributors | "
            f"{repo['collaborators']} collaborators"
        )

    print("\n" + "=" * 80)
    print("GITHUB DATA SYNCHRONIZATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()