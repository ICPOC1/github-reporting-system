
import json
import os
import shutil
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DATA_FOLDER = BASE_DIR / "data"
REPOSITORIES_FOLDER = DATA_FOLDER / "repositories"
REPOSITORY_INDEX_FILE = DATA_FOLDER / "repository_index.json"

load_dotenv(BASE_DIR / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_PROJECT_TOKEN = os.getenv("GITHUB_PROJECT_TOKEN")

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

if not GITHUB_PROJECT_TOKEN:
    print("=" * 80)
    print("ERROR: GITHUB_PROJECT_TOKEN was not found.")
    print("=" * 80)
    print("Please check your .env file.")
    raise SystemExit(1)

DATA_FOLDER.mkdir(parents=True, exist_ok=True)
REPOSITORIES_FOLDER.mkdir(parents=True, exist_ok=True)

API_ROOT = "https://api.github.com"

# Repository/activity APIs always use GITHUB_TOKEN.
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2026-03-10",
}

# Organization Projects V2 GraphQL always uses GITHUB_PROJECT_TOKEN.
PROJECT_HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_PROJECT_TOKEN}",
    "X-GitHub-Api-Version": "2026-03-10",
}

# Live repository registry. It is populated by discover_repositories() and
# lets every repository operation use the repository's real owner instead of
# assuming that all repositories belong to ICPOC1.
REPOSITORY_REGISTRY = {}


def repository_owner(repository_name):
    key = str(repository_name or "").strip().lower()
    entry = REPOSITORY_REGISTRY.get(key)
    if isinstance(entry, dict) and entry.get("owner"):
        return entry["owner"]
    return OWNER


def repository_full_name(repository_name):
    key = str(repository_name or "").strip().lower()
    entry = REPOSITORY_REGISTRY.get(key)
    if isinstance(entry, dict) and entry.get("full_name"):
        return entry["full_name"]
    owner = repository_owner(repository_name)
    return f"{owner}/{repository_name}"


def repository_api_path(repository_name):
    return f"{repository_owner(repository_name)}/{repository_name}"


def register_repository(repo):
    name = repo.get("name") if isinstance(repo, dict) else None
    if not name:
        return
    owner = repo.get("owner") or str(repo.get("full_name", "")).split("/", 1)[0]
    full_name = repo.get("full_name") or f"{owner}/{name}"
    REPOSITORY_REGISTRY[str(name).lower()] = {
        **repo,
        "name": name,
        "owner": owner,
        "full_name": full_name,
    }


def normalize_repository_record(repo):
    owner_data = repo.get("owner") or {}
    owner = owner_data.get("login") if isinstance(owner_data, dict) else owner_data
    owner = owner or str(repo.get("full_name", "")).split("/", 1)[0]
    name = repo.get("name")
    return {
        "id": repo.get("id"),
        "name": name,
        "full_name": repo.get("full_name") or f"{owner}/{name}",
        "owner": owner,
        "private": repo.get("private", False),
        "visibility": repo.get("visibility", "unknown"),
        "default_branch": repo.get("default_branch", "main"),
        "html_url": repo.get("html_url", ""),
        "description": repo.get("description"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
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
        "projects": folder / "projects.json",
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
    Discover every repository the authenticated GITHUB_TOKEN can access.

    This deliberately combines /user/repos with the ICPOC1 organization
    endpoint. /user/repos covers repositories owned by the authenticated user,
    collaborator repositories, and repositories available through an
    organization. The organization endpoint provides an additional reliable
    source for ICPOC1 repositories, including future repositories.
    """
    global REPOSITORY_REGISTRY

    print("=" * 80)
    print("REPOSITORY DISCOVERY")
    print("=" * 80)
    print("Repository scope       : All repositories accessible to GITHUB_TOKEN")
    print(f"Projects organization  : {OWNER}")

    discovered = {}

    # 1. Authenticated user's complete accessible repository view.
    user_repos = github_get_all(
        f"{API_ROOT}/user/repos",
        params={
            "visibility": "all",
            "affiliation": "owner,collaborator,organization_member",
            "sort": "updated",
            "direction": "desc",
        },
        quiet=False,
    )

    if user_repos:
        for repo in user_repos:
            record = normalize_repository_record(repo)
            if record.get("name") and record.get("owner"):
                discovered[record["full_name"].lower()] = record

    # 2. Explicit organization enumeration. This catches ICPOC1 repositories
    # even when the authenticated user's /user/repos view is restricted.
    org_repos = github_get_all(
        f"{API_ROOT}/orgs/{OWNER}/repos",
        params={
            "type": "all",
            "sort": "updated",
            "direction": "desc",
        },
        quiet=False,
    )

    if org_repos:
        for repo in org_repos:
            record = normalize_repository_record(repo)
            if record.get("name") and record.get("owner"):
                discovered[record["full_name"].lower()] = record

    # 3. Last-resort explicit repository lookup for the legacy TEST setting.
    if not any(
        str(item.get("name", "")).lower() == DEFAULT_REPOSITORY.lower()
        for item in discovered.values()
    ):
        fallback_owner = os.getenv("GITHUB_REPO_OWNER", OWNER)
        fallback = github_get(
            f"{API_ROOT}/repos/{fallback_owner}/{DEFAULT_REPOSITORY}",
            quiet=True,
        )
        if fallback:
            record = normalize_repository_record(fallback)
            discovered[record["full_name"].lower()] = record

    repositories = sorted(
        discovered.values(),
        key=lambda item: (
            str(item.get("owner", "")).lower(),
            str(item.get("name", "")).lower(),
        ),
    )

    REPOSITORY_REGISTRY = {}
    for repo in repositories:
        register_repository(repo)

    save_json_file(
        REPOSITORY_INDEX_FILE,
        {
            "repository_scope": "all_accessible",
            "project_owner": OWNER,
            "total": len(repositories),
            "repositories": repositories,
        },
    )

    print(f"Repositories discovered: {len(repositories)}")
    for repo in repositories:
        print(f"  - {repo.get('full_name')}")

    if not repositories:
        print("WARNING: No repositories are accessible with GITHUB_TOKEN.")

    return repositories


def get_commit_details(repository_name, commit_sha):
    url = (
        f"{API_ROOT}/repos/{repository_api_path(repository_name)}"
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

    url = f"{API_ROOT}/repos/{repository_api_path(repository_name)}/commits"
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

    url = f"{API_ROOT}/repos/{repository_api_path(repository_name)}/pulls"

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
            "repository": repository_full_name(repository_name),
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

    url = f"{API_ROOT}/repos/{repository_api_path(repository_name)}/issues"

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
            "repository": repository_full_name(repository_name),
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

    url = f"{API_ROOT}/repos/{repository_api_path(repository_name)}/branches"
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
            "repository": repository_full_name(repository_name),
            "default_branch": default_branch,
            "total": len(formatted),
            "branches": formatted,
        },
    )

    print(f"Branches synchronized: {len(formatted)}")
    return formatted


def sync_repository_info(repository_name):
    url = f"{API_ROOT}/repos/{repository_api_path(repository_name)}"
    repository_info = github_get(url)

    if repository_info is None:
        return None

    formatted = {
        "id": repository_info.get("id"),
        "name": repository_info.get("name", repository_name),
        "full_name": repository_info.get(
            "full_name",
            repository_full_name(repository_name),
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
    url = f"{API_ROOT}/repos/{repository_api_path(repository_name)}/contributors"
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
            "repository": repository_full_name(repository_name),
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

    url = f"{API_ROOT}/repos/{repository_api_path(repository_name)}/collaborators"

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
            "repository": repository_full_name(repository_name),
            "total": len(formatted),
            "collaborators": formatted,
        },
    )

    print(f"Collaborators synchronized: {len(formatted)}")
    return formatted


# ============================================================
# GITHUB PROJECTS V2 SYNCHRONIZATION
# ============================================================

PROJECTS_FILE = DATA_FOLDER / "projects.json"


def github_graphql(query, variables=None, quiet=False):
    """Execute a GitHub GraphQL query and return the data object."""
    try:
        response = requests.post(
            f"{API_ROOT}/graphql",
            headers=PROJECT_HEADERS,
            json={
                "query": query,
                "variables": variables or {},
            },
            timeout=30,
        )
    except requests.RequestException as error:
        if not quiet:
            print("ERROR: Could not connect to GitHub GraphQL API.")
            print(error)
        return None

    if response.status_code != 200:
        if not quiet:
            print(f"GitHub GraphQL error: {response.status_code}")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text)
        return None

    try:
        payload = response.json()
    except ValueError:
        if not quiet:
            print("ERROR: GitHub GraphQL returned invalid JSON.")
        return None

    if payload.get("errors"):
        if not quiet:
            print("GitHub GraphQL returned errors:")
            print(json.dumps(payload["errors"], indent=2))
        return None

    return payload.get("data")


def github_project_get_all(url, params=None, max_pages=100, quiet=False):
    """Retrieve all pages from a Projects REST endpoint using the project PAT."""
    params = (params or {}).copy()
    params.setdefault("per_page", 100)
    all_items = []
    for page in range(1, max_pages + 1):
        page_params = params.copy()
        page_params["page"] = page
        try:
            response = requests.get(
                url,
                headers=PROJECT_HEADERS,
                params=page_params,
                timeout=30,
            )
        except requests.RequestException as error:
            if not quiet:
                print("ERROR: Could not connect to GitHub Projects REST API.")
                print(error)
            break
        if response.status_code != 200:
            if not quiet:
                print(f"GitHub Projects REST API error: {response.status_code}")
                try:
                    print(json.dumps(response.json(), indent=2))
                except ValueError:
                    print(response.text)
            break
        try:
            data = response.json()
        except ValueError:
            break
        if not isinstance(data, list) or not data:
            break
        all_items.extend(data)
        if len(data) < page_params["per_page"]:
            break
    return all_items


def get_priority_field_configuration(project_number):
    """Return Priority field id and option-id -> option-name mapping."""
    url = f"{API_ROOT}/orgs/{OWNER}/projectsV2/{project_number}/fields"
    fields = github_project_get_all(url, quiet=True)
    for field in fields:
        if str(field.get("name", "")).strip().lower() != "priority":
            continue
        options = {}
        for option in field.get("options", []) or []:
            option_id = str(option.get("id", "")).strip()
            raw_name = option.get("name")
            if isinstance(raw_name, dict):
                option_name = raw_name.get("raw") or raw_name.get("html") or ""
            else:
                option_name = raw_name or ""
            if option_id and option_name:
                options[option_id] = str(option_name)
        return field.get("id"), options
    return None, {}


def _extract_rest_priority(item, priority_field_id, priority_options):
    """Best-effort fallback for the REST Projects item representation."""
    if not isinstance(item, dict) or not priority_field_id:
        return ""
    wanted = str(priority_field_id)

    candidates = []
    for key in ("fields", "field_values", "fieldValues", "values"):
        value = item.get(key)
        if value is not None:
            candidates.append(value)

    def resolve(value):
        if isinstance(value, dict):
            # Common REST shapes: {field_id: option_id/value} or
            # {"id": field_id, "value": option_id}.
            if wanted in value:
                return resolve(value[wanted])
            for key in ("value", "optionId", "option_id", "single_select_option_id", "name", "raw"):
                if key in value:
                    result = resolve(value[key])
                    if result:
                        return result
            return ""
        if isinstance(value, list):
            for entry in value:
                if not isinstance(entry, dict):
                    continue
                entry_id = entry.get("id", entry.get("field_id", entry.get("fieldId")))
                if entry_id is not None and str(entry_id) != wanted:
                    continue
                result = resolve(entry)
                if result:
                    return result
            return ""
        if value is None:
            return ""
        text = str(value)
        return priority_options.get(text, text if text in priority_options.values() else "")

    return resolve(candidates[0]) if candidates else ""


def get_rest_priority_values(project_number, priority_field_id, priority_options):
    """Fetch Priority values through the Projects REST API as a fallback."""
    if not priority_field_id:
        return []
    url = f"{API_ROOT}/orgs/{OWNER}/projectsV2/{project_number}/items"
    return github_project_get_all(
        url,
        params={"fields": str(priority_field_id)},
        quiet=True,
    )


def _project_field_name(field_value):
    field = field_value.get("field") or {}
    return str(field.get("name") or "").strip()


def _project_item_value(field_value):
    typename = field_value.get("__typename", "")

    if typename == "ProjectV2ItemFieldSingleSelectValue":
        return field_value.get("name") or ""

    if typename == "ProjectV2ItemFieldDateValue":
        return field_value.get("date") or ""

    if typename == "ProjectV2ItemFieldTextValue":
        return field_value.get("text") or ""

    if typename == "ProjectV2ItemFieldNumberValue":
        return field_value.get("number")

    return ""


def _normalize_project_item(item, priority_options=None):
    """Convert a GraphQL ProjectV2 item into dashboard-friendly JSON."""
    content = item.get("content") or {}
    content_type = content.get("__typename", "")

    assignees = []
    assignee_data = content.get("assignees") or {}
    for user in assignee_data.get("nodes", []) or []:
        login = user.get("login")
        if login:
            assignees.append(login)

    repository = ""
    repository_data = content.get("repository") or {}
    repository = repository_data.get("nameWithOwner", "")

    priority_options = priority_options or {}

    field_values = {}
    for field_value in (item.get("fieldValues") or {}).get("nodes", []) or []:
        name = _project_field_name(field_value)
        if name:
            value = _project_item_value(field_value)
            if name.strip().lower() == "priority" and not value:
                value = priority_options.get(str(field_value.get("optionId", "")), "")
            field_values[name] = value

    def field_by_name(*names):
        lowered = {str(key).strip().lower(): value for key, value in field_values.items()}
        for name in names:
            value = lowered.get(name.lower())
            if value not in (None, ""):
                return value
        return ""

    labels = []
    for label in (content.get("labels") or {}).get("nodes", []) or []:
        label_name = label.get("name")
        if label_name:
            labels.append(label_name)

    human_type = {
        "Issue": "Issue",
        "PullRequest": "Pull Request",
        "DraftIssue": "Draft Issue",
    }.get(content_type, content_type or item.get("type", ""))

    # Prefer the project's named Priority field when available. GitHub's
    # fieldValueByName API is more reliable than inferring the field name
    # from the generic fieldValues connection. Fall back to the normalized
    # fieldValues map for compatibility with older project data.
    priority_value = item.get("priorityValue") or {}
    priority_type = priority_value.get("__typename", "")
    if priority_type == "ProjectV2ItemFieldSingleSelectValue":
        priority = priority_value.get("name") or priority_options.get(str(priority_value.get("optionId", "")), "")
    elif priority_type == "ProjectV2ItemFieldTextValue":
        priority = priority_value.get("text") or ""
    elif priority_type == "ProjectV2ItemFieldNumberValue":
        priority = priority_value.get("number")
        priority = "" if priority is None else str(priority)
    else:
        priority = field_by_name("Priority")

    return {
        "id": item.get("id", ""),
        "type": human_type,
        "title": content.get("title", "Untitled"),
        "number": content.get("number"),
        "url": content.get("url", ""),
        "labels": labels,
        "repository": repository,
        "assignees": assignees,
        "status": field_by_name("Status"),
        "due_date": field_by_name("Due Date", "Due date", "Target Date", "Target date"),
        "priority": priority,
        "field_values": field_values,
    }


def sync_projects(discovered_repositories):
    """
    Synchronize ALL Projects V2 owned by OWNER (ICPOC1).

    Projects are organization-owned resources, so they are not filtered by
    repository ownership. Project items are mapped to their actual repository
    when possible, including repositories outside ICPOC1.
    """
    print("\n" + "=" * 80)
    print("GITHUB PROJECTS V2 SYNCHRONIZATION")
    print("=" * 80)

    project_query = """
    query($login: String!, $after: String) {
      organization(login: $login) {
        projectsV2(first: 100, after: $after) {
          nodes {
            id
            number
            title
            shortDescription
            url
            public
            closed
            updatedAt
            repositories(first: 100) {
              nodes {
                nameWithOwner
                url
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    """

    raw_projects = []
    cursor = None

    while True:
        data = github_graphql(
            project_query,
            {"login": OWNER, "after": cursor},
        )

        if not data or not data.get("organization"):
            print("Unable to retrieve organization projects.")
            save_json_file(
                PROJECTS_FILE,
                {"organization": OWNER, "total": 0, "projects": []},
            )
            return []

        connection = data["organization"].get("projectsV2") or {}
        raw_projects.extend(connection.get("nodes") or [])

        page_info = connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break

    item_query = """
    query($projectId: ID!, $after: String) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100, after: $after) {
            nodes {
              id
              type
              content {
                __typename
                ... on DraftIssue {
                  title
                  assignees(first: 20) {
                    nodes { login }
                  }
                }
                ... on Issue {
                  number
                  title
                  url
                  repository { nameWithOwner }
                  assignees(first: 20) {
                    nodes { login }
                  }
                  labels(first: 50) {
                    nodes { name }
                  }
                }
                ... on PullRequest {
                  number
                  title
                  url
                  repository { nameWithOwner }
                  assignees(first: 20) {
                    nodes { login }
                  }
                  labels(first: 50) {
                    nodes { name }
                  }
                }
              }
              priorityValue: fieldValueByName(name: "Priority") {
                __typename
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                }
                ... on ProjectV2ItemFieldTextValue {
                  text
                }
                ... on ProjectV2ItemFieldNumberValue {
                  number
                }
              }
              fieldValues(first: 50) {
                nodes {
                  __typename
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                  ... on ProjectV2ItemFieldDateValue {
                    date
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                  ... on ProjectV2ItemFieldTextValue {
                    text
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                  ... on ProjectV2ItemFieldNumberValue {
                    number
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
      }
    }
    """

    projects = []

    for project in raw_projects:
        if not isinstance(project, dict):
            continue
        linked_repositories = []
        repo_connection = project.get("repositories") or {}
        for repo in repo_connection.get("nodes", []) or []:
            full_name = repo.get("nameWithOwner")
            if full_name:
                linked_repositories.append(full_name)

        normalized_project = {
            "id": project.get("id", ""),
            "number": project.get("number"),
            "title": project.get("title", "Untitled Project"),
            "description": project.get("shortDescription") or "",
            "url": project.get("url", ""),
            "public": bool(project.get("public", False)),
            "closed": bool(project.get("closed", False)),
            "updated_at": project.get("updatedAt"),
            "repositories": sorted(set(linked_repositories), key=str.lower),
            "items": [],
        }

        priority_field_id, priority_options = get_priority_field_configuration(
            normalized_project["number"]
        )
        rest_priority_items = get_rest_priority_values(
            normalized_project["number"], priority_field_id, priority_options
        )

        cursor = None
        all_items = []

        while True:
            data = github_graphql(
                item_query,
                {"projectId": normalized_project["id"], "after": cursor},
            )

            if not data or not data.get("node"):
                print(
                    f"WARNING: Could not retrieve items for project "
                    f"#{normalized_project['number']}."
                )
                break

            connection = data["node"].get("items") or {}
            for item in connection.get("nodes") or []:
                normalized = _normalize_project_item(item, priority_options)

                # If GraphQL did not expose Priority, use the REST Projects
                # field endpoint as a second source of truth.
                if not normalized.get("priority") and rest_priority_items:
                    for rest_item in rest_priority_items:
                        rest_content = rest_item.get("content") or {}
                        same_number = (
                            normalized.get("number") is not None
                            and rest_content.get("number") == normalized.get("number")
                        )
                        same_title = (
                            str(rest_content.get("title", "")).strip().lower()
                            == str(normalized.get("title", "")).strip().lower()
                            and str(normalized.get("title", "")).strip()
                        )
                        if same_number or same_title:
                            rest_priority = _extract_rest_priority(
                                rest_item, priority_field_id, priority_options
                            )
                            if rest_priority:
                                normalized["priority"] = rest_priority
                                normalized.setdefault("field_values", {})["Priority"] = rest_priority
                            break

                if normalized.get("title"):
                    all_items.append(normalized)

            page_info = connection.get("pageInfo") or {}
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info.get("endCursor")
            if not cursor:
                break

        # Project items can reveal repositories that are not explicitly listed
        # in the project's repository connection. Include those as well.
        item_repositories = [
            item.get("repository")
            for item in all_items
            if item.get("repository")
        ]
        normalized_project["repositories"] = sorted(
            set(normalized_project["repositories"]) | set(item_repositories),
            key=str.lower,
        )
        normalized_project["items"] = all_items
        projects.append(normalized_project)

    projects.sort(key=lambda item: str(item.get("title", "")).lower())

    save_json_file(
        PROJECTS_FILE,
        {
            "organization": OWNER,
            "total": len(projects),
            "projects": projects,
        },
    )

    # Build repository-local project views using full owner/repository names.
    # This allows an organization project to contain items from personal repos.
    projects_by_repo = {}
    for project in projects:
        for full_name in project.get("repositories", []) or []:
            projects_by_repo.setdefault(full_name.lower(), []).append(project)

    for repo in discovered_repositories:
        repo_name = repo.get("name")
        full_name = repo.get("full_name") or repository_full_name(repo_name)
        repo_projects = projects_by_repo.get(full_name.lower(), [])
        save_json_file(
            repository_files(repo_name)["projects"],
            {
                "repository": full_name,
                "total": len(repo_projects),
                "projects": repo_projects,
            },
        )

    print(f"Organization projects found: {len(raw_projects)}")
    print(f"Projects synchronized: {len(projects)}")
    for project in projects:
        print(
            f"  - #{project['number']} {project['title']} "
            f"({len(project['items'])} items)"
        )
        if project.get("items"):
            priorities = [
                item.get("priority", "") for item in project["items"]
                if item.get("priority")
            ]
            print(f"    Priority values captured: {len(priorities)}/{len(project['items'])}")

    return projects


def sync_one_repository(repository):
    """Synchronize every existing repository feature for one repository."""
    repository_name = repository.get("name")
    full_name = repository.get("full_name") or repository_full_name(repository_name)

    print("\n" + "=" * 80)
    print(f"SYNCHRONIZING REPOSITORY: {full_name}")
    print("=" * 80)

    # Ensure API helpers use this repository's real owner.
    register_repository(repository)

    repository_info = sync_repository_info(repository_name)

    if not repository_info:
        return None

    commits = sync_commits(repository_name)
    pull_requests = sync_pull_requests(repository_name)
    issues = sync_issues(repository_name)
    branches = sync_branches(repository_name, repository_info)
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



def project_count_for_repository(repository_name):
    data = load_json_file(repository_files(repository_name)["projects"], {"projects": []})
    if isinstance(data, dict) and isinstance(data.get("projects"), list):
        return len(data["projects"])
    if isinstance(data, list):
        return len(data)
    return 0

def main():
    print("\n" + "=" * 80)
    print("GITHUB USAGE & ACCESS REPORTING SYSTEM")
    print("MULTI-REPOSITORY SYNCHRONIZATION")
    print("=" * 80)
    print(f"Projects organization  : {OWNER}")
    print("Repository scope       : All repositories accessible to GITHUB_TOKEN")
    print(f"Default repository    : {DEFAULT_REPOSITORY}")
    print("Repository API token : GITHUB_TOKEN")
    print("Projects API token   : GITHUB_PROJECT_TOKEN")

    repositories = discover_repositories()

    if not repositories:
        print("\nNo accessible repositories were discovered.")
        print(
            "Check GITHUB_TOKEN permissions and the repository owner/name "
            "in .env."
        )
        return

    # Projects V2 are organization-owned, so synchronize them once after
    # repository discovery rather than making a separate project API call for
    # every repository.
    sync_projects(repositories)

    all_results = {}

    for repo in repositories:
        repository_name = repo.get("name")
        if not repository_name:
            continue

        result = sync_one_repository(repo)

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


    # Update repository index with synchronization counts so the dashboard
    # can build repository-wise activity without making extra API calls.
    index = load_json_file(
        REPOSITORY_INDEX_FILE,
        {
            "owner": "multiple",
            "project_owner": OWNER,
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
                    repository_full_name(name),
                ),
                "owner": info.get("owner") or repository_owner(name),
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
                "projects": project_count_for_repository(name),
            }
        )

    index["owner"] = "multiple"
    index["project_owner"] = OWNER
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