
# import json
# import os
# import shutil
# import time
# from pathlib import Path

# import jwt
# import requests
# from dotenv import load_dotenv
# import database as db

# BASE_DIR = Path(__file__).resolve().parent
# DATA_FOLDER = BASE_DIR / "data"
# REPOSITORIES_FOLDER = DATA_FOLDER / "repositories"
# REPOSITORY_INDEX_FILE = DATA_FOLDER / "repository_index.json"

# load_dotenv(BASE_DIR / ".env")

# # ---------------------------------------------------------------------------
# # GitHub App authentication
# # ---------------------------------------------------------------------------
# # The application now authenticates with a GitHub App installation token
# # instead of a Personal Access Token. The installation token is generated
# # automatically from the App ID + private key and refreshed when it is close
# # to expiry.

# GITHUB_APP_ID = (
#     os.getenv("GITHUB_APP_ID")
#     or os.getenv("GITHUB_APP_ID_NUMBER")
# )
# GITHUB_APP_INSTALLATION_ID = (
#     os.getenv("GITHUB_APP_INSTALLATION_ID")
#     or os.getenv("GITHUB_INSTALLATION_ID")
# )
# GITHUB_APP_PRIVATE_KEY_PATH = (
#     os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
#     or os.getenv("GITHUB_PRIVATE_KEY_PATH")
# )
# GITHUB_APP_PRIVATE_KEY = os.getenv("GITHUB_APP_PRIVATE_KEY")

# OWNER = os.getenv(
#     "GITHUB_REPO_OWNER",
#     os.getenv("GITHUB_OWNER", "ICPOC1"),
# )

# DEFAULT_REPOSITORY = os.getenv(
#     "GITHUB_REPO_NAME",
#     os.getenv("GITHUB_REPOSITORY", "TEST"),
# )

# if not GITHUB_APP_ID:
#     print("=" * 80)
#     print("ERROR: GITHUB_APP_ID was not found.")
#     print("Please check your .env file.")
#     print("=" * 80)
#     raise SystemExit(1)

# if not GITHUB_APP_INSTALLATION_ID:
#     print("=" * 80)
#     print("ERROR: GITHUB_APP_INSTALLATION_ID was not found.")
#     print("Please check your .env file.")
#     print("=" * 80)
#     raise SystemExit(1)

# if not GITHUB_APP_PRIVATE_KEY_PATH and not GITHUB_APP_PRIVATE_KEY:
#     print("=" * 80)
#     print("ERROR: GitHub App private key was not found.")
#     print("Set GITHUB_APP_PRIVATE_KEY_PATH or GITHUB_APP_PRIVATE_KEY in .env.")
#     print("=" * 80)
#     raise SystemExit(1)

# DATA_FOLDER.mkdir(parents=True, exist_ok=True)
# REPOSITORIES_FOLDER.mkdir(parents=True, exist_ok=True)

# API_ROOT = "https://api.github.com"
# GITHUB_API_VERSION = "2026-03-10"

# _INSTALLATION_TOKEN = None
# _INSTALLATION_TOKEN_EXPIRES_AT = 0


# def _load_github_app_private_key():
#     """Load the GitHub App private key from a file or .env value."""
#     if GITHUB_APP_PRIVATE_KEY_PATH:
#         key_path = Path(GITHUB_APP_PRIVATE_KEY_PATH)
#         if not key_path.is_absolute():
#             key_path = BASE_DIR / key_path
#         try:
#             return key_path.read_text(encoding="utf-8")
#         except OSError as error:
#             raise RuntimeError(
#                 f"Could not read GitHub App private key file: {key_path}\n{error}"
#             ) from error

#     # When stored directly in .env, escaped newlines are converted back to
#     # actual PEM line breaks.
#     return GITHUB_APP_PRIVATE_KEY.replace("\\n", "\n")


# def _create_github_app_jwt():
#     """Create the short-lived JWT used to request an installation token."""
#     now = int(time.time())
#     payload = {
#         "iat": now - 60,
#         "exp": now + 540,  # GitHub App JWTs are limited to 10 minutes.
#         "iss": GITHUB_APP_ID,
#     }
#     return jwt.encode(
#         payload,
#         _load_github_app_private_key(),
#         algorithm="RS256",
#     )


# def _request_installation_token(force_refresh=False):
#     """Generate a GitHub App installation token and cache it temporarily."""
#     global _INSTALLATION_TOKEN, _INSTALLATION_TOKEN_EXPIRES_AT

#     now = int(time.time())
#     if (
#         not force_refresh
#         and _INSTALLATION_TOKEN
#         and now < _INSTALLATION_TOKEN_EXPIRES_AT - 300
#     ):
#         return _INSTALLATION_TOKEN

#     app_jwt = _create_github_app_jwt()
#     response = requests.post(
#         f"{API_ROOT}/app/installations/{GITHUB_APP_INSTALLATION_ID}/access_tokens",
#         headers={
#             "Accept": "application/vnd.github+json",
#             "Authorization": f"Bearer {app_jwt}",
#             "X-GitHub-Api-Version": GITHUB_API_VERSION,
#         },
#         timeout=30,
#     )

#     if response.status_code != 201:
#         try:
#             details = json.dumps(response.json(), indent=2)
#         except ValueError:
#             details = response.text
#         raise RuntimeError(
#             f"GitHub App installation-token request failed "
#             f"({response.status_code}):\n{details}"
#         )

#     data = response.json()
#     _INSTALLATION_TOKEN = data.get("token")
#     expires_at = data.get("expires_at")

#     if not _INSTALLATION_TOKEN:
#         raise RuntimeError("GitHub did not return an installation token.")

#     # Installation tokens normally expire after one hour. Parse the GitHub
#     # timestamp when possible; otherwise use a safe one-hour fallback.
#     if expires_at:
#         try:
#             from datetime import datetime, timezone
#             _INSTALLATION_TOKEN_EXPIRES_AT = int(
#                 datetime.fromisoformat(
#                     expires_at.replace("Z", "+00:00")
#                 ).timestamp()
#             )
#         except (ValueError, TypeError):
#             _INSTALLATION_TOKEN_EXPIRES_AT = now + 3600
#     else:
#         _INSTALLATION_TOKEN_EXPIRES_AT = now + 3600

#     print(
#         "GitHub App installation token generated successfully "
#         f"(expires: {expires_at or 'unknown'})."
#     )
#     return _INSTALLATION_TOKEN


# def github_headers(force_refresh=False):
#     """Return current headers using the GitHub App installation token."""
#     token = _request_installation_token(force_refresh=force_refresh)
#     return {
#         "Accept": "application/vnd.github+json",
#         "Authorization": f"Bearer {token}",
#         "X-GitHub-Api-Version": GITHUB_API_VERSION,
#     }


# # Live headers are generated when a request is made so the installation token
# # can be refreshed automatically during a long synchronization.
# HEADERS = github_headers()
# PROJECT_HEADERS = HEADERS

# # Live repository registry. It is populated by discover_repositories() and
# # lets every repository operation use the repository's real owner instead of
# # assuming that all repositories belong to ICPOC1.
# REPOSITORY_REGISTRY = {}


# def repository_owner(repository_name):
#     key = str(repository_name or "").strip().lower()
#     entry = REPOSITORY_REGISTRY.get(key)
#     if isinstance(entry, dict) and entry.get("owner"):
#         return entry["owner"]
#     return OWNER


# def repository_full_name(repository_name):
#     key = str(repository_name or "").strip().lower()
#     entry = REPOSITORY_REGISTRY.get(key)
#     if isinstance(entry, dict) and entry.get("full_name"):
#         return entry["full_name"]
#     owner = repository_owner(repository_name)
#     return f"{owner}/{repository_name}"


# def repository_api_path(repository_name):
#     return f"{repository_owner(repository_name)}/{repository_name}"


# def register_repository(repo):
#     name = repo.get("name") if isinstance(repo, dict) else None
#     if not name:
#         return
#     owner = repo.get("owner") or str(repo.get("full_name", "")).split("/", 1)[0]
#     full_name = repo.get("full_name") or f"{owner}/{name}"
#     REPOSITORY_REGISTRY[str(name).lower()] = {
#         **repo,
#         "name": name,
#         "owner": owner,
#         "full_name": full_name,
#     }


# def normalize_repository_record(repo):
#     owner_data = repo.get("owner") or {}
#     owner = owner_data.get("login") if isinstance(owner_data, dict) else owner_data
#     owner = owner or str(repo.get("full_name", "")).split("/", 1)[0]
#     name = repo.get("name")
#     return {
#         "id": repo.get("id"),
#         "name": name,
#         "full_name": repo.get("full_name") or f"{owner}/{name}",
#         "owner": owner,
#         "private": repo.get("private", False),
#         "visibility": repo.get("visibility", "unknown"),
#         "default_branch": repo.get("default_branch", "main"),
#         "html_url": repo.get("html_url", ""),
#         "description": repo.get("description"),
#         "updated_at": repo.get("updated_at"),
#         "pushed_at": repo.get("pushed_at"),
#     }

# # Root-level files retained for compatibility with the original project.
# ROOT_FILES = {
#     "commits": DATA_FOLDER / "commits.json",
#     "pull_requests": DATA_FOLDER / "pull_requests.json",
#     "issues": DATA_FOLDER / "issues.json",
#     "branches": DATA_FOLDER / "branches.json",
#     "repository": DATA_FOLDER / "repository.json",
#     "contributors": DATA_FOLDER / "contributors.json",
#     "collaborators": DATA_FOLDER / "collaborators.json",
# }


# def safe_repository_folder(repository_name):
#     """Create a safe local folder name for a repository."""
#     safe = "".join(
#         char if char.isalnum() or char in "._-" else "_"
#         for char in repository_name
#     )
#     return safe or "repository"


# def repository_folder(repository_name):
#     return REPOSITORIES_FOLDER / safe_repository_folder(repository_name)


# def repository_files(repository_name):
#     folder = repository_folder(repository_name)
#     folder.mkdir(parents=True, exist_ok=True)
#     return {
#         "commits": folder / "commits.json",
#         "pull_requests": folder / "pull_requests.json",
#         "issues": folder / "issues.json",
#         "branches": folder / "branches.json",
#         "repository": folder / "repository.json",
#         "contributors": folder / "contributors.json",
#         "collaborators": folder / "collaborators.json",
#         "projects": folder / "projects.json",
#     }


# def load_json_file(file_path, default):
#     if not file_path.exists():
#         return default

#     try:
#         with open(file_path, "r", encoding="utf-8") as file:
#             return json.load(file)
#     except (json.JSONDecodeError, OSError):
#         print(f"WARNING: Could not read {file_path}")
#         return default


# def save_json_file(file_path, data):
#     try:
#         file_path.parent.mkdir(parents=True, exist_ok=True)
#         with open(file_path, "w", encoding="utf-8") as file:
#             json.dump(data, file, indent=4, ensure_ascii=False)
#         return True
#     except OSError as error:
#         print(f"ERROR: Could not save {file_path}")
#         print(error)
#         return False


# def github_get(url, params=None, timeout=30, quiet=False):
#     """Perform a GitHub GET request and return JSON."""
#     try:
#         response = requests.get(
#             url,
#             headers=github_headers(),
#             params=params,
#             timeout=timeout,
#         )
#         if response.status_code == 401:
#             response = requests.get(
#                 url,
#                 headers=github_headers(force_refresh=True),
#                 params=params,
#                 timeout=timeout,
#             )
#     except requests.RequestException as error:
#         if not quiet:
#             print("ERROR: Could not connect to GitHub.")
#             print(error)
#         return None

#     if response.status_code != 200:
#         if not quiet:
#             print(f"GitHub API error: {response.status_code}")
#             try:
#                 print(json.dumps(response.json(), indent=2))
#             except ValueError:
#                 print(response.text)
#         return None

#     try:
#         return response.json()
#     except ValueError:
#         if not quiet:
#             print("ERROR: GitHub returned invalid JSON.")
#         return None


# def github_get_all(url, params=None, max_pages=100, quiet=False):
#     """Retrieve all pages from a list endpoint."""
#     params = (params or {}).copy()
#     params.setdefault("per_page", 100)

#     all_items = []

#     for page in range(1, max_pages + 1):
#         params["page"] = page
#         data = github_get(url, params=params, quiet=quiet)

#         if data is None or not isinstance(data, list) or not data:
#             break

#         all_items.extend(data)

#         if len(data) < params["per_page"]:
#             break

#     return all_items


# def discover_repositories():
#     """
#     Discover every repository the authenticated GITHUB_TOKEN can access.

#     This deliberately combines /user/repos with the ICPOC1 organization
#     endpoint. /user/repos covers repositories owned by the authenticated user,
#     collaborator repositories, and repositories available through an
#     organization. The organization endpoint provides an additional reliable
#     source for ICPOC1 repositories, including future repositories.
#     """
#     global REPOSITORY_REGISTRY

#     print("=" * 80)
#     print("REPOSITORY DISCOVERY")
#     print("=" * 80)
#     print("Repository scope       : All repositories accessible to the GitHub App installation")
#     print(f"Projects organization  : {OWNER}")

#     discovered = {}

#     # GitHub App installation tokens are installation-scoped and do not use
#     # the user-scoped /user/repos endpoint. Enumerate repositories from the
#     # organization where the App is installed. With "All repositories"
#     # selected during installation, this automatically includes current and
#     # future repositories in the organization.
#     org_repos = github_get_all(
#         f"{API_ROOT}/orgs/{OWNER}/repos",
#         params={
#             "type": "all",
#             "sort": "updated",
#             "direction": "desc",
#         },
#         quiet=False,
#     )

#     if org_repos:
#         for repo in org_repos:
#             record = normalize_repository_record(repo)
#             if record.get("name") and record.get("owner"):
#                 discovered[record["full_name"].lower()] = record

#     # Last-resort explicit repository lookup for the configured TEST setting.
#     if not any(
#         str(item.get("name", "")).lower() == DEFAULT_REPOSITORY.lower()
#         for item in discovered.values()
#     ):
#         fallback_owner = os.getenv("GITHUB_REPO_OWNER", OWNER)
#         fallback = github_get(
#             f"{API_ROOT}/repos/{fallback_owner}/{DEFAULT_REPOSITORY}",
#             quiet=True,
#         )
#         if fallback:
#             record = normalize_repository_record(fallback)
#             discovered[record["full_name"].lower()] = record

#     repositories = sorted(
#         discovered.values(),
#         key=lambda item: (
#             str(item.get("owner", "")).lower(),
#             str(item.get("name", "")).lower(),
#         ),
#     )

#     REPOSITORY_REGISTRY = {}
#     for repo in repositories:
#         register_repository(repo)

#     print(f"Repositories discovered: {len(repositories)}")
#     for repo in repositories:
#         print(f"  - {repo.get('full_name')}")

#     if not repositories:
#         print("WARNING: No repositories are accessible with GITHUB_TOKEN.")

#     return repositories


# def get_commit_details(repository_name, commit_sha):
#     url = (
#         f"{API_ROOT}/repos/{repository_api_path(repository_name)}"
#         f"/commits/{commit_sha}"
#     )
#     return github_get(url, quiet=True)


# def load_commit_history(repository_name):
#     files = repository_files(repository_name)

#     data = load_json_file(
#         files["commits"],
#         {"commits": []},
#     )

#     if not isinstance(data, dict):
#         data = {"commits": []}

#     if not isinstance(data.get("commits"), list):
#         data["commits"] = []

#     return data


# def build_commit_record(repository_name, commit):
#     sha = commit.get("sha", "Unknown")
#     details = get_commit_details(repository_name, sha)

#     if not details:
#         return None

#     commit_data = details.get("commit") or {}
#     author_data = commit_data.get("author") or {}
#     stats = details.get("stats") or {}

#     additions = int(stats.get("additions", 0) or 0)
#     deletions = int(stats.get("deletions", 0) or 0)

#     files = []
#     for file_data in details.get("files", []) or []:
#         files.append(
#             {
#                 "filename": file_data.get("filename", "Unknown"),
#                 "status": file_data.get("status", "Unknown"),
#                 "additions": int(file_data.get("additions", 0) or 0),
#                 "deletions": int(file_data.get("deletions", 0) or 0),
#                 "changes": int(file_data.get("changes", 0) or 0),
#             }
#         )

#     return {
#         "sha": sha,
#         "author": {
#             "name": author_data.get("name", "Unknown"),
#             "email": author_data.get("email", "Unknown"),
#         },
#         "date": author_data.get("date", "Unknown"),
#         "message": commit_data.get(
#             "message",
#             "No commit message",
#         ),
#         "statistics": {
#             "additions": additions,
#             "deletions": deletions,
#             "total_changes": int(
#                 stats.get(
#                     "total",
#                     additions + deletions,
#                 )
#                 or 0
#             ),
#         },
#         "files": files,
#     }


# def sync_commits(repository_name):
#     print("\n" + "=" * 80)
#     print(f"COMMIT SYNCHRONIZATION: {repository_name}")
#     print("=" * 80)

#     url = f"{API_ROOT}/repos/{repository_api_path(repository_name)}/commits"
#     github_commits = github_get_all(url)
#     if github_commits is None:
#         print("Unable to retrieve commits.")
#         repository_id = db.repository_id_by_name(repository_name)
#         return db.get_repository_commits(repository_id) if repository_id else []

#     formatted=[]
#     for commit in github_commits:
#         sha=commit.get("sha")
#         if not sha:
#             continue
#         detailed_record=build_commit_record(repository_name, commit)
#         if detailed_record:
#             formatted.append(detailed_record)

#     repository_id=db.repository_id_by_name(repository_name)
#     if repository_id is None:
#         raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
#     db.sync_commits(repository_id, formatted)
#     print(f"Commits synchronized to MySQL: {len(formatted)}")
#     return formatted

# def sync_pull_requests(repository_name):
#     print("\n" + "=" * 80)
#     print(f"PULL REQUEST SYNCHRONIZATION: {repository_name}")
#     print("=" * 80)
#     url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}/pulls"
#     pull_requests=github_get_all(url, params={"state":"all","sort":"updated","direction":"desc"})
#     if pull_requests is None:
#         return []
#     formatted=[]
#     for pr in pull_requests:
#         user=pr.get("user") or {}; head=pr.get("head") or {}; base=pr.get("base") or {}
#         formatted.append({
#             "number":pr.get("number"), "title":pr.get("title","No title"),
#             "state":pr.get("state","unknown"), "draft":bool(pr.get("draft",False)),
#             "merged":pr.get("merged_at") is not None, "author":user.get("login","Unknown"),
#             "author_url":user.get("html_url",""), "created_at":pr.get("created_at"),
#             "updated_at":pr.get("updated_at"), "closed_at":pr.get("closed_at"),
#             "merged_at":pr.get("merged_at"), "url":pr.get("html_url",""),
#             "head_branch":head.get("ref",""), "base_branch":base.get("ref","")})
#     repository_id=db.repository_id_by_name(repository_name)
#     if repository_id is None: raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
#     db.sync_pull_requests(repository_id, formatted)
#     print(f"Pull requests synchronized to MySQL: {len(formatted)}")
#     return formatted

# def sync_issues(repository_name):
#     print("\n" + "=" * 80)
#     print(f"ISSUE SYNCHRONIZATION: {repository_name}")
#     print("=" * 80)
#     url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}/issues"
#     issues=github_get_all(url, params={"state":"all","sort":"updated","direction":"desc"})
#     if issues is None: return []
#     formatted=[]
#     for issue in issues:
#         if "pull_request" in issue: continue
#         user=issue.get("user") or {}
#         labels=[label.get("name","") for label in issue.get("labels",[]) or []]
#         formatted.append({
#             "number":issue.get("number"), "title":issue.get("title","No title"),
#             "state":issue.get("state","unknown"), "author":user.get("login","Unknown"),
#             "author_url":user.get("html_url",""), "created_at":issue.get("created_at"),
#             "updated_at":issue.get("updated_at"), "closed_at":issue.get("closed_at"),
#             "comments":int(issue.get("comments",0) or 0), "labels":labels,
#             "url":issue.get("html_url","")})
#     repository_id=db.repository_id_by_name(repository_name)
#     if repository_id is None: raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
#     db.sync_issues(repository_id, formatted)
#     print(f"Issues synchronized to MySQL: {len(formatted)}")
#     return formatted

# def sync_branches(repository_name, repository_info):
#     print("\n" + "=" * 80)
#     print(f"BRANCH SYNCHRONIZATION: {repository_name}")
#     print("=" * 80)
#     url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}/branches"
#     branches=github_get_all(url)
#     if branches is None: return []
#     default_branch=repository_info.get("default_branch","") if repository_info else ""
#     formatted=[]
#     for branch in branches:
#         branch_name=branch.get("name","Unknown"); commit_data=branch.get("commit") or {}
#         formatted.append({"name":branch_name,"default":branch_name==default_branch,
#                           "protected":bool(branch.get("protected",False)),"commit_sha":commit_data.get("sha","")})
#     repository_id=db.repository_id_by_name(repository_name)
#     if repository_id is None: raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
#     db.sync_branches(repository_id, formatted)
#     print(f"Branches synchronized to MySQL: {len(formatted)}")
#     return formatted

# def sync_repository_info(repository_name):
#     url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}"
#     repository_info=github_get(url)
#     if repository_info is None: return None
#     owner_data=repository_info.get("owner") or {}
#     owner=owner_data.get("login") if isinstance(owner_data,dict) else owner_data
#     formatted={
#         "id":repository_info.get("id"), "name":repository_info.get("name",repository_name),
#         "full_name":repository_info.get("full_name",repository_full_name(repository_name)),
#         "owner":owner or repository_owner(repository_name), "description":repository_info.get("description"),
#         "private":repository_info.get("private",False), "visibility":repository_info.get("visibility","unknown"),
#         "default_branch":repository_info.get("default_branch","main"), "html_url":repository_info.get("html_url",""),
#         "clone_url":repository_info.get("clone_url",""), "ssh_url":repository_info.get("ssh_url",""),
#         "language":repository_info.get("language"), "created_at":repository_info.get("created_at"),
#         "updated_at":repository_info.get("updated_at"), "pushed_at":repository_info.get("pushed_at"),
#         "size":repository_info.get("size",0), "stars":repository_info.get("stargazers_count",0),
#         "forks":repository_info.get("forks_count",0), "open_issues":repository_info.get("open_issues_count",0),
#         "watchers":repository_info.get("watchers_count",0), "archived":repository_info.get("archived",False),
#         "disabled":repository_info.get("disabled",False)}
#     db.upsert_repository(formatted)
#     register_repository(formatted)
#     return formatted

# def sync_contributors(repository_name):
#     url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}/contributors"
#     contributors=github_get_all(url)
#     if contributors is None: return []
#     formatted=[{"login":c.get("login","Unknown"),"id":c.get("id"),"contributions":int(c.get("contributions",0) or 0),
#                 "type":c.get("type","User"),"profile_url":c.get("html_url",""),"avatar_url":c.get("avatar_url","")}
#                for c in contributors]
#     repository_id=db.repository_id_by_name(repository_name)
#     if repository_id is None: raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
#     db.sync_contributors(repository_id, formatted)
#     print(f"Contributors synchronized to MySQL: {len(formatted)}")
#     return formatted

# def sync_collaborators(repository_name):
#     print("\n" + "=" * 80)
#     print(f"COLLABORATOR / ACCESS SYNCHRONIZATION: {repository_name}")
#     print("=" * 80)
#     url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}/collaborators"
#     collaborators=github_get_all(url, params={"affiliation":"all"})
#     if collaborators is None:
#         print("Collaborators could not be retrieved. The token may not have permission to read collaborator data.")
#         return []
#     formatted=[]
#     for collaborator in collaborators:
#         permissions=collaborator.get("permissions") or {}
#         formatted.append({"login":collaborator.get("login","Unknown"),"id":collaborator.get("id"),
#                           "type":collaborator.get("type","User"),"role_name":collaborator.get("role_name","Unknown"),
#                           "admin":bool(permissions.get("admin",False)),"maintain":bool(permissions.get("maintain",False)),
#                           "push":bool(permissions.get("push",False)),"triage":bool(permissions.get("triage",False)),
#                           "pull":bool(permissions.get("pull",False)),"profile_url":collaborator.get("html_url","")})
#     repository_id=db.repository_id_by_name(repository_name)
#     if repository_id is None: raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
#     db.sync_collaborators(repository_id, formatted)
#     print(f"Collaborators synchronized to MySQL: {len(formatted)}")
#     return formatted


# # ============================================================
# # GITHUB PROJECTS V2 SYNCHRONIZATION
# # ============================================================

# PROJECTS_FILE = DATA_FOLDER / "projects.json"


# def github_graphql(query, variables=None, quiet=False):
#     """Execute a GitHub GraphQL query and return the data object."""
#     try:
#         response = requests.post(
#             f"{API_ROOT}/graphql",
#             headers=github_headers(),
#             json={
#                 "query": query,
#                 "variables": variables or {},
#             },
#             timeout=30,
#         )
#         if response.status_code == 401:
#             response = requests.post(
#                 f"{API_ROOT}/graphql",
#                 headers=github_headers(force_refresh=True),
#                 json={
#                     "query": query,
#                     "variables": variables or {},
#                 },
#                 timeout=30,
#             )
#     except requests.RequestException as error:
#         if not quiet:
#             print("ERROR: Could not connect to GitHub GraphQL API.")
#             print(error)
#         return None

#     if response.status_code != 200:
#         if not quiet:
#             print(f"GitHub GraphQL error: {response.status_code}")
#             try:
#                 print(json.dumps(response.json(), indent=2))
#             except ValueError:
#                 print(response.text)
#         return None

#     try:
#         payload = response.json()
#     except ValueError:
#         if not quiet:
#             print("ERROR: GitHub GraphQL returned invalid JSON.")
#         return None

#     if payload.get("errors"):
#         if not quiet:
#             print("GitHub GraphQL returned errors:")
#             print(json.dumps(payload["errors"], indent=2))
#         return None

#     return payload.get("data")


# def github_project_get_all(url, params=None, max_pages=100, quiet=False):
#     """Retrieve all pages from a Projects REST endpoint using the project PAT."""
#     params = (params or {}).copy()
#     params.setdefault("per_page", 100)
#     all_items = []
#     for page in range(1, max_pages + 1):
#         page_params = params.copy()
#         page_params["page"] = page
#         try:
#             response = requests.get(
#                 url,
#                 headers=github_headers(),
#                 params=page_params,
#                 timeout=30,
#             )
#         except requests.RequestException as error:
#             if not quiet:
#                 print("ERROR: Could not connect to GitHub Projects REST API.")
#                 print(error)
#             break
#         if response.status_code != 200:
#             if not quiet:
#                 print(f"GitHub Projects REST API error: {response.status_code}")
#                 try:
#                     print(json.dumps(response.json(), indent=2))
#                 except ValueError:
#                     print(response.text)
#             break
#         try:
#             data = response.json()
#         except ValueError:
#             break
#         if not isinstance(data, list) or not data:
#             break
#         all_items.extend(data)
#         if len(data) < page_params["per_page"]:
#             break
#     return all_items


# def get_priority_field_configuration(project_number):
#     """Return Priority field id and option-id -> option-name mapping."""
#     url = f"{API_ROOT}/orgs/{OWNER}/projectsV2/{project_number}/fields"
#     fields = github_project_get_all(url, quiet=True)
#     for field in fields:
#         if str(field.get("name", "")).strip().lower() != "priority":
#             continue
#         options = {}
#         for option in field.get("options", []) or []:
#             option_id = str(option.get("id", "")).strip()
#             raw_name = option.get("name")
#             if isinstance(raw_name, dict):
#                 option_name = raw_name.get("raw") or raw_name.get("html") or ""
#             else:
#                 option_name = raw_name or ""
#             if option_id and option_name:
#                 options[option_id] = str(option_name)
#         return field.get("id"), options
#     return None, {}


# def _extract_rest_priority(item, priority_field_id, priority_options):
#     """Best-effort fallback for the REST Projects item representation."""
#     if not isinstance(item, dict) or not priority_field_id:
#         return ""
#     wanted = str(priority_field_id)

#     candidates = []
#     for key in ("fields", "field_values", "fieldValues", "values"):
#         value = item.get(key)
#         if value is not None:
#             candidates.append(value)

#     def resolve(value):
#         if isinstance(value, dict):
#             # Common REST shapes: {field_id: option_id/value} or
#             # {"id": field_id, "value": option_id}.
#             if wanted in value:
#                 return resolve(value[wanted])
#             for key in ("value", "optionId", "option_id", "single_select_option_id", "name", "raw"):
#                 if key in value:
#                     result = resolve(value[key])
#                     if result:
#                         return result
#             return ""
#         if isinstance(value, list):
#             for entry in value:
#                 if not isinstance(entry, dict):
#                     continue
#                 entry_id = entry.get("id", entry.get("field_id", entry.get("fieldId")))
#                 if entry_id is not None and str(entry_id) != wanted:
#                     continue
#                 result = resolve(entry)
#                 if result:
#                     return result
#             return ""
#         if value is None:
#             return ""
#         text = str(value)
#         return priority_options.get(text, text if text in priority_options.values() else "")

#     return resolve(candidates[0]) if candidates else ""


# def get_rest_priority_values(project_number, priority_field_id, priority_options):
#     """Fetch Priority values through the Projects REST API as a fallback."""
#     if not priority_field_id:
#         return []
#     url = f"{API_ROOT}/orgs/{OWNER}/projectsV2/{project_number}/items"
#     return github_project_get_all(
#         url,
#         params={"fields": str(priority_field_id)},
#         quiet=True,
#     )


# def _project_field_name(field_value):
#     field = field_value.get("field") or {}
#     return str(field.get("name") or "").strip()


# def _project_item_value(field_value):
#     typename = field_value.get("__typename", "")

#     if typename == "ProjectV2ItemFieldSingleSelectValue":
#         return field_value.get("name") or ""

#     if typename == "ProjectV2ItemFieldDateValue":
#         return field_value.get("date") or ""

#     if typename == "ProjectV2ItemFieldTextValue":
#         return field_value.get("text") or ""

#     if typename == "ProjectV2ItemFieldNumberValue":
#         return field_value.get("number")

#     return ""


# def _normalize_project_item(item, priority_options=None):
#     """Convert a GraphQL ProjectV2 item into dashboard-friendly JSON."""
#     content = item.get("content") or {}
#     content_type = content.get("__typename", "")

#     assignees = []
#     assignee_data = content.get("assignees") or {}
#     for user in assignee_data.get("nodes", []) or []:
#         login = user.get("login")
#         if login:
#             assignees.append(login)

#     repository = ""
#     repository_data = content.get("repository") or {}
#     repository = repository_data.get("nameWithOwner", "")

#     priority_options = priority_options or {}

#     field_values = {}
#     for field_value in (item.get("fieldValues") or {}).get("nodes", []) or []:
#         name = _project_field_name(field_value)
#         if name:
#             value = _project_item_value(field_value)
#             if name.strip().lower() == "priority" and not value:
#                 value = priority_options.get(str(field_value.get("optionId", "")), "")
#             field_values[name] = value

#     def field_by_name(*names):
#         lowered = {str(key).strip().lower(): value for key, value in field_values.items()}
#         for name in names:
#             value = lowered.get(name.lower())
#             if value not in (None, ""):
#                 return value
#         return ""

#     labels = []
#     for label in (content.get("labels") or {}).get("nodes", []) or []:
#         label_name = label.get("name")
#         if label_name:
#             labels.append(label_name)

#     human_type = {
#         "Issue": "Issue",
#         "PullRequest": "Pull Request",
#         "DraftIssue": "Draft Issue",
#     }.get(content_type, content_type or item.get("type", ""))

#     # Prefer the project's named Priority field when available. GitHub's
#     # fieldValueByName API is more reliable than inferring the field name
#     # from the generic fieldValues connection. Fall back to the normalized
#     # fieldValues map for compatibility with older project data.
#     priority_value = item.get("priorityValue") or {}
#     priority_type = priority_value.get("__typename", "")
#     if priority_type == "ProjectV2ItemFieldSingleSelectValue":
#         priority = priority_value.get("name") or priority_options.get(str(priority_value.get("optionId", "")), "")
#     elif priority_type == "ProjectV2ItemFieldTextValue":
#         priority = priority_value.get("text") or ""
#     elif priority_type == "ProjectV2ItemFieldNumberValue":
#         priority = priority_value.get("number")
#         priority = "" if priority is None else str(priority)
#     else:
#         priority = field_by_name("Priority")

#     return {
#         "id": item.get("id", ""),
#         "type": human_type,
#         "title": content.get("title", "Untitled"),
#         "number": content.get("number"),
#         "url": content.get("url", ""),
#         "labels": labels,
#         "repository": repository,
#         "assignees": assignees,
#         "status": field_by_name("Status"),
#         "due_date": field_by_name("Due Date", "Due date", "Target Date", "Target date"),
#         "priority": priority,
#         "field_values": field_values,
#     }


# def sync_projects(discovered_repositories):
#     """
#     Synchronize ALL Projects V2 owned by OWNER (ICPOC1).

#     Projects are organization-owned resources, so they are not filtered by
#     repository ownership. Project items are mapped to their actual repository
#     when possible, including repositories outside ICPOC1.
#     """
#     print("\n" + "=" * 80)
#     print("GITHUB PROJECTS V2 SYNCHRONIZATION")
#     print("=" * 80)

#     project_query = """
#     query($login: String!, $after: String) {
#       organization(login: $login) {
#         projectsV2(first: 100, after: $after) {
#           nodes {
#             id
#             number
#             title
#             shortDescription
#             url
#             public
#             closed
#             updatedAt
#             repositories(first: 100) {
#               nodes {
#                 nameWithOwner
#                 url
#               }
#               pageInfo {
#                 hasNextPage
#                 endCursor
#               }
#             }
#           }
#           pageInfo {
#             hasNextPage
#             endCursor
#           }
#         }
#       }
#     }
#     """

#     raw_projects = []
#     cursor = None

#     while True:
#         data = github_graphql(
#             project_query,
#             {"login": OWNER, "after": cursor},
#         )

#         if not data or not data.get("organization"):
#             print("Unable to retrieve organization projects.")
#             db.replace_projects(OWNER, [])
#             return []

#         connection = data["organization"].get("projectsV2") or {}
#         raw_projects.extend(connection.get("nodes") or [])

#         page_info = connection.get("pageInfo") or {}
#         if not page_info.get("hasNextPage"):
#             break
#         cursor = page_info.get("endCursor")
#         if not cursor:
#             break

#     item_query = """
#     query($projectId: ID!, $after: String) {
#       node(id: $projectId) {
#         ... on ProjectV2 {
#           items(first: 100, after: $after) {
#             nodes {
#               id
#               type
#               content {
#                 __typename
#                 ... on DraftIssue {
#                   title
#                   assignees(first: 20) {
#                     nodes { login }
#                   }
#                 }
#                 ... on Issue {
#                   number
#                   title
#                   url
#                   repository { nameWithOwner }
#                   assignees(first: 20) {
#                     nodes { login }
#                   }
#                   labels(first: 50) {
#                     nodes { name }
#                   }
#                 }
#                 ... on PullRequest {
#                   number
#                   title
#                   url
#                   repository { nameWithOwner }
#                   assignees(first: 20) {
#                     nodes { login }
#                   }
#                   labels(first: 50) {
#                     nodes { name }
#                   }
#                 }
#               }
#               priorityValue: fieldValueByName(name: "Priority") {
#                 __typename
#                 ... on ProjectV2ItemFieldSingleSelectValue {
#                   name
#                 }
#                 ... on ProjectV2ItemFieldTextValue {
#                   text
#                 }
#                 ... on ProjectV2ItemFieldNumberValue {
#                   number
#                 }
#               }
#               fieldValues(first: 50) {
#                 nodes {
#                   __typename
#                   ... on ProjectV2ItemFieldSingleSelectValue {
#                     name
#                     field { ... on ProjectV2FieldCommon { name } }
#                   }
#                   ... on ProjectV2ItemFieldDateValue {
#                     date
#                     field { ... on ProjectV2FieldCommon { name } }
#                   }
#                   ... on ProjectV2ItemFieldTextValue {
#                     text
#                     field { ... on ProjectV2FieldCommon { name } }
#                   }
#                   ... on ProjectV2ItemFieldNumberValue {
#                     number
#                     field { ... on ProjectV2FieldCommon { name } }
#                   }
#                 }
#               }
#             }
#             pageInfo {
#               hasNextPage
#               endCursor
#             }
#           }
#         }
#       }
#     }
#     """

#     projects = []

#     for project in raw_projects:
#         if not isinstance(project, dict):
#             continue
#         linked_repositories = []
#         repo_connection = project.get("repositories") or {}
#         for repo in repo_connection.get("nodes", []) or []:
#             full_name = repo.get("nameWithOwner")
#             if full_name:
#                 linked_repositories.append(full_name)

#         normalized_project = {
#             "id": project.get("id", ""),
#             "number": project.get("number"),
#             "title": project.get("title", "Untitled Project"),
#             "description": project.get("shortDescription") or "",
#             "url": project.get("url", ""),
#             "public": bool(project.get("public", False)),
#             "closed": bool(project.get("closed", False)),
#             "updated_at": project.get("updatedAt"),
#             "repositories": sorted(set(linked_repositories), key=str.lower),
#             "items": [],
#         }

#         priority_field_id, priority_options = get_priority_field_configuration(
#             normalized_project["number"]
#         )
#         rest_priority_items = get_rest_priority_values(
#             normalized_project["number"], priority_field_id, priority_options
#         )

#         cursor = None
#         all_items = []

#         while True:
#             data = github_graphql(
#                 item_query,
#                 {"projectId": normalized_project["id"], "after": cursor},
#             )

#             if not data or not data.get("node"):
#                 print(
#                     f"WARNING: Could not retrieve items for project "
#                     f"#{normalized_project['number']}."
#                 )
#                 break

#             connection = data["node"].get("items") or {}
#             for item in connection.get("nodes") or []:
#                 normalized = _normalize_project_item(item, priority_options)

#                 # If GraphQL did not expose Priority, use the REST Projects
#                 # field endpoint as a second source of truth.
#                 if not normalized.get("priority") and rest_priority_items:
#                     for rest_item in rest_priority_items:
#                         rest_content = rest_item.get("content") or {}
#                         same_number = (
#                             normalized.get("number") is not None
#                             and rest_content.get("number") == normalized.get("number")
#                         )
#                         same_title = (
#                             str(rest_content.get("title", "")).strip().lower()
#                             == str(normalized.get("title", "")).strip().lower()
#                             and str(normalized.get("title", "")).strip()
#                         )
#                         if same_number or same_title:
#                             rest_priority = _extract_rest_priority(
#                                 rest_item, priority_field_id, priority_options
#                             )
#                             if rest_priority:
#                                 normalized["priority"] = rest_priority
#                                 normalized.setdefault("field_values", {})["Priority"] = rest_priority
#                             break

#                 if normalized.get("title"):
#                     all_items.append(normalized)

#             page_info = connection.get("pageInfo") or {}
#             if not page_info.get("hasNextPage"):
#                 break
#             cursor = page_info.get("endCursor")
#             if not cursor:
#                 break

#         # Project items can reveal repositories that are not explicitly listed
#         # in the project's repository connection. Include those as well.
#         item_repositories = [
#             item.get("repository")
#             for item in all_items
#             if item.get("repository")
#         ]
#         normalized_project["repositories"] = sorted(
#             set(normalized_project["repositories"]) | set(item_repositories),
#             key=str.lower,
#         )
#         normalized_project["items"] = all_items
#         projects.append(normalized_project)

#     projects.sort(key=lambda item: str(item.get("title", "")).lower())

#     db.replace_projects(OWNER, projects)

#     # MySQL stores project-to-repository relationships centrally; no local JSON
#     # project copies are required in the production application.
#     print(f"Organization projects found: {len(raw_projects)}")
#     print(f"Projects synchronized: {len(projects)}")
#     for project in projects:
#         print(
#             f"  - #{project['number']} {project['title']} "
#             f"({len(project['items'])} items)"
#         )
#         if project.get("items"):
#             priorities = [
#                 item.get("priority", "") for item in project["items"]
#                 if item.get("priority")
#             ]
#             print(f"    Priority values captured: {len(priorities)}/{len(project['items'])}")

#     return projects


# def sync_one_repository(repository):
#     """Synchronize every existing repository feature for one repository."""
#     repository_name = repository.get("name")
#     full_name = repository.get("full_name") or repository_full_name(repository_name)

#     print("\n" + "=" * 80)
#     print(f"SYNCHRONIZING REPOSITORY: {full_name}")
#     print("=" * 80)

#     # Ensure API helpers use this repository's real owner.
#     register_repository(repository)

#     repository_info = sync_repository_info(repository_name)

#     if not repository_info:
#         return None

#     commits = sync_commits(repository_name)
#     pull_requests = sync_pull_requests(repository_name)
#     issues = sync_issues(repository_name)
#     branches = sync_branches(repository_name, repository_info)
#     contributors = sync_contributors(repository_name)
#     collaborators = sync_collaborators(repository_name)

#     return {
#         "repository": repository_info,
#         "commits": commits,
#         "pull_requests": pull_requests,
#         "issues": issues,
#         "branches": branches,
#         "contributors": contributors,
#         "collaborators": collaborators,
#     }


# def mirror_default_repository(repository_name):
#     """
#     Keep the original data/*.json layout working for existing code.
#     """
#     if repository_name.lower() != DEFAULT_REPOSITORY.lower():
#         return

#     files = repository_files(repository_name)

#     for key, root_file in ROOT_FILES.items():
#         source = files[key]
#         if source.exists():
#             try:
#                 shutil.copy2(source, root_file)
#             except OSError as error:
#                 print(f"WARNING: Could not mirror {source}: {error}")


# def display_commit_report(repository_name, commits):
#     print("\n" + "=" * 80)
#     print(f"HISTORICAL COMMIT REPORT: {repository_name}")
#     print("=" * 80)
#     print(f"Total tracked commits: {len(commits)}")

#     for index, commit in enumerate(commits, start=1):
#         author = commit.get("author") or {}
#         stats = commit.get("statistics") or {}

#         print("\n" + "-" * 80)
#         print(f"COMMIT #{index}")
#         print("-" * 80)
#         print("SHA      :", commit.get("sha", "Unknown"))
#         print("Author   :", author.get("name", "Unknown"))
#         print("Email    :", author.get("email", "Unknown"))
#         print("Date     :", commit.get("date", "Unknown"))
#         print("Message  :", commit.get("message", "Unknown"))
#         print("Additions:", stats.get("additions", 0))
#         print("Deletions:", stats.get("deletions", 0))
#         print("Changes  :", stats.get("total_changes", 0))

#         print("Files:")
#         for file_data in commit.get("files", []):
#             print(
#                 f"  - {file_data.get('filename', 'Unknown')} "
#                 f"[{file_data.get('status', 'Unknown')}] "
#                 f"+{file_data.get('additions', 0)} "
#                 f"-{file_data.get('deletions', 0)}"
#             )


# def display_repository_summary(repository_name, result):
#     print("\n" + "=" * 80)
#     print(f"REPOSITORY SUMMARY: {repository_name}")
#     print("=" * 80)
#     print(f"Commits          : {len(result['commits'])}")
#     print(f"Pull Requests    : {len(result['pull_requests'])}")
#     print(f"Issues           : {len(result['issues'])}")
#     print(f"Branches         : {len(result['branches'])}")
#     print(f"Contributors     : {len(result['contributors'])}")
#     print(f"Collaborators    : {len(result['collaborators'])}")



# def project_count_for_repository(repository_name):
#     return db.count_projects_for_repository(repository_name)

# def main():
#     print("\n" + "=" * 80)
#     print("GITHUB USAGE & ACCESS REPORTING SYSTEM")
#     print("MYSQL-BACKED MULTI-REPOSITORY SYNCHRONIZATION")
#     print("=" * 80)
#     print(f"Projects organization : {OWNER}")
#     print("Repository scope      : All repositories accessible to the GitHub App installation")
#     print(f"Default repository    : {DEFAULT_REPOSITORY}")

#     if not db.test_connection():
#         print("ERROR: MySQL connection failed. Check MYSQL_* settings in .env.")
#         return

#     repositories=discover_repositories()
#     if not repositories:
#         print("No accessible repositories were discovered.")
#         return

#     sync_id=db.begin_sync(len(repositories))
#     synced=0
#     try:
#         all_results={}
#         # Repository rows must exist before Projects V2 relationships are stored.
#         for repo in repositories:
#             repository_name=repo.get("name")
#             if not repository_name: continue
#             result=sync_one_repository(repo)
#             if result is None: continue
#             all_results[repository_name]=result
#             synced+=1
#             display_commit_report(repository_name,result["commits"])
#             display_repository_summary(repository_name,result)

#         projects=sync_projects(repositories)
#         db.finish_sync(sync_id,"SUCCESS",synced,
#                        f"Synchronized {synced}/{len(repositories)} repositories and {len(projects)} Projects V2.")

#         rows=db.repository_index_rows()
#         print("\n" + "=" * 80)
#         print("MYSQL SYNCHRONIZATION SUMMARY")
#         print("=" * 80)
#         for repo in rows:
#             print(f"{repo['name']}: {repo['commits']} commits | {repo['pull_requests']} PRs | "
#                   f"{repo['issues']} issues | {repo['branches']} branches | "
#                   f"{repo['contributors']} contributors | {repo['collaborators']} collaborators | "
#                   f"{repo['projects']} projects")
#         print("\nGITHUB DATA SYNCHRONIZATION COMPLETED")
#     except Exception as error:
#         db.finish_sync(sync_id,"FAILED",synced,f"{type(error).__name__}: {error}")
#         print(f"ERROR: Synchronization failed: {error}")
#         raise

# if __name__ == "__main__":
#     main()






import json
import os
import shutil
import time
from pathlib import Path

import jwt
import requests
from dotenv import load_dotenv
import database as db

BASE_DIR = Path(__file__).resolve().parent
DATA_FOLDER = BASE_DIR / "data"
REPOSITORIES_FOLDER = DATA_FOLDER / "repositories"
REPOSITORY_INDEX_FILE = DATA_FOLDER / "repository_index.json"

load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# GitHub App authentication
# ---------------------------------------------------------------------------
# The application now authenticates with a GitHub App installation token
# instead of a Personal Access Token. The installation token is generated
# automatically from the App ID + private key and refreshed when it is close
# to expiry.

GITHUB_APP_ID = (
    os.getenv("GITHUB_APP_ID")
    or os.getenv("GITHUB_APP_ID_NUMBER")
)

# Primary organization used for reporting/classification.
# Repository discovery itself is NOT restricted to this owner;
# all GitHub App installations are discovered dynamically.
OWNER = (
    os.getenv("GITHUB_OWNER")
    or os.getenv("GITHUB_ORGANIZATION")
    or "ICPOC1"
)


DEFAULT_REPOSITORY = os.getenv(
    "GITHUB_DEFAULT_REPOSITORY",
    ""
)

GITHUB_APP_INSTALLATION_ID = (
    os.getenv("GITHUB_APP_INSTALLATION_ID")
    or os.getenv("GITHUB_INSTALLATION_ID")
)

GITHUB_APP_PRIVATE_KEY_PATH = os.getenv(
    "GITHUB_APP_PRIVATE_KEY_PATH"
)

GITHUB_APP_PRIVATE_KEY = os.getenv(
    "GITHUB_APP_PRIVATE_KEY",
    ""
)


if not GITHUB_APP_ID:
    print("=" * 80)
    print("ERROR: GITHUB_APP_ID was not found.")
    print("Please check your .env file.")
    print("=" * 80)
    raise SystemExit(1)

if not GITHUB_APP_PRIVATE_KEY_PATH and not GITHUB_APP_PRIVATE_KEY:
    print("=" * 80)
    print("ERROR: GitHub App private key was not found.")
    print("Set GITHUB_APP_PRIVATE_KEY_PATH or GITHUB_APP_PRIVATE_KEY in .env.")
    print("=" * 80)
    raise SystemExit(1)

DATA_FOLDER.mkdir(parents=True, exist_ok=True)
REPOSITORIES_FOLDER.mkdir(parents=True, exist_ok=True)

API_ROOT = "https://api.github.com"
GITHUB_API_VERSION = "2026-03-10"

# Multiple GitHub App installations can use the same App ID/private key.
# The active installation is switched automatically before each repository
# synchronization.
ACTIVE_INSTALLATION_ID = None
_INSTALLATION_TOKENS = {}
_INSTALLATION_TOKEN_EXPIRES_AT = {}


def _load_github_app_private_key():
    """Load the GitHub App private key from a file or .env value."""
    if GITHUB_APP_PRIVATE_KEY_PATH:
        key_path = Path(GITHUB_APP_PRIVATE_KEY_PATH)
        if not key_path.is_absolute():
            key_path = BASE_DIR / key_path
        try:
            return key_path.read_text(encoding="utf-8")
        except OSError as error:
            raise RuntimeError(
                f"Could not read GitHub App private key file: {key_path}\n{error}"
            ) from error

    return GITHUB_APP_PRIVATE_KEY.replace("\\n", "\n")


def _create_github_app_jwt():
    """Create the short-lived JWT used to request installation tokens."""
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 540,
        "iss": GITHUB_APP_ID,
    }
    return jwt.encode(
        payload,
        _load_github_app_private_key(),
        algorithm="RS256",
    )


def _request_installation_token(installation_id, force_refresh=False):
    """Generate/cache an installation token for a specific GitHub App installation."""
    installation_id = int(installation_id)
    now = int(time.time())

    cached_token = _INSTALLATION_TOKENS.get(installation_id)
    expires_at = _INSTALLATION_TOKEN_EXPIRES_AT.get(installation_id, 0)

    if (
        not force_refresh
        and cached_token
        and now < expires_at - 300
    ):
        return cached_token

    app_jwt = _create_github_app_jwt()
    response = requests.post(
        f"{API_ROOT}/app/installations/{installation_id}/access_tokens",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {app_jwt}",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
        },
        timeout=30,
    )

    if response.status_code != 201:
        try:
            details = json.dumps(response.json(), indent=2)
        except ValueError:
            details = response.text
        raise RuntimeError(
            f"GitHub App installation-token request failed for installation "
            f"{installation_id} ({response.status_code}):\n{details}"
        )

    data = response.json()
    token = data.get("token")
    expires_at_text = data.get("expires_at")

    if not token:
        raise RuntimeError(
            f"GitHub did not return an installation token for installation {installation_id}."
        )

    _INSTALLATION_TOKENS[installation_id] = token

    if expires_at_text:
        try:
            from datetime import datetime
            _INSTALLATION_TOKEN_EXPIRES_AT[installation_id] = int(
                datetime.fromisoformat(
                    expires_at_text.replace("Z", "+00:00")
                ).timestamp()
            )
        except (ValueError, TypeError):
            _INSTALLATION_TOKEN_EXPIRES_AT[installation_id] = now + 3600
    else:
        _INSTALLATION_TOKEN_EXPIRES_AT[installation_id] = now + 3600

    print(
        "GitHub App installation token generated successfully "
        f"for installation {installation_id} "
        f"(expires: {expires_at_text or 'unknown'})."
    )
    return token


def set_active_installation(installation_id):
    """Make one GitHub App installation the active API identity."""
    global ACTIVE_INSTALLATION_ID
    if installation_id is None:
        raise RuntimeError("No GitHub App installation ID was supplied.")
    ACTIVE_INSTALLATION_ID = int(installation_id)
    _request_installation_token(ACTIVE_INSTALLATION_ID)


def github_headers(force_refresh=False, installation_id=None):
    """Return headers for the selected GitHub App installation."""
    installation_id = (
        installation_id
        or ACTIVE_INSTALLATION_ID
        or GITHUB_APP_INSTALLATION_ID
    )
    if not installation_id:
        raise RuntimeError(
            "No active GitHub App installation ID is available. "
            "The application must discover at least one installation."
        )

    token = _request_installation_token(
        installation_id,
        force_refresh=force_refresh,
    )
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }


def get_app_installations():
    """Discover every installation of this GitHub App."""
    app_jwt = _create_github_app_jwt()
    installations = []

    for page in range(1, 101):
        response = requests.get(
            f"{API_ROOT}/app/installations",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {app_jwt}",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
            params={"per_page": 100, "page": page},
            timeout=30,
        )

        if response.status_code != 200:
            try:
                details = json.dumps(response.json(), indent=2)
            except ValueError:
                details = response.text
            raise RuntimeError(
                f"Unable to retrieve GitHub App installations "
                f"({response.status_code}):\n{details}"
            )

        page_items = response.json()
        if not isinstance(page_items, list) or not page_items:
            break

        installations.extend(page_items)

        if len(page_items) < 100:
            break

    result = []
    for installation in installations:
        account = installation.get("account") or {}
        result.append({
            "installation_id": installation.get("id"),
            "account_login": account.get("login"),
            "account_type": account.get("type"),
            "repository_selection": installation.get(
                "repository_selection", "all"
            ),
        })

    return result


def get_installation_repositories(installation):
    """Retrieve all repositories available through one installation."""
    installation_id = int(installation["installation_id"])
    token = _request_installation_token(installation_id)
    repositories = []

    for page in range(1, 101):
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
        }
        response = requests.get(
            f"{API_ROOT}/installation/repositories",
            headers=headers,
            params={"per_page": 100, "page": page},
            timeout=30,
        )

        if response.status_code == 401:
            token = _request_installation_token(
                installation_id,
                force_refresh=True,
            )
            headers["Authorization"] = f"Bearer {token}"
            response = requests.get(
                f"{API_ROOT}/installation/repositories",
                headers=headers,
                params={"per_page": 100, "page": page},
                timeout=30,
            )

        if response.status_code != 200:
            try:
                details = json.dumps(response.json(), indent=2)
            except ValueError:
                details = response.text
            raise RuntimeError(
                f"Unable to retrieve repositories for installation "
                f"{installation_id} ({response.status_code}):\n{details}"
            )

        payload = response.json()
        page_items = payload.get("repositories", [])
        if not page_items:
            break

        repositories.extend(page_items)

        if len(page_items) < 100:
            break

    return repositories


# Live headers are generated on demand. These constants are retained for
# compatibility with older code that imports them.
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": GITHUB_API_VERSION,
}
PROJECT_HEADERS = HEADERS.copy()

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
            headers=github_headers(),
            params=params,
            timeout=timeout,
        )
        if response.status_code == 401:
            response = requests.get(
                url,
                headers=github_headers(force_refresh=True),
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
    Discover repositories from every installation of this GitHub App.

    This includes organization repositories and repositories owned by the
    installed user account. Each repository remembers the installation that
    grants access so later API calls use the correct installation token.
    """
    global REPOSITORY_REGISTRY

    print("=" * 80)
    print("REPOSITORY DISCOVERY")
    print("=" * 80)
    print(
        "Repository scope       : "
        "All repositories accessible to all GitHub App installations"
    )

    installations = get_app_installations()
    if not installations:
        print("WARNING: No GitHub App installations found.")
        return []

    discovered = {}
    print(f"GitHub App installations discovered: {len(installations)}")

    for installation in installations:
        installation_id = installation.get("installation_id")
        account_login = installation.get("account_login")
        account_type = installation.get("account_type")

        print()
        print(
            f"Installation {installation_id}: "
            f"{account_login} ({account_type})"
        )

        repos = get_installation_repositories(installation)
        print(f"Repositories found: {len(repos)}")

        for repo in repos:
            record = normalize_repository_record(repo)
            if not record.get("name") or not record.get("owner"):
                continue

            full_name = record.get("full_name")
            record["installation_id"] = installation_id
            record["installation_account"] = account_login
            record["installation_account_type"] = account_type
            record["repository_scope"] = (
                "Organization"
                if account_type == "Organization"
                else "Outside Organization"
            )

            discovered[str(full_name).lower()] = record
            print(
                f"  - {full_name} "
                f"[{record['repository_scope']}]"
            )

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

    # Persist a lightweight repository index for compatibility with the
    # existing dashboard and older tooling.
    save_json_file(
        REPOSITORY_INDEX_FILE,
        {
            "repositories": [
                {
                    "id": repo.get("id"),
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "owner": repo.get("owner"),
                    "installation_id": repo.get("installation_id"),
                    "installation_account": repo.get("installation_account"),
                    "repository_scope": repo.get("repository_scope"),
                }
                for repo in repositories
            ]
        },
    )

    print()
    print(f"TOTAL REPOSITORIES DISCOVERED: {len(repositories)}")

    if not repositories:
        print(
            "WARNING: No repositories are accessible "
            "through the GitHub App."
        )

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

    url = f"{API_ROOT}/repos/{repository_api_path(repository_name)}/commits"
    github_commits = github_get_all(url)
    if github_commits is None:
        print("Unable to retrieve commits.")
        repository_id = db.repository_id_by_name(repository_name)
        return db.get_repository_commits(repository_id) if repository_id else []

    formatted=[]
    for commit in github_commits:
        sha=commit.get("sha")
        if not sha:
            continue
        detailed_record=build_commit_record(repository_name, commit)
        if detailed_record:
            formatted.append(detailed_record)

    repository_id=db.repository_id_by_name(repository_name)
    if repository_id is None:
        raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
    db.sync_commits(repository_id, formatted)
    print(f"Commits synchronized to MySQL: {len(formatted)}")
    return formatted

def sync_pull_requests(repository_name):
    print("\n" + "=" * 80)
    print(f"PULL REQUEST SYNCHRONIZATION: {repository_name}")
    print("=" * 80)
    url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}/pulls"
    pull_requests=github_get_all(url, params={"state":"all","sort":"updated","direction":"desc"})
    if pull_requests is None:
        return []
    formatted=[]
    for pr in pull_requests:
        user=pr.get("user") or {}; head=pr.get("head") or {}; base=pr.get("base") or {}
        formatted.append({
            "number":pr.get("number"), "title":pr.get("title","No title"),
            "state":pr.get("state","unknown"), "draft":bool(pr.get("draft",False)),
            "merged":pr.get("merged_at") is not None, "author":user.get("login","Unknown"),
            "author_url":user.get("html_url",""), "created_at":pr.get("created_at"),
            "updated_at":pr.get("updated_at"), "closed_at":pr.get("closed_at"),
            "merged_at":pr.get("merged_at"), "url":pr.get("html_url",""),
            "head_branch":head.get("ref",""), "base_branch":base.get("ref","")})
    repository_id=db.repository_id_by_name(repository_name)
    if repository_id is None: raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
    db.sync_pull_requests(repository_id, formatted)
    print(f"Pull requests synchronized to MySQL: {len(formatted)}")
    return formatted

def sync_issues(repository_name):
    print("\n" + "=" * 80)
    print(f"ISSUE SYNCHRONIZATION: {repository_name}")
    print("=" * 80)
    url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}/issues"
    issues=github_get_all(url, params={"state":"all","sort":"updated","direction":"desc"})
    if issues is None: return []
    formatted=[]
    for issue in issues:
        if "pull_request" in issue: continue
        user=issue.get("user") or {}
        labels=[label.get("name","") for label in issue.get("labels",[]) or []]
        formatted.append({
            "number":issue.get("number"), "title":issue.get("title","No title"),
            "state":issue.get("state","unknown"), "author":user.get("login","Unknown"),
            "author_url":user.get("html_url",""), "created_at":issue.get("created_at"),
            "updated_at":issue.get("updated_at"), "closed_at":issue.get("closed_at"),
            "comments":int(issue.get("comments",0) or 0), "labels":labels,
            "url":issue.get("html_url","")})
    repository_id=db.repository_id_by_name(repository_name)
    if repository_id is None: raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
    db.sync_issues(repository_id, formatted)
    print(f"Issues synchronized to MySQL: {len(formatted)}")
    return formatted

def sync_branches(repository_name, repository_info):
    print("\n" + "=" * 80)
    print(f"BRANCH SYNCHRONIZATION: {repository_name}")
    print("=" * 80)
    url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}/branches"
    branches=github_get_all(url)
    if branches is None: return []
    default_branch=repository_info.get("default_branch","") if repository_info else ""
    formatted=[]
    for branch in branches:
        branch_name=branch.get("name","Unknown"); commit_data=branch.get("commit") or {}
        formatted.append({"name":branch_name,"default":branch_name==default_branch,
                          "protected":bool(branch.get("protected",False)),"commit_sha":commit_data.get("sha","")})
    repository_id=db.repository_id_by_name(repository_name)
    if repository_id is None: raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
    db.sync_branches(repository_id, formatted)
    print(f"Branches synchronized to MySQL: {len(formatted)}")
    return formatted

def sync_repository_info(repository_name):
    url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}"
    repository_info=github_get(url)
    if repository_info is None: return None
    owner_data=repository_info.get("owner") or {}
    owner=owner_data.get("login") if isinstance(owner_data,dict) else owner_data
    formatted={
        "id":repository_info.get("id"), "name":repository_info.get("name",repository_name),
        "full_name":repository_info.get("full_name",repository_full_name(repository_name)),
        "owner":owner or repository_owner(repository_name), "description":repository_info.get("description"),
        "private":repository_info.get("private",False), "visibility":repository_info.get("visibility","unknown"),
        "default_branch":repository_info.get("default_branch","main"), "html_url":repository_info.get("html_url",""),
        "clone_url":repository_info.get("clone_url",""), "ssh_url":repository_info.get("ssh_url",""),
        "language":repository_info.get("language"), "created_at":repository_info.get("created_at"),
        "updated_at":repository_info.get("updated_at"), "pushed_at":repository_info.get("pushed_at"),
        "size":repository_info.get("size",0), "stars":repository_info.get("stargazers_count",0),
        "forks":repository_info.get("forks_count",0), "open_issues":repository_info.get("open_issues_count",0),
        "watchers":repository_info.get("watchers_count",0), "archived":repository_info.get("archived",False),
        "disabled":repository_info.get("disabled",False)}
    db.upsert_repository(formatted)
    register_repository(formatted)
    return formatted

def sync_contributors(repository_name):
    url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}/contributors"
    contributors=github_get_all(url)
    if contributors is None: return []
    formatted=[{"login":c.get("login","Unknown"),"id":c.get("id"),"contributions":int(c.get("contributions",0) or 0),
                "type":c.get("type","User"),"profile_url":c.get("html_url",""),"avatar_url":c.get("avatar_url","")}
               for c in contributors]
    repository_id=db.repository_id_by_name(repository_name)
    if repository_id is None: raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
    db.sync_contributors(repository_id, formatted)
    print(f"Contributors synchronized to MySQL: {len(formatted)}")
    return formatted

def sync_collaborators(repository_name):
    print("\n" + "=" * 80)
    print(f"COLLABORATOR / ACCESS SYNCHRONIZATION: {repository_name}")
    print("=" * 80)
    url=f"{API_ROOT}/repos/{repository_api_path(repository_name)}/collaborators"
    collaborators=github_get_all(url, params={"affiliation":"all"})
    if collaborators is None:
        print("Collaborators could not be retrieved. The token may not have permission to read collaborator data.")
        return []
    formatted=[]
    for collaborator in collaborators:
        permissions=collaborator.get("permissions") or {}
        formatted.append({"login":collaborator.get("login","Unknown"),"id":collaborator.get("id"),
                          "type":collaborator.get("type","User"),"role_name":collaborator.get("role_name","Unknown"),
                          "admin":bool(permissions.get("admin",False)),"maintain":bool(permissions.get("maintain",False)),
                          "push":bool(permissions.get("push",False)),"triage":bool(permissions.get("triage",False)),
                          "pull":bool(permissions.get("pull",False)),"profile_url":collaborator.get("html_url","")})
    repository_id=db.repository_id_by_name(repository_name)
    if repository_id is None: raise RuntimeError(f"Repository {repository_name!r} is not present in MySQL")
    db.sync_collaborators(repository_id, formatted)
    print(f"Collaborators synchronized to MySQL: {len(formatted)}")
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
            headers=github_headers(),
            json={
                "query": query,
                "variables": variables or {},
            },
            timeout=30,
        )
        if response.status_code == 401:
            response = requests.post(
                f"{API_ROOT}/graphql",
                headers=github_headers(force_refresh=True),
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
                headers=github_headers(),
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
            db.replace_projects(OWNER, [])
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

    db.replace_projects(OWNER, projects)

    # MySQL stores project-to-repository relationships centrally; no local JSON
    # project copies are required in the production application.
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
    """Synchronize every repository feature using its installation token."""
    repository_name = repository.get("name")
    full_name = (
        repository.get("full_name")
        or repository_full_name(repository_name)
    )
    installation_id = repository.get("installation_id")

    if not installation_id:
        raise RuntimeError(
            f"No GitHub App installation ID recorded for {full_name}."
        )

    print("\n" + "=" * 80)
    print(f"SYNCHRONIZING REPOSITORY: {full_name}")
    print("=" * 80)
    print(f"Installation ID     : {installation_id}")
    print(
        f"Installation account: "
        f"{repository.get('installation_account')}"
    )
    print(
        f"Repository scope    : "
        f"{repository.get('repository_scope')}"
    )

    set_active_installation(installation_id)
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

    result = {
        "repository": repository_info,
        "commits": commits,
        "pull_requests": pull_requests,
        "issues": issues,
        "branches": branches,
        "contributors": contributors,
        "collaborators": collaborators,
    }

    # Keep the JSON mirror because the existing Streamlit dashboard reads the
    # per-repository JSON files. MySQL remains the authoritative database.
    files = repository_files(repository_name)
    save_json_file(files["repository"], repository_info)
    save_json_file(files["commits"], {"commits": commits})
    save_json_file(files["pull_requests"], {"pull_requests": pull_requests})
    save_json_file(files["issues"], {"issues": issues})
    save_json_file(files["branches"], {"branches": branches})
    save_json_file(files["contributors"], {"contributors": contributors})
    save_json_file(files["collaborators"], {"collaborators": collaborators})

    return result


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
    return db.count_projects_for_repository(repository_name)

def main():
    print("\n" + "=" * 80)
    print("GITHUB USAGE & ACCESS REPORTING SYSTEM")
    print("MYSQL-BACKED MULTI-REPOSITORY SYNCHRONIZATION")
    print("=" * 80)
    print(f"Projects organization : {OWNER}")
    print(
        "Repository scope      : "
        "All repositories accessible to all GitHub App installations"
    )
    print(f"Default repository    : {DEFAULT_REPOSITORY}")

    if not db.test_connection():
        print("ERROR: MySQL connection failed. Check MYSQL_* settings in .env.")
        return

    installations = get_app_installations()
    if not installations:
        print("No GitHub App installations were discovered.")
        return

    repositories = discover_repositories()
    if not repositories:
        print("No accessible repositories were discovered.")
        return

    sync_id = db.begin_sync(len(repositories))
    synced = 0

    try:
        all_results = {}

        # Repository rows must exist before Projects V2 relationships are stored.
        for repo in repositories:
            repository_name = repo.get("name")
            if not repository_name:
                continue

            result = sync_one_repository(repo)
            if result is None:
                continue

            all_results[repository_name] = result
            synced += 1
            display_commit_report(repository_name, result["commits"])
            display_repository_summary(repository_name, result)

        # Projects V2 belongs to the ICPOC1 organization. Explicitly switch
        # back to that organization's installation before querying GraphQL.
        organization_installation = next(
            (
                item for item in installations
                if str(item.get("account_login", "")).lower()
                == str(OWNER).lower()
                and str(item.get("account_type", "")).lower()
                == "organization"
            ),
            None,
        )

        if organization_installation:
            set_active_installation(
                organization_installation["installation_id"]
            )
            projects = sync_projects(repositories)
        else:
            print(
                f"WARNING: No organization installation found for {OWNER}. "
                "Projects V2 synchronization skipped."
            )
            projects = []

        # Mirror Projects V2 into each repository JSON folder for the existing
        # dashboard. The dashboard performs its own repository-level filtering.
        for repo in repositories:
            repo_name = repo.get("name")
            if repo_name:
                files = repository_files(repo_name)
                save_json_file(
                    files["projects"],
                    {"projects": projects},
                )

        db.finish_sync(
            sync_id,
            "SUCCESS",
            synced,
            f"Synchronized {synced}/{len(repositories)} repositories "
            f"and {len(projects)} Projects V2.",
        )

        rows = db.repository_index_rows()
        print("\n" + "=" * 80)
        print("MYSQL SYNCHRONIZATION SUMMARY")
        print("=" * 80)

        for repo in rows:
            print(
                f"{repo['full_name']}: "
                f"{repo['commits']} commits | "
                f"{repo['pull_requests']} PRs | "
                f"{repo['issues']} issues | "
                f"{repo['branches']} branches | "
                f"{repo['contributors']} contributors | "
                f"{repo['collaborators']} collaborators | "
                f"{repo['projects']} projects"
            )

        print("\nGITHUB DATA SYNCHRONIZATION COMPLETED")

    except Exception as error:
        db.finish_sync(
            sync_id,
            "FAILED",
            synced,
            f"{type(error).__name__}: {error}",
        )
        print(f"ERROR: Synchronization failed: {error}")
        raise

if __name__ == "__main__":
    main()
