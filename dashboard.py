





# import json
# import io
# import os
# import subprocess
# import sys
# from pathlib import Path
# from datetime import datetime

# import pandas as pd
# import plotly.express as px
# import requests
# import streamlit as st
# from dotenv import load_dotenv


# # ============================================================
# # GitHub Usage & Access Reporting System
# # Professional Dashboard
# # ============================================================


# # ============================================================
# # 1. BASE CONFIGURATION
# # ============================================================

# BASE_DIR = Path(__file__).resolve().parent

# # Phase 1: Incepteo Labs corporate branding asset
# LOGO_PATH = BASE_DIR / "assets" / "incepteo_labs_logo.png"

# DATA_DIR = BASE_DIR / "data"

# COMMITS_FILE = DATA_DIR / "commits.json"
# PULL_REQUESTS_FILE = DATA_DIR / "pull_requests.json"
# ISSUES_FILE = DATA_DIR / "issues.json"
# BRANCHES_FILE = DATA_DIR / "branches.json"
# REPOSITORY_FILE = DATA_DIR / "repository.json"
# CONTRIBUTORS_FILE = DATA_DIR / "contributors.json"
# COLLABORATORS_FILE = DATA_DIR / "collaborators.json"


# load_dotenv(BASE_DIR / ".env")


# REPO_OWNER = os.getenv(
#     "GITHUB_REPO_OWNER",
#     "PraharshaIncepteolabs"
# )

# REPO_NAME = os.getenv(
#     "GITHUB_REPO_NAME",
#     "TEST"
# )

# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# GITHUB_API = "https://api.github.com"


# GITHUB_HEADERS = {
#     "Accept": "application/vnd.github+json",
#     "X-GitHub-Api-Version": "2026-03-10"
# }


# if GITHUB_TOKEN:
#     GITHUB_HEADERS["Authorization"] = (
#         f"Bearer {GITHUB_TOKEN}"
#     )


# # ============================================================
# # 2. STREAMLIT PAGE CONFIGURATION
# # ============================================================

# st.set_page_config(
#     page_title="GitHub Usage & Access Reporting",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )


# # ============================================================
# # 3. CUSTOM CSS
# # ============================================================

# st.markdown(
#     """
#     <style>

#     /* Phase 1: Corporate brand header */

#     .brand-content {
#         flex: 1;
#     }

#     /* Main title */

#     .main-title {
#         font-size: 38px;
#         font-weight: 700;
#         margin-bottom: 4px;
#     }


#     .subtitle {
#         color: #6b7280;
#         font-size: 16px;
#         margin-bottom: 18px;
#     }


#     /* Repository box */

#     .repo-box {
#         padding: 15px 20px;
#         border-radius: 10px;
#         background-color: #eef5ff;
#         border: 1px solid #dbeafe;
#         margin-bottom: 20px;
#         font-size: 17px;
#         color: #1f2937 !important;
#     }


#     /* Section headings */

#     .section-title {
#         font-size: 25px;
#         font-weight: 650;
#         margin-top: 10px;
#         margin-bottom: 12px;
#     }


#     /* Small information cards */

#     .info-card {
#         padding: 15px;
#         border-radius: 10px;
#         border: 1px solid #e5e7eb;
#         background-color: #ffffff;
#         margin-bottom: 10px;
#     }


#     /* Hide unnecessary Streamlit footer */

#     footer {
#         visibility: hidden;
#     }


#     /* Better dataframe appearance */

#     [data-testid="stDataFrame"] {
#         width: 100%;
#     }


#     </style>
#     """,
#     unsafe_allow_html=True
# )


# # ============================================================
# # 4. PLOTLY CONFIGURATION
# # ============================================================

# # Important:
# # scrollZoom=False prevents mouse-wheel scrolling over a chart
# # from zooming the graph.

# PLOTLY_CONFIG = {
#     "scrollZoom": False,
#     "displayModeBar": False,
#     "doubleClick": False,
#     "showTips": False,
#     "responsive": True
# }


# COMMON_LAYOUT = {
#     "dragmode": False,
#     "hovermode": "closest",
#     "margin": {
#         "l": 30,
#         "r": 20,
#         "t": 45,
#         "b": 40
#     },
#     "height": 400
# }


# # ============================================================
# # 5. GENERIC JSON LOADER
# # ============================================================

# def load_json_file(file_path, default=None):

#     if default is None:
#         default = {}

#     if not file_path.exists():
#         return default

#     try:

#         with open(
#             file_path,
#             "r",
#             encoding="utf-8"
#         ) as file:

#             data = json.load(file)

#         return data

#     except (
#         json.JSONDecodeError,
#         OSError,
#         TypeError
#     ):

#         return default


# # ============================================================
# # 6. LOAD COMMITS
# # ============================================================

# @st.cache_data(ttl=60)
# def load_commits():

#     data = load_json_file(
#         COMMITS_FILE,
#         {"commits": []}
#     )

#     if isinstance(data, dict):

#         commits = data.get(
#             "commits",
#             []
#         )

#         if isinstance(commits, list):
#             return commits

#     return []


# # ============================================================
# # 7. LOAD PULL REQUESTS
# # ============================================================

# @st.cache_data(ttl=60)
# def load_pull_requests():

#     data = load_json_file(
#         PULL_REQUESTS_FILE,
#         {"pull_requests": []}
#     )

#     if isinstance(data, dict):

#         prs = data.get(
#             "pull_requests",
#             []
#         )

#         if isinstance(prs, list):
#             return prs

#     if isinstance(data, list):
#         return data

#     return []


# # ============================================================
# # 8. LOAD ISSUES
# # ============================================================

# @st.cache_data(ttl=60)
# def load_issues():

#     data = load_json_file(
#         ISSUES_FILE,
#         {"issues": []}
#     )

#     if isinstance(data, dict):

#         issues = data.get(
#             "issues",
#             []
#         )

#         if isinstance(issues, list):
#             return issues

#     if isinstance(data, list):
#         return data

#     return []


# # ============================================================
# # 9. LOAD BRANCHES
# # ============================================================

# @st.cache_data(ttl=60)
# def load_branches():

#     data = load_json_file(
#         BRANCHES_FILE,
#         {"branches": []}
#     )

#     if isinstance(data, dict):

#         branches = data.get(
#             "branches",
#             []
#         )

#         if isinstance(branches, list):
#             return branches

#     if isinstance(data, list):
#         return data

#     return []


# # ============================================================
# # 10. LOAD REPOSITORY
# # ============================================================

# @st.cache_data(ttl=60)
# def load_repository():

#     data = load_json_file(
#         REPOSITORY_FILE,
#         {}
#     )

#     if isinstance(data, dict):
#         return data

#     return {}


# # ============================================================
# # 11. LOAD CONTRIBUTORS
# # ============================================================

# @st.cache_data(ttl=60)
# def load_contributors():

#     data = load_json_file(
#         CONTRIBUTORS_FILE,
#         {"contributors": []}
#     )

#     if isinstance(data, dict):

#         contributors = data.get(
#             "contributors",
#             []
#         )

#         if isinstance(contributors, list):
#             return contributors

#     if isinstance(data, list):
#         return data

#     return []


# # ============================================================
# # 12. LOAD COLLABORATORS
# # ============================================================

# @st.cache_data(ttl=60)
# def load_collaborators():

#     data = load_json_file(
#         COLLABORATORS_FILE,
#         {"collaborators": []}
#     )

#     if isinstance(data, dict):

#         collaborators = data.get(
#             "collaborators",
#             []
#         )

#         if isinstance(collaborators, list):
#             return collaborators

#     if isinstance(data, list):
#         return data

#     return []


# # ============================================================
# # 13. SYNC WITH GITHUB
# # ============================================================

# def sync_github_data():

#     try:

#         result = subprocess.run(
#             [
#                 sys.executable,
#                 str(BASE_DIR / "app.py")
#             ],
#             cwd=BASE_DIR,
#             capture_output=True,
#             text=True,
#             timeout=180
#         )

#         if result.returncode == 0:

#             return True, result.stdout

#         return False, (
#             result.stderr
#             or result.stdout
#             or "Unknown synchronization error."
#         )

#     except subprocess.TimeoutExpired:

#         return False, (
#             "GitHub synchronization timed out."
#         )

#     except Exception as error:

#         return False, str(error)


# # ============================================================
# # 14. COMMIT DATAFRAME
# # ============================================================

# def commits_to_dataframe(commits):

#     rows = []

#     for commit in commits:

#         author = commit.get(
#             "author",
#             {}
#         )

#         statistics = commit.get(
#             "statistics",
#             {}
#         )

#         date_value = commit.get(
#             "date"
#         )

#         parsed_date = pd.to_datetime(
#             date_value,
#             errors="coerce",
#             utc=True
#         )

#         additions = int(
#             statistics.get(
#                 "additions",
#                 0
#             )
#             or 0
#         )

#         deletions = int(
#             statistics.get(
#                 "deletions",
#                 0
#             )
#             or 0
#         )

#         changes = statistics.get(
#             "total_changes"
#         )

#         if changes is None:
#             changes = additions + deletions

#         files = commit.get(
#             "files",
#             []
#         )

#         rows.append(
#             {
#                 "SHA": commit.get(
#                     "sha",
#                     ""
#                 ),

#                 "Developer": author.get(
#                     "name",
#                     "Unknown"
#                 ),

#                 "Email": author.get(
#                     "email",
#                     "Unknown"
#                 ),

#                 "Date": parsed_date,

#                 "Message": commit.get(
#                     "message",
#                     "No commit message"
#                 ),

#                 "Additions": additions,

#                 "Deletions": deletions,

#                 "Changes": int(changes or 0),

#                 "Files Changed": len(files)
#             }
#         )

#     return pd.DataFrame(rows)


# # ============================================================
# # 15. PULL REQUEST DATAFRAME
# # ============================================================

# def pull_requests_to_dataframe(pull_requests):

#     rows = []

#     for pr in pull_requests:

#         user = pr.get(
#             "user",
#             {}
#         )

#         if not isinstance(user, dict):
#             user = {}

#         state = pr.get(
#             "state",
#             "unknown"
#         )

#         created = pr.get(
#             "created_at",
#             pr.get(
#                 "created",
#                 None
#             )
#         )

#         updated = pr.get(
#             "updated_at",
#             pr.get(
#                 "updated",
#                 None
#             )
#         )

#         merged = pr.get(
#             "merged_at",
#             None
#         )

#         rows.append(
#             {
#                 "Number": pr.get(
#                     "number",
#                     ""
#                 ),

#                 "Title": pr.get(
#                     "title",
#                     "Untitled"
#                 ),

#                 "Author": user.get(
#                     "login",
#                     pr.get(
#                         "author",
#                         "Unknown"
#                     )
#                 ),

#                 "State": state,

#                 "Created": pd.to_datetime(
#                     created,
#                     errors="coerce",
#                     utc=True
#                 ),

#                 "Updated": pd.to_datetime(
#                     updated,
#                     errors="coerce",
#                     utc=True
#                 ),

#                 "Merged": pd.to_datetime(
#                     merged,
#                     errors="coerce",
#                     utc=True
#                 ),

#                 "URL": pr.get(
#                     "html_url",
#                     pr.get(
#                         "url",
#                         ""
#                     )
#                 )
#             }
#         )

#     return pd.DataFrame(rows)


# # ============================================================
# # 16. ISSUE DATAFRAME
# # ============================================================

# def issues_to_dataframe(issues):

#     rows = []

#     for issue in issues:

#         # GitHub pull requests can sometimes appear
#         # in issue results. Exclude them if detected.

#         if "pull_request" in issue:
#             continue

#         user = issue.get(
#             "user",
#             {}
#         )

#         if not isinstance(user, dict):
#             user = {}

#         labels = issue.get(
#             "labels",
#             []
#         )

#         label_names = []

#         if isinstance(labels, list):

#             for label in labels:

#                 if isinstance(label, dict):

#                     label_names.append(
#                         label.get(
#                             "name",
#                             ""
#                         )
#                     )

#                 elif isinstance(label, str):

#                     label_names.append(label)

#         rows.append(
#             {
#                 "Number": issue.get(
#                     "number",
#                     ""
#                 ),

#                 "Title": issue.get(
#                     "title",
#                     "Untitled"
#                 ),

#                 "Author": user.get(
#                     "login",
#                     issue.get(
#                         "author",
#                         "Unknown"
#                     )
#                 ),

#                 "State": issue.get(
#                     "state",
#                     "unknown"
#                 ),

#                 "Created": pd.to_datetime(
#                     issue.get(
#                         "created_at"
#                     ),
#                     errors="coerce",
#                     utc=True
#                 ),

#                 "Updated": pd.to_datetime(
#                     issue.get(
#                         "updated_at"
#                     ),
#                     errors="coerce",
#                     utc=True
#                 ),

#                 "Labels": ", ".join(
#                     label_names
#                 ),

#                 "URL": issue.get(
#                     "html_url",
#                     issue.get(
#                         "url",
#                         ""
#                     )
#                 )
#             }
#         )

#     return pd.DataFrame(rows)


# # ============================================================
# # 17. BRANCH DATAFRAME
# # ============================================================

# def branches_to_dataframe(branches):

#     rows = []

#     for branch in branches:

#         commit_data = branch.get(
#             "commit",
#             {}
#         )

#         if not isinstance(commit_data, dict):
#             commit_data = {}

#         rows.append(
#             {
#                 "Branch": branch.get(
#                     "name",
#                     "Unknown"
#                 ),

#                 "Protected": branch.get(
#                     "protected",
#                     False
#                 ),

#                 "Commit SHA": commit_data.get(
#                     "sha",
#                     branch.get(
#                         "sha",
#                         ""
#                     )
#                 )
#             }
#         )

#     return pd.DataFrame(rows)


# # ============================================================
# # 18. DEVELOPER REPORT
# # ============================================================

# def developer_report(df):

#     if df.empty:
#         return pd.DataFrame()

#     result = (
#         df.groupby(
#             [
#                 "Developer",
#                 "Email"
#             ],
#             as_index=False
#         )
#         .agg(
#             {
#                 "SHA": "count",
#                 "Additions": "sum",
#                 "Deletions": "sum",
#                 "Changes": "sum",
#                 "Files Changed": "sum",
#                 "Date": "max"
#             }
#         )
#     )

#     result.rename(
#         columns={
#             "SHA": "Commits",
#             "Date": "Last Activity"
#         },
#         inplace=True
#     )

#     result = result.sort_values(
#         "Commits",
#         ascending=False
#     )

#     return result


# # ============================================================
# # 19. FILE ACTIVITY REPORT
# # ============================================================

# def file_report(commits):

#     files = {}

#     for commit in commits:

#         developer = (
#             commit
#             .get(
#                 "author",
#                 {}
#             )
#             .get(
#                 "name",
#                 "Unknown"
#             )
#         )

#         for file_info in commit.get(
#             "files",
#             []
#         ):

#             filename = file_info.get(
#                 "filename",
#                 "Unknown"
#             )

#             if filename not in files:

#                 files[filename] = {
#                     "File": filename,
#                     "Commits": 0,
#                     "Changes": 0,
#                     "Additions": 0,
#                     "Deletions": 0,
#                     "Developers": set()
#                 }

#             files[filename]["Commits"] += 1

#             files[filename]["Changes"] += int(
#                 file_info.get(
#                     "changes",
#                     0
#                 )
#                 or 0
#             )

#             files[filename]["Additions"] += int(
#                 file_info.get(
#                     "additions",
#                     0
#                 )
#                 or 0
#             )

#             files[filename]["Deletions"] += int(
#                 file_info.get(
#                     "deletions",
#                     0
#                 )
#                 or 0
#             )

#             files[filename]["Developers"].add(
#                 developer
#             )

#     result = []

#     for data in files.values():

#         result.append(
#             {
#                 "File": data["File"],
#                 "Commits": data["Commits"],
#                 "Changes": data["Changes"],
#                 "Additions": data["Additions"],
#                 "Deletions": data["Deletions"],
#                 "Developers": ", ".join(
#                     sorted(
#                         data["Developers"]
#                     )
#                 )
#             }
#         )

#     return pd.DataFrame(result)


# # ============================================================
# # 20. COLLABORATOR PERMISSION HELPERS
# # ============================================================

# def _permission_bool(value):
#     if isinstance(value, bool):
#         return value
#     if isinstance(value, str):
#         return value.strip().lower() in {"true", "yes", "1", "write", "maintain", "admin"}
#     return bool(value)


# def get_effective_permission(user):
#     """Return the effective GitHub repository permission."""
#     role = user.get("role_name", user.get("role"))
#     if isinstance(role, str) and role.strip():
#         role = role.strip().lower()
#         mapping = {
#             "admin": "Admin",
#             "maintain": "Maintain",
#             "write": "Write",
#             "triage": "Triage",
#             "read": "Read",
#             "pull": "Read",
#         }
#         if role in mapping:
#             return mapping[role]

#     permissions = user.get("permissions", {})
#     if not isinstance(permissions, dict):
#         permissions = {}

#     if _permission_bool(permissions.get("admin")):
#         return "Admin"
#     if _permission_bool(permissions.get("maintain")):
#         return "Maintain"
#     if _permission_bool(permissions.get("push")):
#         return "Write"
#     if _permission_bool(permissions.get("triage")):
#         return "Triage"
#     if _permission_bool(permissions.get("pull")):
#         return "Read"
#     return "Unknown"


# def collaborators_to_dataframe(collaborators):
#     """
#     Convert GitHub collaborator records into a dashboard dataframe.

#     The synchronized collaborators.json produced by app.py stores the
#     permission flags at the top level:
#         admin, maintain, push, triage, pull

#     Some GitHub API responses may instead contain these values inside a
#     nested "permissions" object, so this function supports both formats.
#     """
#     rows = []

#     for user in collaborators:
#         if not isinstance(user, dict):
#             continue

#         nested_permissions = user.get("permissions", {})
#         if not isinstance(nested_permissions, dict):
#             nested_permissions = {}

#         def permission_value(name, default=False):
#             if name in user:
#                 return _permission_bool(user.get(name))
#             return _permission_bool(
#                 nested_permissions.get(name, default)
#             )

#         role = get_effective_permission(user)

#         admin = permission_value(
#             "admin",
#             role == "Admin"
#         )

#         maintain = permission_value(
#             "maintain",
#             role in {"Maintain", "Admin"}
#         )

#         write_access = permission_value(
#             "push",
#             role in {"Write", "Maintain", "Admin"}
#         )

#         triage = permission_value(
#             "triage",
#             role in {"Triage", "Write", "Maintain", "Admin"}
#         )

#         read_access = permission_value(
#             "pull",
#             role in {"Read", "Triage", "Write", "Maintain", "Admin"}
#         )

#         # app.py stores the profile as profile_url.
#         # html_url is retained as a fallback for compatibility.
#         profile_url = user.get(
#             "profile_url",
#             user.get("html_url", "")
#         )

#         rows.append({
#             "User": user.get("login", "Unknown"),
#             "Permission": role,
#             "Admin": admin,
#             "Maintain": maintain,
#             "Write": write_access,
#             "Triage": triage,
#             "Read": read_access,
#             "Profile": profile_url,
#         })

#     return pd.DataFrame(rows)


# # ============================================================
# # 21. EXCEL EXPORT HELPER
# # ============================================================

# def dataframes_to_excel(dataframes):
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine="openpyxl") as writer:
#         for sheet_name, dataframe in dataframes.items():
#             df = dataframe.copy() if isinstance(dataframe, pd.DataFrame) else pd.DataFrame()
#             for column in df.columns:
#                 if pd.api.types.is_datetime64tz_dtype(df[column]):
#                     df[column] = df[column].dt.tz_convert("UTC").dt.tz_localize(None)
#             df.to_excel(writer, sheet_name=str(sheet_name)[:31], index=False)
#     return output.getvalue()


# # ============================================================
# # SIDEBAR CONTROLS
# # ============================================================

# with st.sidebar:

#     st.header("⚙️ Controls")

#     sync_button = st.button(
#         "🔄 Sync with GitHub",
#         use_container_width=True
#     )

#     if sync_button:

#         with st.spinner(
#             "Synchronizing GitHub data..."
#         ):

#             success, output = sync_github_data()

#         if success:

#             st.success(
#                 "GitHub data synchronized successfully."
#             )

#             # Clear cached JSON data.

#             st.cache_data.clear()

#             st.rerun()

#         else:

#             st.error(
#                 "GitHub synchronization failed."
#             )

#             with st.expander(
#                 "View synchronization output"
#             ):

#                 st.code(output)

#     st.divider()

#     st.subheader("🔎 Filters")


# # ============================================================
# # 22. REPOSITORY-AWARE DATA LOADING
# # ============================================================

# def normalize_repo_name(value):
#     """Return a clean repository name from a value."""
#     if value is None:
#         return ""
#     value = str(value).strip()
#     if "/" in value:
#         return value.rsplit("/", 1)[-1]
#     return value


# def repository_payload(repo_name):
#     """
#     Load synchronized data for one repository.

#     The multi-repository synchronization stores per-repository data under
#     data/repositories/<repo>/ when available. The helper also falls back to
#     the legacy single-repository files for TEST.
#     """
#     repo_name = normalize_repo_name(repo_name)

#     repo_dir = DATA_DIR / "repositories" / repo_name

#     def repo_file(filename, fallback_file):
#         candidate = repo_dir / filename
#         if candidate.exists():
#             return load_json_file(candidate, {})
#         return load_json_file(fallback_file, {})

#     commit_data = repo_file("commits.json", COMMITS_FILE)
#     pr_data = repo_file("pull_requests.json", PULL_REQUESTS_FILE)
#     issue_data = repo_file("issues.json", ISSUES_FILE)
#     branch_data = repo_file("branches.json", BRANCHES_FILE)
#     repo_data = repo_file("repository.json", REPOSITORY_FILE)
#     contributor_data = repo_file("contributors.json", CONTRIBUTORS_FILE)
#     collaborator_data = repo_file("collaborators.json", COLLABORATORS_FILE)

#     def list_value(data, key):
#         if isinstance(data, dict):
#             value = data.get(key, [])
#             return value if isinstance(value, list) else []
#         return data if isinstance(data, list) else []

#     return {
#         "commits": list_value(commit_data, "commits"),
#         "pull_requests": list_value(pr_data, "pull_requests"),
#         "issues": list_value(issue_data, "issues"),
#         "branches": list_value(branch_data, "branches"),
#         "repository": repo_data if isinstance(repo_data, dict) else {},
#         "contributors": list_value(contributor_data, "contributors"),
#         "collaborators": list_value(collaborator_data, "collaborators"),
#     }


# def discover_repositories():
#     """
#     Discover repositories from synchronized multi-repository folders.

#     Also includes the legacy configured repository so existing TEST data
#     continues to work.
#     """
#     names = set()

#     repo_root = DATA_DIR / "repositories"
#     if repo_root.exists():
#         for child in repo_root.iterdir():
#             if child.is_dir():
#                 names.add(child.name)

#     # Support a repositories.json file if the synchronization layer creates it.
#     repositories_file = DATA_DIR / "repositories.json"
#     repositories_data = load_json_file(
#         repositories_file,
#         {"repositories": []}
#     )

#     if isinstance(repositories_data, dict):
#         repo_items = repositories_data.get("repositories", [])
#     elif isinstance(repositories_data, list):
#         repo_items = repositories_data
#     else:
#         repo_items = []

#     for item in repo_items:
#         if isinstance(item, str):
#             names.add(normalize_repo_name(item))
#         elif isinstance(item, dict):
#             name = (
#                 item.get("name")
#                 or item.get("repository")
#                 or item.get("full_name")
#             )
#             if name:
#                 names.add(normalize_repo_name(name))

#     if REPO_NAME:
#         names.add(normalize_repo_name(REPO_NAME))

#     return sorted(name for name in names if name)


# # ============================================================
# # 23. LOAD ALL REPOSITORIES
# # ============================================================

# repositories = discover_repositories()

# if not repositories:
#     st.warning(
#         "No repositories were discovered. "
#         "Run GitHub synchronization from the sidebar."
#     )
#     st.stop()


# # ============================================================
# # 24. GLOBAL SIDEBAR FILTERS
# # ============================================================

# # Repository selection must affect every repository-specific dashboard
# # section, while the Repository-wise Activity tab remains the comparison
# # view across all repositories.

# with st.sidebar:
#     selected_repository = st.selectbox(
#         "📦 Select Repository",
#         ["All Repositories"] + repositories,
#         key="selected_repository_filter",
#     )

#     all_repository_data = {
#         repo_name: repository_payload(repo_name)
#         for repo_name in repositories
#     }

#     # Developers are based on the selected repository when one is selected.
#     if selected_repository == "All Repositories":
#         developer_source_commits = []
#         for payload in all_repository_data.values():
#             developer_source_commits.extend(payload["commits"])
#     else:
#         developer_source_commits = all_repository_data[
#             selected_repository
#         ]["commits"]

#     developer_source_df = commits_to_dataframe(
#         developer_source_commits
#     )

#     developers = sorted(
#         developer_source_df["Developer"]
#         .dropna()
#         .unique()
#         .tolist()
#     ) if not developer_source_df.empty else []

#     selected_developer = st.selectbox(
#         "👤 Developer",
#         ["All Developers"] + developers,
#         key="selected_developer_filter",
#     )

#     date_filter = st.selectbox(
#         "📅 Commit Date Range",
#         [
#             "All Time",
#             "Last 7 Days",
#             "Last 30 Days",
#             "Last 90 Days",
#             "Custom Range",
#         ],
#         key="date_range_filter",
#     )

#     custom_start = None
#     custom_end = None

#     if date_filter == "Custom Range":
#         valid_dates = developer_source_df["Date"].dropna()

#         if not valid_dates.empty:
#             min_date = valid_dates.min().date()
#             max_date = valid_dates.max().date()

#             custom_start = st.date_input(
#                 "Start Date",
#                 value=min_date,
#                 min_value=min_date,
#                 max_value=max_date,
#                 key="custom_start_date",
#             )

#             custom_end = st.date_input(
#                 "End Date",
#                 value=max_date,
#                 min_value=min_date,
#                 max_value=max_date,
#                 key="custom_end_date",
#             )

#             if custom_start > custom_end:
#                 st.error(
#                     "Start Date cannot be after End Date."
#                 )


# # ============================================================
# # 25. SELECTED REPOSITORY DATA
# # ============================================================

# if selected_repository == "All Repositories":
#     selected_data = None

#     selected_commits = []
#     selected_pull_requests = []
#     selected_issues = []
#     selected_branches = []
#     selected_repository_info = {}
#     selected_contributors = []
#     selected_collaborators = []

#     for payload in all_repository_data.values():
#         selected_commits.extend(payload["commits"])
#         selected_pull_requests.extend(payload["pull_requests"])
#         selected_issues.extend(payload["issues"])
#         selected_branches.extend(payload["branches"])
#         selected_contributors.extend(payload["contributors"])
#         selected_collaborators.extend(payload["collaborators"])

# else:
#     selected_data = all_repository_data[selected_repository]

#     selected_commits = selected_data["commits"]
#     selected_pull_requests = selected_data["pull_requests"]
#     selected_issues = selected_data["issues"]
#     selected_branches = selected_data["branches"]
#     selected_repository_info = selected_data["repository"]
#     selected_contributors = selected_data["contributors"]
#     selected_collaborators = selected_data["collaborators"]


# # ============================================================
# # 26. APPLY COMMIT FILTERS
# # ============================================================

# commit_df = commits_to_dataframe(selected_commits)

# filtered_df = commit_df.copy()

# if (
#     selected_developer != "All Developers"
#     and not filtered_df.empty
# ):
#     filtered_df = filtered_df[
#         filtered_df["Developer"] == selected_developer
#     ]

# if not filtered_df.empty:
#     latest_date = filtered_df["Date"].max()

#     if pd.notna(latest_date):

#         if date_filter == "Last 7 Days":
#             filtered_df = filtered_df[
#                 filtered_df["Date"]
#                 >= latest_date - pd.Timedelta(days=7)
#             ]

#         elif date_filter == "Last 30 Days":
#             filtered_df = filtered_df[
#                 filtered_df["Date"]
#                 >= latest_date - pd.Timedelta(days=30)
#             ]

#         elif date_filter == "Last 90 Days":
#             filtered_df = filtered_df[
#                 filtered_df["Date"]
#                 >= latest_date - pd.Timedelta(days=90)
#             ]

#         elif (
#             date_filter == "Custom Range"
#             and custom_start is not None
#             and custom_end is not None
#             and custom_start <= custom_end
#         ):
#             start_ts = pd.Timestamp(
#                 custom_start,
#                 tz="UTC"
#             )

#             end_ts = (
#                 pd.Timestamp(
#                     custom_end,
#                     tz="UTC"
#                 )
#                 + pd.Timedelta(days=1)
#             )

#             filtered_df = filtered_df[
#                 (filtered_df["Date"] >= start_ts)
#                 & (filtered_df["Date"] < end_ts)
#             ]


# # ============================================================
# # 27. FILTER PR / ISSUE DATA USING THE SAME DATE RANGE
# # ============================================================

# def filter_activity_dataframe(
#     dataframe,
#     date_columns,
#     selected_range,
#     start_date,
#     end_date,
# ):
#     if dataframe.empty:
#         return dataframe

#     result = dataframe.copy()

#     date_column = None
#     for candidate in date_columns:
#         if candidate in result.columns:
#             date_column = candidate
#             break

#     if date_column is None:
#         return result

#     result[date_column] = pd.to_datetime(
#         result[date_column],
#         errors="coerce",
#         utc=True,
#     )

#     valid = result[date_column].notna()

#     if selected_range == "All Time":
#         return result

#     if not valid.any():
#         return result.iloc[0:0]

#     latest = result.loc[valid, date_column].max()

#     if selected_range == "Last 7 Days":
#         return result[
#             result[date_column]
#             >= latest - pd.Timedelta(days=7)
#         ]

#     if selected_range == "Last 30 Days":
#         return result[
#             result[date_column]
#             >= latest - pd.Timedelta(days=30)
#         ]

#     if selected_range == "Last 90 Days":
#         return result[
#             result[date_column]
#             >= latest - pd.Timedelta(days=90)
#         ]

#     if (
#         selected_range == "Custom Range"
#         and start_date is not None
#         and end_date is not None
#         and start_date <= end_date
#     ):
#         start_ts = pd.Timestamp(
#             start_date,
#             tz="UTC"
#         )
#         end_ts = (
#             pd.Timestamp(
#                 end_date,
#                 tz="UTC"
#             )
#             + pd.Timedelta(days=1)
#         )

#         return result[
#             (result[date_column] >= start_ts)
#             & (result[date_column] < end_ts)
#         ]

#     return result


# pr_df = pull_requests_to_dataframe(
#     selected_pull_requests
# )

# issue_df = issues_to_dataframe(
#     selected_issues
# )

# branch_df = branches_to_dataframe(
#     selected_branches
# )

# filtered_pr_df = filter_activity_dataframe(
#     pr_df,
#     ["Created", "Updated"],
#     date_filter,
#     custom_start,
#     custom_end,
# )

# filtered_issue_df = filter_activity_dataframe(
#     issue_df,
#     ["Created", "Updated"],
#     date_filter,
#     custom_start,
#     custom_end,
# )


# # ============================================================
# # 28. SELECTED REPOSITORY DERIVED REPORTS
# # ============================================================

# developer_df = developer_report(
#     filtered_df
# )

# files_df = file_report(
#     filtered_df.to_dict("records")
# )


# # ============================================================
# # 29. HEADER
# # ============================================================

# # Phase 1: Incepteo Labs branded header
# header_logo_col, header_content_col = st.columns(
#     [1.45, 4.55],
#     vertical_alignment="center"
# )

# with header_logo_col:
#     if LOGO_PATH.exists():
#         st.image(
#             str(LOGO_PATH),
#             width=270
#         )

# with header_content_col:
#     st.markdown(
#         '<div class="brand-content">'
#         '<div class="main-title">'
#         'GitHub Usage & Access Reporting System'
#         '</div>'
#         '<div class="subtitle">'
#         'Automated GitHub activity monitoring, '
#         'developer analytics, repository insights '
#         'and access reporting'
#         '</div>'
#         '</div>',
#         unsafe_allow_html=True
#     )

# st.divider()

# if selected_repository == "All Repositories":
#     st.markdown(
#         f"""
#         <div class="repo-box">
#             <b>Repository:</b>
#             All repositories under {REPO_OWNER}
#         </div>
#         """,
#         unsafe_allow_html=True
#     )
# else:
#     st.markdown(
#         f"""
#         <div class="repo-box">
#             <b>Repository:</b>
#             {REPO_OWNER}/{selected_repository}
#         </div>
#         """,
#         unsafe_allow_html=True
#     )


# # ============================================================
# # 30. NAVIGATION
# # ============================================================

# (
#     tab_repository_activity,
#     tab_overview,
#     tab_developers,
#     tab_commits,
#     tab_prs,
#     tab_issues,
#     tab_branches,
#     tab_access,
#     tab_reports,
# ) = st.tabs(
#     [
#         "🏢 Repository-wise Activity",
#         "📊 Overview",
#         "👥 Developers",
#         "📝 Commits",
#         "🔀 Pull Requests",
#         "⚠️ Issues",
#         "🌿 Branches",
#         "🔐 Repository & Access",
#         "📥 Reports",
#     ]
# )


# # ============================================================
# # 31. REPOSITORY-WISE ACTIVITY
# # ============================================================

# with tab_repository_activity:

#     st.header(
#         "🏢 Repository-wise Activity"
#     )

#     st.write(
#         "This section compares activity across all repositories "
#         "available to the current GitHub token."
#     )

#     comparison_rows = []

#     for repo_name, payload in all_repository_data.items():

#         repo_commit_df = commits_to_dataframe(
#             payload["commits"]
#         )

#         comparison_rows.append(
#             {
#                 "Repository": repo_name,
#                 "Commits": len(repo_commit_df),
#                 "Pull Requests": len(
#                     payload["pull_requests"]
#                 ),
#                 "Issues": len(
#                     payload["issues"]
#                 ),
#                 "Branches": len(
#                     payload["branches"]
#                 ),
#                 "Contributors": len(
#                     payload["contributors"]
#                 ),
#                 "Collaborators": len(
#                     payload["collaborators"]
#                 ),
#                 "Additions": int(
#                     repo_commit_df["Additions"].sum()
#                 ) if not repo_commit_df.empty else 0,
#                 "Deletions": int(
#                     repo_commit_df["Deletions"].sum()
#                 ) if not repo_commit_df.empty else 0,
#             }
#         )

#     comparison_df = pd.DataFrame(
#         comparison_rows
#     )

#     if comparison_df.empty:
#         st.info(
#             "No repository activity is available."
#         )
#     else:
#         st.dataframe(
#             comparison_df.sort_values(
#                 "Commits",
#                 ascending=False
#             ),
#             use_container_width=True,
#             hide_index=True
#         )

#         st.divider()

#         st.subheader(
#             "📈 Commits by Repository"
#         )

#         repo_commit_chart = px.bar(
#             comparison_df.sort_values(
#                 "Commits",
#                 ascending=False
#             ),
#             x="Repository",
#             y="Commits",
#             text="Commits",
#         )

#         repo_commit_chart.update_layout(
#             **COMMON_LAYOUT
#         )

#         st.plotly_chart(
#             repo_commit_chart,
#             use_container_width=True,
#             config=PLOTLY_CONFIG,
#             key="repository_activity_commits_chart",
#         )

#         st.subheader(
#             "📊 Pull Requests & Issues by Repository"
#         )

#         repo_activity_long = comparison_df.melt(
#             id_vars=["Repository"],
#             value_vars=[
#                 "Pull Requests",
#                 "Issues",
#             ],
#             var_name="Activity",
#             value_name="Count",
#         )

#         repo_pr_issue_chart = px.bar(
#             repo_activity_long,
#             x="Repository",
#             y="Count",
#             color="Activity",
#             barmode="group",
#             text="Count",
#         )

#         repo_pr_issue_chart.update_layout(
#             **COMMON_LAYOUT
#         )

#         st.plotly_chart(
#             repo_pr_issue_chart,
#             use_container_width=True,
#             config=PLOTLY_CONFIG,
#             key="repository_activity_pr_issue_chart",
#         )


# # ============================================================
# # 32. OVERVIEW / OVERALL GITHUB USAGE SUMMARY
# # ============================================================

# with tab_overview:

#     if selected_repository == "All Repositories":
#         st.header(
#             "📊 Overall GitHub Usage Summary"
#         )
#         st.caption(
#             "Showing combined GitHub usage across all synchronized repositories."
#         )
#     else:
#         st.header(
#             f"📊 {selected_repository} — GitHub Usage Summary"
#         )
#         st.caption(
#             f"Showing GitHub usage for {REPO_OWNER}/{selected_repository}."
#         )

#     total_commits = len(filtered_df)
#     total_prs = len(filtered_pr_df)
#     total_issues = len(filtered_issue_df)
#     total_branches = len(branch_df)
#     total_developers = (
#         filtered_df["Developer"].nunique()
#         if not filtered_df.empty
#         else 0
#     )

#     total_additions = int(
#         filtered_df["Additions"].sum()
#     ) if not filtered_df.empty else 0

#     total_deletions = int(
#         filtered_df["Deletions"].sum()
#     ) if not filtered_df.empty else 0

#     total_files = int(
#         filtered_df["Files Changed"].sum()
#     ) if not filtered_df.empty else 0

#     total_contributors = len(
#         selected_contributors
#     )

#     total_collaborators = len(
#         selected_collaborators
#     )

#     if selected_repository == "All Repositories":
#         total_repositories = len(repositories)
#     else:
#         total_repositories = 1

#     repository_info_for_summary = (
#         selected_repository_info
#         if selected_repository != "All Repositories"
#         else {}
#     )

#     if selected_repository == "All Repositories":
#         total_stars = 0
#         total_forks = 0
#         total_watchers = 0
#         total_open_issues = 0

#         for payload in all_repository_data.values():
#             info = payload["repository"]
#             total_stars += int(
#                 info.get("stars", info.get("stargazers_count", 0))
#                 or 0
#             )
#             total_forks += int(
#                 info.get("forks", info.get("forks_count", 0))
#                 or 0
#             )
#             total_watchers += int(
#                 info.get("watchers", info.get("watchers_count", 0))
#                 or 0
#             )

#             # GitHub's open_issues_count can include pull requests.
#             # Count only records from issues.json that are actual issues.
#             repository_issue_df = issues_to_dataframe(
#                 payload["issues"]
#             )
#             if not repository_issue_df.empty:
#                 total_open_issues += int(
#                     (
#                         repository_issue_df["State"]
#                         .astype(str)
#                         .str.lower()
#                         == "open"
#                     ).sum()
#                 )
#     else:
#         total_stars = int(
#             repository_info_for_summary.get(
#                 "stars",
#                 repository_info_for_summary.get(
#                     "stargazers_count",
#                     0
#                 )
#             )
#             or 0
#         )

#         total_forks = int(
#             repository_info_for_summary.get(
#                 "forks",
#                 repository_info_for_summary.get(
#                     "forks_count",
#                     0
#                 )
#             )
#             or 0
#         )

#         total_watchers = int(
#             repository_info_for_summary.get(
#                 "watchers",
#                 repository_info_for_summary.get(
#                     "watchers_count",
#                     0
#                 )
#             )
#             or 0
#         )

#         # Count actual open issues from issues.json rather than using
#         # GitHub's repository open_issues_count, which can include PRs.
#         total_open_issues = int(
#             (
#                 issue_df["State"]
#                 .astype(str)
#                 .str.lower()
#                 == "open"
#             ).sum()
#         ) if not issue_df.empty else 0

#     c1, c2, c3, c4, c5 = st.columns(5)

#     c1.metric(
#         "Repositories",
#         total_repositories
#     )

#     c2.metric(
#         "Developers",
#         total_developers
#     )

#     c3.metric(
#         "Commits",
#         total_commits
#     )

#     c4.metric(
#         "Pull Requests",
#         total_prs
#     )

#     c5.metric(
#         "Issues",
#         total_issues
#     )

#     c6, c7, c8, c9, c10 = st.columns(5)

#     c6.metric(
#         "Branches",
#         total_branches
#     )

#     c7.metric(
#         "Contributors",
#         total_contributors
#     )

#     c8.metric(
#         "Collaborators",
#         total_collaborators
#     )

#     c9.metric(
#         "Lines Added",
#         total_additions
#     )

#     c10.metric(
#         "Lines Deleted",
#         total_deletions
#     )

#     st.divider()

#     st.subheader(
#         "💻 Code Activity"
#     )

#     code1, code2, code3 = st.columns(3)

#     code1.metric(
#         "Files Changed",
#         total_files
#     )

#     code2.metric(
#         "Lines Added",
#         total_additions
#     )

#     code3.metric(
#         "Lines Deleted",
#         total_deletions
#     )

#     st.divider()

#     st.subheader(
#         "📈 Commit Activity"
#     )

#     overview_developer_counts = (
#         filtered_df
#         .groupby("Developer")
#         .size()
#         .reset_index(name="Commits")
#         .sort_values(
#             "Commits",
#             ascending=False
#         )
#     ) if not filtered_df.empty else pd.DataFrame()

#     if not overview_developer_counts.empty:

#         overview_commits_chart = px.bar(
#             overview_developer_counts,
#             x="Developer",
#             y="Commits",
#             text="Commits",
#         )

#         overview_commits_chart.update_layout(
#             **COMMON_LAYOUT
#         )

#         st.plotly_chart(
#             overview_commits_chart,
#             use_container_width=True,
#             config=PLOTLY_CONFIG,
#             key="overview_commits_by_developer_chart",
#         )

#     activity = (
#         filtered_df
#         .dropna(subset=["Date"])
#         .assign(
#             Day=lambda x: x["Date"].dt.date
#         )
#         .groupby("Day")
#         .size()
#         .reset_index(name="Commits")
#     ) if not filtered_df.empty else pd.DataFrame()

#     if not activity.empty:

#         overview_timeline_chart = px.line(
#             activity,
#             x="Day",
#             y="Commits",
#             markers=True,
#         )

#         overview_timeline_chart.update_layout(
#             **COMMON_LAYOUT
#         )

#         st.plotly_chart(
#             overview_timeline_chart,
#             use_container_width=True,
#             config=PLOTLY_CONFIG,
#             key="overview_commit_timeline_chart",
#         )

#     st.divider()

#     st.subheader(
#         "📦 Repository Health / Snapshot"
#     )

#     h1, h2, h3, h4 = st.columns(4)

#     h1.metric(
#         "Stars",
#         total_stars
#     )

#     h2.metric(
#         "Forks",
#         total_forks
#     )

#     h3.metric(
#         "Watchers",
#         total_watchers
#     )

#     h4.metric(
#         "Open Issues",
#         total_open_issues
#     )

#     if selected_repository != "All Repositories":
#         st.write(
#             "**Repository:**",
#             repository_info_for_summary.get(
#                 "full_name",
#                 f"{REPO_OWNER}/{selected_repository}"
#             )
#         )

#         st.write(
#             "**Default Branch:**",
#             repository_info_for_summary.get(
#                 "default_branch",
#                 "Unknown"
#             )
#         )

#         st.write(
#             "**Visibility:**",
#             repository_info_for_summary.get(
#                 "visibility",
#                 "Unknown"
#             )
#         )


# # ============================================================
# # 33. DEVELOPERS
# # ============================================================

# with tab_developers:

#     st.header(
#         "👥 Developer Analysis"
#     )

#     if developer_df.empty:
#         st.info(
#             "No developer activity for the selected filters."
#         )
#     else:
#         display_df = developer_df.copy()

#         display_df["Last Activity"] = (
#             display_df["Last Activity"]
#             .dt.strftime(
#                 "%Y-%m-%d %H:%M UTC"
#             )
#         )

#         st.dataframe(
#             display_df,
#             use_container_width=True,
#             hide_index=True
#         )

#         st.divider()

#         st.subheader(
#             "⏱️ Developer Activity Status"
#         )

#         now = pd.Timestamp.now(
#             tz="UTC"
#         )

#         status_rows = []

#         for _, row in developer_df.iterrows():

#             last_activity = row[
#                 "Last Activity"
#             ]

#             if pd.isna(last_activity):

#                 status = "Unknown"
#                 days_inactive = None

#             else:

#                 if last_activity.tzinfo is None:
#                     last_activity = (
#                         last_activity
#                         .tz_localize("UTC")
#                     )

#                 days_inactive = (
#                     now - last_activity
#                 ).days

#                 if days_inactive <= 7:
#                     status = "Active"
#                 elif days_inactive <= 30:
#                     status = "Low Activity"
#                 else:
#                     status = "Inactive"

#             status_rows.append(
#                 {
#                     "Developer":
#                     row["Developer"],

#                     "Last Activity":
#                     last_activity,

#                     "Days Since Activity":
#                     days_inactive,

#                     "Status":
#                     status
#                 }
#             )

#         status_df = pd.DataFrame(
#             status_rows
#         )

#         if not status_df.empty:

#             status_display = status_df.copy()

#             status_display[
#                 "Last Activity"
#             ] = (
#                 pd.to_datetime(
#                     status_display[
#                         "Last Activity"
#                     ],
#                     errors="coerce"
#                 )
#                 .dt.strftime(
#                     "%Y-%m-%d %H:%M UTC"
#                 )
#             )

#             st.dataframe(
#                 status_display,
#                 use_container_width=True,
#                 hide_index=True
#             )

#             st.caption(
#                 "Activity status is based only on tracked commit history."
#             )

#         st.divider()

#         ranking = developer_report(
#             filtered_df
#         )

#         if not ranking.empty:

#             st.subheader(
#                 "🏆 Developer Contribution Ranking"
#             )

#             ranking_chart = px.bar(
#                 ranking,
#                 x="Developer",
#                 y="Changes",
#                 text="Changes",
#             )

#             ranking_chart.update_layout(
#                 **COMMON_LAYOUT
#             )

#             st.plotly_chart(
#                 ranking_chart,
#                 use_container_width=True,
#                 config=PLOTLY_CONFIG,
#                 key="developer_contribution_ranking_chart",
#             )


# # ============================================================
# # 34. COMMITS
# # ============================================================

# with tab_commits:

#     st.header(
#         "📝 Commit History"
#     )

#     if filtered_df.empty:
#         st.info(
#             "No commits match the selected filters."
#         )
#     else:

#         commit_display = filtered_df.copy()

#         commit_display["Date"] = (
#             commit_display["Date"]
#             .dt.strftime(
#                 "%Y-%m-%d %H:%M:%S UTC"
#             )
#         )

#         st.dataframe(
#             commit_display[
#                 [
#                     "Developer",
#                     "Email",
#                     "Date",
#                     "Message",
#                     "Additions",
#                     "Deletions",
#                     "Changes",
#                     "Files Changed",
#                     "SHA"
#                 ]
#             ],
#             use_container_width=True,
#             hide_index=True
#         )

#         st.divider()

#         st.subheader(
#             "🔎 Detailed Commit Information"
#         )

#         for index, commit in enumerate(
#             selected_commits,
#             start=1
#         ):

#             author = commit.get(
#                 "author",
#                 {}
#             )

#             developer = author.get(
#                 "name",
#                 "Unknown"
#             )

#             if (
#                 selected_developer
#                 != "All Developers"
#                 and developer
#                 != selected_developer
#             ):
#                 continue

#             message = commit.get(
#                 "message",
#                 "No commit message"
#             )

#             with st.expander(
#                 f"{index}. {message}"
#             ):

#                 left, right = st.columns(2)

#                 with left:

#                     st.write(
#                         "**Developer:**",
#                         developer
#                     )

#                     st.write(
#                         "**Email:**",
#                         author.get(
#                             "email",
#                             "Unknown"
#                         )
#                     )

#                     st.write(
#                         "**Date:**",
#                         commit.get(
#                             "date",
#                             "Unknown"
#                         )
#                     )

#                 with right:

#                     st.write(
#                         "**SHA:**",
#                         commit.get(
#                             "sha",
#                             "Unknown"
#                         )
#                     )

#                     statistics = commit.get(
#                         "statistics",
#                         {}
#                     )

#                     st.write(
#                         "**Additions:**",
#                         statistics.get(
#                             "additions",
#                             0
#                         )
#                     )

#                     st.write(
#                         "**Deletions:**",
#                         statistics.get(
#                             "deletions",
#                             0
#                         )
#                     )

#                 files = commit.get(
#                     "files",
#                     []
#                 )

#                 if files:

#                     st.write(
#                         "**Files Changed**"
#                     )

#                     file_rows = []

#                     for file_info in files:

#                         file_rows.append(
#                             {
#                                 "File":
#                                 file_info.get(
#                                     "filename",
#                                     "Unknown"
#                                 ),

#                                 "Status":
#                                 file_info.get(
#                                     "status",
#                                     "Unknown"
#                                 ),

#                                 "Additions":
#                                 file_info.get(
#                                     "additions",
#                                     0
#                                 ),

#                                 "Deletions":
#                                 file_info.get(
#                                     "deletions",
#                                     0
#                                 ),

#                                 "Changes":
#                                 file_info.get(
#                                     "changes",
#                                     0
#                                 )
#                             }
#                         )

#                     st.dataframe(
#                         pd.DataFrame(
#                             file_rows
#                         ),
#                         use_container_width=True,
#                         hide_index=True
#                     )


# # ============================================================
# # 35. PULL REQUESTS
# # ============================================================

# with tab_prs:

#     st.header(
#         "🔀 Pull Request Analytics"
#     )

#     if filtered_pr_df.empty:

#         st.info(
#             "No pull request data matches the selected filters."
#         )

#     else:

#         open_prs = int(
#             (
#                 filtered_pr_df["State"]
#                 .astype(str)
#                 .str.lower()
#                 == "open"
#             ).sum()
#         )

#         merged_prs = int(
#             filtered_pr_df["Merged"]
#             .notna()
#             .sum()
#         )

#         c1, c2, c3 = st.columns(3)

#         c1.metric(
#             "Total PRs",
#             len(filtered_pr_df)
#         )

#         c2.metric(
#             "Open PRs",
#             open_prs
#         )

#         c3.metric(
#             "Merged PRs",
#             merged_prs
#         )

#         display_pr = filtered_pr_df.copy()

#         # Use a simple serial number for dashboard display instead of the
#         # actual GitHub PR number. The original "Number" value is preserved
#         # in filtered_pr_df for reports, exports and all other functionality.
#         display_pr["Number"] = range(1, len(display_pr) + 1)

#         for column in [
#             "Created",
#             "Updated",
#             "Merged"
#         ]:
#             if column in display_pr.columns:
#                 display_pr[column] = (
#                     pd.to_datetime(
#                         display_pr[column],
#                         errors="coerce"
#                     )
#                     .dt.strftime(
#                         "%Y-%m-%d %H:%M UTC"
#                     )
#                 )

#         st.dataframe(
#             display_pr[
#                 [
#                     "Number",
#                     "Title",
#                     "Author",
#                     "State",
#                     "Created",
#                     "Updated",
#                     "Merged",
#                     "URL"
#                 ]
#             ],
#             use_container_width=True,
#             hide_index=True
#         )

#         state_counts = (
#             filtered_pr_df["State"]
#             .astype(str)
#             .str.title()
#             .value_counts()
#             .reset_index()
#         )

#         state_counts.columns = [
#             "State",
#             "Count"
#         ]

#         fig = px.bar(
#             state_counts,
#             x="State",
#             y="Count",
#             text="Count",
#             title="Pull Request Status",
#         )

#         fig.update_layout(
#             **COMMON_LAYOUT
#         )

#         st.plotly_chart(
#             fig,
#             use_container_width=True,
#             config=PLOTLY_CONFIG,
#             key="pull_request_status_chart",
#         )


# # ============================================================
# # 36. ISSUES
# # ============================================================

# with tab_issues:

#     st.header(
#         "⚠️ Issue Analytics"
#     )

#     if filtered_issue_df.empty:

#         st.info(
#             "No issue data matches the selected filters."
#         )

#     else:

#         open_issues = int(
#             (
#                 filtered_issue_df["State"]
#                 .astype(str)
#                 .str.lower()
#                 == "open"
#             ).sum()
#         )

#         closed_issues = int(
#             (
#                 filtered_issue_df["State"]
#                 .astype(str)
#                 .str.lower()
#                 == "closed"
#             ).sum()
#         )

#         c1, c2, c3 = st.columns(3)

#         c1.metric(
#             "Total Issues",
#             len(filtered_issue_df)
#         )

#         c2.metric(
#             "Open Issues",
#             open_issues
#         )

#         c3.metric(
#             "Closed Issues",
#             closed_issues
#         )

#         issue_display = filtered_issue_df.copy()

#         for column in [
#             "Created",
#             "Updated"
#         ]:
#             if column in issue_display.columns:
#                 issue_display[column] = (
#                     pd.to_datetime(
#                         issue_display[column],
#                         errors="coerce"
#                     )
#                     .dt.strftime(
#                         "%Y-%m-%d %H:%M UTC"
#                     )
#                 )

#         st.dataframe(
#             issue_display[
#                 [
#                     "Number",
#                     "Title",
#                     "Author",
#                     "State",
#                     "Created",
#                     "Updated",
#                     "Labels",
#                     "URL"
#                 ]
#             ],
#             use_container_width=True,
#             hide_index=True
#         )

#         state_counts = (
#             filtered_issue_df["State"]
#             .astype(str)
#             .str.title()
#             .value_counts()
#             .reset_index()
#         )

#         state_counts.columns = [
#             "State",
#             "Count"
#         ]

#         fig = px.bar(
#             state_counts,
#             x="State",
#             y="Count",
#             text="Count",
#             title="Issue Status",
#         )

#         fig.update_layout(
#             **COMMON_LAYOUT
#         )

#         st.plotly_chart(
#             fig,
#             use_container_width=True,
#             config=PLOTLY_CONFIG,
#             key="issue_status_chart",
#         )


# # ============================================================
# # 37. BRANCHES
# # ============================================================

# with tab_branches:

#     st.header(
#         "🌿 Branch Management"
#     )

#     if branch_df.empty:

#         st.info(
#             "No branch information is available."
#         )

#     else:

#         protected_count = int(
#             branch_df["Protected"]
#             .fillna(False)
#             .astype(bool)
#             .sum()
#         )

#         unprotected_count = (
#             len(branch_df)
#             - protected_count
#         )

#         c1, c2, c3 = st.columns(3)

#         c1.metric(
#             "Total Branches",
#             len(branch_df)
#         )

#         c2.metric(
#             "Protected",
#             protected_count
#         )

#         c3.metric(
#             "Unprotected",
#             unprotected_count
#         )

#         # Display only the branch information needed in the dashboard.
#         # Keep branch_df unchanged so Commit SHA remains available to
#         # existing reports/exports and other functionality.
#         branch_display = branch_df.copy()

#         if "Commit SHA" in branch_display.columns:
#             branch_display = branch_display[
#                 [
#                     "Branch",
#                     "Protected",
#                 ]
#             ]

#         st.dataframe(
#             branch_display,
#             use_container_width=True,
#             hide_index=True
#         )

#         branch_status = pd.DataFrame(
#             {
#                 "Status": [
#                     "Protected",
#                     "Unprotected"
#                 ],
#                 "Branches": [
#                     protected_count,
#                     unprotected_count
#                 ]
#             }
#         )

#         fig = px.pie(
#             branch_status,
#             names="Status",
#             values="Branches",
#             title="Branch Protection Overview",
#         )

#         fig.update_layout(
#             margin=dict(
#                 l=20,
#                 r=20,
#                 t=50,
#                 b=20
#             ),
#             height=400
#         )

#         st.plotly_chart(
#             fig,
#             use_container_width=True,
#             config=PLOTLY_CONFIG,
#             key="branch_protection_chart",
#         )


# # ============================================================
# # 38. REPOSITORY & ACCESS
# # ============================================================

# with tab_access:

#     st.header(
#         "🔐 Repository & Access"
#     )

#     st.subheader(
#         "📦 Repository Information"
#     )

#     if selected_repository == "All Repositories":

#         st.info(
#             "Select a specific repository to view its detailed "
#             "repository information."
#         )

#     elif selected_repository_info:

#         info = selected_repository_info

#         c1, c2, c3, c4, c5 = st.columns(5)

#         c1.metric(
#             "Stars",
#             info.get(
#                 "stars",
#                 info.get(
#                     "stargazers_count",
#                     0
#                 )
#             )
#         )

#         c2.metric(
#             "Forks",
#             info.get(
#                 "forks",
#                 info.get(
#                     "forks_count",
#                     0
#                 )
#             )
#         )

#         c3.metric(
#             "Open Issues",
#             int(
#                 (
#                     issue_df["State"]
#                     .astype(str)
#                     .str.lower()
#                     == "open"
#                 ).sum()
#             ) if not issue_df.empty else 0
#         )

#         c4.metric(
#             "Watchers",
#             info.get(
#                 "watchers",
#                 info.get(
#                     "watchers_count",
#                     0
#                 )
#             )
#         )

#         c5.metric(
#             "Size (KB)",
#             info.get(
#                 "size",
#                 0
#             )
#         )

#         st.write(
#             "**Repository:**",
#             info.get(
#                 "full_name",
#                 f"{REPO_OWNER}/{selected_repository}"
#             )
#         )

#         st.write(
#             "**Default Branch:**",
#             info.get(
#                 "default_branch",
#                 "Unknown"
#             )
#         )

#         st.write(
#             "**Visibility:**",
#             info.get(
#                 "visibility",
#                 "Unknown"
#             )
#         )

#         st.write(
#             "**Description:**",
#             info.get(
#                 "description",
#                 "No description available."
#             )
#         )

#         repo_url = info.get(
#             "html_url",
#             ""
#         )

#         if repo_url:
#             st.markdown(
#                 f"[🔗 Open Repository]({repo_url})"
#             )

#     else:

#         st.warning(
#             "Repository information is unavailable."
#         )

#     st.divider()

#     st.subheader(
#         "👨‍💻 GitHub Contributors"
#     )

#     if selected_contributors:

#         contributor_rows = []

#         for user in selected_contributors:

#             if not isinstance(
#                 user,
#                 dict
#             ):
#                 continue

#             contributor_rows.append(
#                 {
#                     "Login":
#                     user.get(
#                         "login",
#                         "Anonymous"
#                     ),

#                     "Contributions":
#                     user.get(
#                         "contributions",
#                         0
#                     ),

#                     "Profile":
#                     user.get(
#                         "html_url",
#                         user.get(
#                             "profile_url",
#                             ""
#                         )
#                     )
#                 }
#             )

#         st.dataframe(
#             pd.DataFrame(
#                 contributor_rows
#             ),
#             use_container_width=True,
#             hide_index=True
#         )

#     else:

#         st.info(
#             "Contributor information is unavailable."
#         )

#     st.divider()

#     st.subheader(
#         "🔑 Repository Collaborators & Permissions"
#     )

#     access_df = collaborators_to_dataframe(
#         selected_collaborators
#     )

#     if access_df.empty:

#         st.info(
#             "Collaborator information is unavailable "
#             "for this repository."
#         )

#     else:

#         st.dataframe(
#             access_df[
#                 [
#                     "User",
#                     "Permission",
#                     "Admin",
#                     "Maintain",
#                     "Write",
#                     "Triage",
#                     "Read",
#                     "Profile",
#                 ]
#             ],
#             column_config={
#                 "Admin": st.column_config.CheckboxColumn(
#                     "Admin",
#                     disabled=True,
#                 ),
#                 "Maintain": st.column_config.CheckboxColumn(
#                     "Maintain",
#                     disabled=True,
#                 ),
#                 "Write": st.column_config.CheckboxColumn(
#                     "Write",
#                     disabled=True,
#                 ),
#                 "Triage": st.column_config.CheckboxColumn(
#                     "Triage",
#                     disabled=True,
#                 ),
#                 "Read": st.column_config.CheckboxColumn(
#                     "Read",
#                     disabled=True,
#                 ),
#                 "Profile": st.column_config.LinkColumn(
#                     "Profile",
#                     display_text="🔗 Open Profile",
#                     validate="^https?://",
#                 ),
#             },
#             use_container_width=True,
#             hide_index=True,
#         )

#         st.caption(
#             "Permission is the effective repository permission "
#             "returned by GitHub. Write means the collaborator "
#             "has push/write access."
#         )

#         permission_counts = (
#             access_df["Permission"]
#             .value_counts()
#             .rename_axis("Permission")
#             .reset_index(name="Users")
#         )

#         st.dataframe(
#             permission_counts,
#             use_container_width=True,
#             hide_index=True
#         )

#     st.divider()

#     st.subheader(
#         "⚠️ Login / Audit Activity"
#     )

#     st.info(
#         "Commit activity cannot prove that a developer logged "
#         "into GitHub. Actual GitHub login and organization/"
#         "enterprise audit events require appropriate GitHub "
#         "organization or enterprise audit-log access. "
#         "This feature is intentionally excluded from the "
#         "current project scope because the current account/token "
#         "does not provide that access."
#     )


# # ============================================================
# # 39. REPORTS & EXPORT
# # ============================================================

# with tab_reports:

#     st.header(
#         "📥 Reports & Data Export"
#     )

#     report_developer_df = developer_report(
#         filtered_df
#     )

#     report_files_df = file_report(
#         filtered_df.to_dict("records")
#     )

#     report_access_df = collaborators_to_dataframe(
#         selected_collaborators
#     )

#     report_repository_name = (
#         "All Repositories"
#         if selected_repository == "All Repositories"
#         else f"{REPO_OWNER}/{selected_repository}"
#     )

#     excel_sheets = {
#         "Summary": pd.DataFrame(
#             [{
#                 "Repository": report_repository_name,
#                 "Developer": selected_developer,
#                 "Date Range": date_filter,
#                 "Commits": len(filtered_df),
#                 "Pull Requests": len(filtered_pr_df),
#                 "Issues": len(filtered_issue_df),
#                 "Branches": len(branch_df),
#                 "Contributors": len(selected_contributors),
#                 "Collaborators": len(report_access_df),
#                 "Lines Added": total_additions,
#                 "Lines Deleted": total_deletions,
#             }]
#         ),

#         "Developers":
#         report_developer_df,

#         "Commits":
#         filtered_df,

#         "Pull Requests":
#         filtered_pr_df,

#         "Issues":
#         filtered_issue_df,

#         "Branches":
#         branch_df,

#         "Collaborators":
#         report_access_df,

#         "File Activity":
#         report_files_df,
#     }

#     try:

#         excel_bytes = dataframes_to_excel(
#             excel_sheets
#         )

#         st.download_button(
#             "⬇️ Download Complete Excel Report",
#             data=excel_bytes,
#             file_name="github_usage_complete_report.xlsx",
#             mime=(
#                 "application/vnd.openxmlformats-officedocument."
#                 "spreadsheetml.sheet"
#             ),
#             use_container_width=True,
#             key="download_complete_excel_report",
#         )

#         st.caption(
#             "The Excel report respects the selected repository, "
#             "developer and date filters."
#         )

#     except ImportError:

#         st.error(
#             "Excel export requires openpyxl. "
#             "Install it with: pip install openpyxl"
#         )

#     st.divider()

#     st.subheader(
#         "👥 Developer Report"
#     )

#     if not report_developer_df.empty:

#         st.download_button(
#             "⬇️ Download Developer CSV",
#             report_developer_df.to_csv(
#                 index=False
#             ),
#             file_name="developer_report.csv",
#             mime="text/csv",
#             use_container_width=True,
#             key="download_developer_csv",
#         )

#     else:

#         st.info(
#             "No developer data is available."
#         )

#     st.subheader(
#         "📝 Commit Report"
#     )

#     st.download_button(
#         "⬇️ Download Commit CSV",
#         filtered_df.to_csv(
#             index=False
#         ),
#         file_name="commit_report.csv",
#         mime="text/csv",
#         use_container_width=True,
#         key="download_commit_csv",
#     )
    

#     st.subheader(
#         "🔀 Pull Request Report"
#     )

#     if filtered_pr_df.empty:

#         st.info(
#             "No pull request records are currently available "
#             "for the selected repository and filters."
#         )

#     else:

#         st.download_button(
#             "⬇️ Download Pull Request CSV",
#             filtered_pr_df.to_csv(
#                 index=False
#             ),
#             file_name="pull_request_report.csv",
#             mime="text/csv",
#             use_container_width=True,
#             key="download_pull_request_csv",
#         )

#     st.subheader(
#         "⚠️ Issue Report"
#     )

#     if filtered_issue_df.empty:

#         st.info(
#             "No issue records are currently available "
#             "for the selected repository and filters."
#         )

#     else:

#         st.download_button(
#             "⬇️ Download Issue CSV",
#             filtered_issue_df.to_csv(
#                 index=False
#             ),
#             file_name="issue_report.csv",
#             mime="text/csv",
#             use_container_width=True,
#             key="download_issue_csv",
#         )

#     st.subheader(
#         "🌿 Branch Report"
#     )

#     if not branch_df.empty:

#         st.download_button(
#             "⬇️ Download Branch CSV",
#             branch_df.to_csv(
#                 index=False
#             ),
#             file_name="branch_report.csv",
#             mime="text/csv",
#             use_container_width=True,
#             key="download_branch_csv",
#         )

#     else:

#         st.info(
#             "No branch data is available."
#         )

#     st.subheader(
#         "📦 Complete GitHub JSON Report"
#     )

#     complete_report = {
#         "repository": report_repository_name,

#         "generated_at":
#         datetime.utcnow().isoformat() + "Z",

#         "filters": {
#             "developer":
#             selected_developer,

#             "date_range":
#             date_filter,

#             "custom_start":
#             (
#                 str(custom_start)
#                 if custom_start is not None
#                 else None
#             ),

#             "custom_end":
#             (
#                 str(custom_end)
#                 if custom_end is not None
#                 else None
#             ),
#         },

#         "repository_info":
#         selected_repository_info,

#         "commits":
#         selected_commits,

#         "pull_requests":
#         selected_pull_requests,

#         "issues":
#         selected_issues,

#         "branches":
#         selected_branches,

#         "contributors":
#         selected_contributors,

#         "collaborators":
#         selected_collaborators,
#     }

#     st.download_button(
#         "⬇️ Download Complete JSON Report",
#         json.dumps(
#             complete_report,
#             indent=4,
#             ensure_ascii=False,
#             default=str,
#         ),
#         file_name="github_usage_complete_report.json",
#         mime="application/json",
#         use_container_width=True,
#         key="download_complete_json_report",
#     )


# # ============================================================
# # 40. FOOTER
# # ============================================================

# st.divider()

# st.caption(
#     "GitHub Usage & Access Reporting System | "
#     "Automated GitHub activity, analytics and "
#     "access reporting"
# )






import json
import io
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# GitHub Usage & Access Reporting System
# Professional Dashboard
# ============================================================


# ============================================================
# 1. BASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# Phase 1: Incepteo Labs corporate branding asset
LOGO_PATH = BASE_DIR / "assets" / "incepteo_labs_logo.png"

DATA_DIR = BASE_DIR / "data"

COMMITS_FILE = DATA_DIR / "commits.json"
PULL_REQUESTS_FILE = DATA_DIR / "pull_requests.json"
ISSUES_FILE = DATA_DIR / "issues.json"
BRANCHES_FILE = DATA_DIR / "branches.json"
REPOSITORY_FILE = DATA_DIR / "repository.json"
CONTRIBUTORS_FILE = DATA_DIR / "contributors.json"
COLLABORATORS_FILE = DATA_DIR / "collaborators.json"


load_dotenv(BASE_DIR / ".env")


REPO_OWNER = os.getenv(
    "GITHUB_REPO_OWNER",
    "PraharshaIncepteolabs"
)

REPO_NAME = os.getenv(
    "GITHUB_REPO_NAME",
    "TEST"
)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


GITHUB_API = "https://api.github.com"


GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10"
}


if GITHUB_TOKEN:
    GITHUB_HEADERS["Authorization"] = (
        f"Bearer {GITHUB_TOKEN}"
    )


# ============================================================
# 2. STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="GitHub Activity & Access Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 3. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Phase 1: Corporate brand header */

    /* Phase 1 corporate header */
    .brand-content {
        width: 100%;
        text-align: center;
        padding: 4px 0;
    }

    .main-title {
        font-size: 38px;
        font-weight: 700;
        line-height: 1.15;
        margin: 0 auto 8px auto;
        text-align: center;
    }

    .subtitle {
        color: #6b7280;
        font-size: 16px;
        line-height: 1.4;
        margin: 0 auto;
        text-align: center;
        max-width: 850px;
    }


    /* Repository box */

    .repo-box {
        padding: 15px 20px;
        border-radius: 10px;
        background-color: #eef5ff;
        border: 1px solid #dbeafe;
        margin-bottom: 20px;
        font-size: 17px;
        color: #1f2937 !important;
    }


    /* Section headings */

    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 10px;
        margin-bottom: 12px;
    }


    /* Small information cards */

    .info-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        background-color: #ffffff;
        margin-bottom: 10px;
    }


    /* Hide unnecessary Streamlit footer */

    footer {
        visibility: hidden;
    }


    /* Better dataframe appearance */

    [data-testid="stDataFrame"] {
        width: 100%;
    }

    





    /* ============================================================
   PHASE 2 — PROFESSIONAL SIDEBAR
   ============================================================ */

    /* Sidebar overall spacing */
    section[data-testid="stSidebar"] {
        padding-top: 1rem;
    }

    /* Sidebar headings */
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-weight: 600;
        letter-spacing: 0.2px;
    }

    /* Professional sidebar section title */
    .sidebar-section-title {
        font-size: 20px;
        font-weight: 600;
        margin-top: 8px;
        margin-bottom: 18px;
        color: inherit;
    }

    /* Sync button */
    section[data-testid="stSidebar"] button[kind="primary"] {
        min-height: 44px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 600;
    }

    /* Normal sidebar buttons */
    section[data-testid="stSidebar"] button {
        border-radius: 8px;
    }

    /* Space between filter controls */
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] {
        margin-bottom: 14px;
    }

    /* Filter labels */
    section[data-testid="stSidebar"] label {
        font-size: 14px;
        font-weight: 500;
    }

    /* Date input spacing */
    section[data-testid="stSidebar"] div[data-testid="stDateInput"] {
        margin-bottom: 12px;
    }

    /* Sidebar divider */
    section[data-testid="stSidebar"] hr {
        margin-top: 24px;
        margin-bottom: 24px;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. PLOTLY CONFIGURATION
# ============================================================

# Important:
# scrollZoom=False prevents mouse-wheel scrolling over a chart
# from zooming the graph.

PLOTLY_CONFIG = {
    "scrollZoom": False,
    "displayModeBar": False,
    "doubleClick": False,
    "showTips": False,
    "responsive": True
}


COMMON_LAYOUT = {
    "dragmode": False,
    "hovermode": "closest",
    "margin": {
        "l": 30,
        "r": 20,
        "t": 45,
        "b": 40
    },
    "height": 400
}


# ============================================================
# 5. GENERIC JSON LOADER
# ============================================================

def load_json_file(file_path, default=None):

    if default is None:
        default = {}

    if not file_path.exists():
        return default

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        TypeError
    ):

        return default


# ============================================================
# 6. LOAD COMMITS
# ============================================================

@st.cache_data(ttl=60)
def load_commits():

    data = load_json_file(
        COMMITS_FILE,
        {"commits": []}
    )

    if isinstance(data, dict):

        commits = data.get(
            "commits",
            []
        )

        if isinstance(commits, list):
            return commits

    return []


# ============================================================
# 7. LOAD PULL REQUESTS
# ============================================================

@st.cache_data(ttl=60)
def load_pull_requests():

    data = load_json_file(
        PULL_REQUESTS_FILE,
        {"pull_requests": []}
    )

    if isinstance(data, dict):

        prs = data.get(
            "pull_requests",
            []
        )

        if isinstance(prs, list):
            return prs

    if isinstance(data, list):
        return data

    return []


# ============================================================
# 8. LOAD ISSUES
# ============================================================

@st.cache_data(ttl=60)
def load_issues():

    data = load_json_file(
        ISSUES_FILE,
        {"issues": []}
    )

    if isinstance(data, dict):

        issues = data.get(
            "issues",
            []
        )

        if isinstance(issues, list):
            return issues

    if isinstance(data, list):
        return data

    return []


# ============================================================
# 9. LOAD BRANCHES
# ============================================================

@st.cache_data(ttl=60)
def load_branches():

    data = load_json_file(
        BRANCHES_FILE,
        {"branches": []}
    )

    if isinstance(data, dict):

        branches = data.get(
            "branches",
            []
        )

        if isinstance(branches, list):
            return branches

    if isinstance(data, list):
        return data

    return []


# ============================================================
# 10. LOAD REPOSITORY
# ============================================================

@st.cache_data(ttl=60)
def load_repository():

    data = load_json_file(
        REPOSITORY_FILE,
        {}
    )

    if isinstance(data, dict):
        return data

    return {}


# ============================================================
# 11. LOAD CONTRIBUTORS
# ============================================================

@st.cache_data(ttl=60)
def load_contributors():

    data = load_json_file(
        CONTRIBUTORS_FILE,
        {"contributors": []}
    )

    if isinstance(data, dict):

        contributors = data.get(
            "contributors",
            []
        )

        if isinstance(contributors, list):
            return contributors

    if isinstance(data, list):
        return data

    return []


# ============================================================
# 12. LOAD COLLABORATORS
# ============================================================

@st.cache_data(ttl=60)
def load_collaborators():

    data = load_json_file(
        COLLABORATORS_FILE,
        {"collaborators": []}
    )

    if isinstance(data, dict):

        collaborators = data.get(
            "collaborators",
            []
        )

        if isinstance(collaborators, list):
            return collaborators

    if isinstance(data, list):
        return data

    return []


# ============================================================
# 13. SYNC WITH GITHUB
# ============================================================

def sync_github_data():

    try:

        result = subprocess.run(
            [
                sys.executable,
                str(BASE_DIR / "app.py")
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=180
        )

        if result.returncode == 0:

            return True, result.stdout

        return False, (
            result.stderr
            or result.stdout
            or "Unknown synchronization error."
        )

    except subprocess.TimeoutExpired:

        return False, (
            "GitHub synchronization timed out."
        )

    except Exception as error:

        return False, str(error)


# ============================================================
# 14. COMMIT DATAFRAME
# ============================================================

def commits_to_dataframe(commits):

    rows = []

    for commit in commits:

        author = commit.get(
            "author",
            {}
        )

        statistics = commit.get(
            "statistics",
            {}
        )

        date_value = commit.get(
            "date"
        )

        parsed_date = pd.to_datetime(
            date_value,
            errors="coerce",
            utc=True
        )

        additions = int(
            statistics.get(
                "additions",
                0
            )
            or 0
        )

        deletions = int(
            statistics.get(
                "deletions",
                0
            )
            or 0
        )

        changes = statistics.get(
            "total_changes"
        )

        if changes is None:
            changes = additions + deletions

        files = commit.get(
            "files",
            []
        )

        rows.append(
            {
                "SHA": commit.get(
                    "sha",
                    ""
                ),

                "Developer": author.get(
                    "name",
                    "Unknown"
                ),

                "Email": author.get(
                    "email",
                    "Unknown"
                ),

                "Date": parsed_date,

                "Message": commit.get(
                    "message",
                    "No commit message"
                ),

                "Additions": additions,

                "Deletions": deletions,

                "Changes": int(changes or 0),

                "Files Changed": len(files)
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# 15. PULL REQUEST DATAFRAME
# ============================================================

def pull_requests_to_dataframe(pull_requests):

    rows = []

    for pr in pull_requests:

        user = pr.get(
            "user",
            {}
        )

        if not isinstance(user, dict):
            user = {}

        state = pr.get(
            "state",
            "unknown"
        )

        created = pr.get(
            "created_at",
            pr.get(
                "created",
                None
            )
        )

        updated = pr.get(
            "updated_at",
            pr.get(
                "updated",
                None
            )
        )

        merged = pr.get(
            "merged_at",
            None
        )

        rows.append(
            {
                "Number": pr.get(
                    "number",
                    ""
                ),

                "Title": pr.get(
                    "title",
                    "Untitled"
                ),

                "Author": user.get(
                    "login",
                    pr.get(
                        "author",
                        "Unknown"
                    )
                ),

                "State": state,

                "Created": pd.to_datetime(
                    created,
                    errors="coerce",
                    utc=True
                ),

                "Updated": pd.to_datetime(
                    updated,
                    errors="coerce",
                    utc=True
                ),

                "Merged": pd.to_datetime(
                    merged,
                    errors="coerce",
                    utc=True
                ),

                "URL": pr.get(
                    "html_url",
                    pr.get(
                        "url",
                        ""
                    )
                )
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# 16. ISSUE DATAFRAME
# ============================================================

def issues_to_dataframe(issues):

    rows = []

    for issue in issues:

        # GitHub pull requests can sometimes appear
        # in issue results. Exclude them if detected.

        if "pull_request" in issue:
            continue

        user = issue.get(
            "user",
            {}
        )

        if not isinstance(user, dict):
            user = {}

        labels = issue.get(
            "labels",
            []
        )

        label_names = []

        if isinstance(labels, list):

            for label in labels:

                if isinstance(label, dict):

                    label_names.append(
                        label.get(
                            "name",
                            ""
                        )
                    )

                elif isinstance(label, str):

                    label_names.append(label)

        rows.append(
            {
                "Number": issue.get(
                    "number",
                    ""
                ),

                "Title": issue.get(
                    "title",
                    "Untitled"
                ),

                "Author": user.get(
                    "login",
                    issue.get(
                        "author",
                        "Unknown"
                    )
                ),

                "State": issue.get(
                    "state",
                    "unknown"
                ),

                "Created": pd.to_datetime(
                    issue.get(
                        "created_at"
                    ),
                    errors="coerce",
                    utc=True
                ),

                "Updated": pd.to_datetime(
                    issue.get(
                        "updated_at"
                    ),
                    errors="coerce",
                    utc=True
                ),

                "Labels": ", ".join(
                    label_names
                ),

                "URL": issue.get(
                    "html_url",
                    issue.get(
                        "url",
                        ""
                    )
                )
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# 17. BRANCH DATAFRAME
# ============================================================

def branches_to_dataframe(branches):

    rows = []

    for branch in branches:

        commit_data = branch.get(
            "commit",
            {}
        )

        if not isinstance(commit_data, dict):
            commit_data = {}

        rows.append(
            {
                "Branch": branch.get(
                    "name",
                    "Unknown"
                ),

                "Protected": branch.get(
                    "protected",
                    False
                ),

                "Commit SHA": commit_data.get(
                    "sha",
                    branch.get(
                        "sha",
                        ""
                    )
                )
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# 18. DEVELOPER REPORT
# ============================================================

def developer_report(df):

    if df.empty:
        return pd.DataFrame()

    result = (
        df.groupby(
            [
                "Developer",
                "Email"
            ],
            as_index=False
        )
        .agg(
            {
                "SHA": "count",
                "Additions": "sum",
                "Deletions": "sum",
                "Changes": "sum",
                "Files Changed": "sum",
                "Date": "max"
            }
        )
    )

    result.rename(
        columns={
            "SHA": "Commits",
            "Date": "Last Activity"
        },
        inplace=True
    )

    result = result.sort_values(
        "Commits",
        ascending=False
    )

    return result


# ============================================================
# 19. FILE ACTIVITY REPORT
# ============================================================

def file_report(commits):

    files = {}

    for commit in commits:

        developer = (
            commit
            .get(
                "author",
                {}
            )
            .get(
                "name",
                "Unknown"
            )
        )

        for file_info in commit.get(
            "files",
            []
        ):

            filename = file_info.get(
                "filename",
                "Unknown"
            )

            if filename not in files:

                files[filename] = {
                    "File": filename,
                    "Commits": 0,
                    "Changes": 0,
                    "Additions": 0,
                    "Deletions": 0,
                    "Developers": set()
                }

            files[filename]["Commits"] += 1

            files[filename]["Changes"] += int(
                file_info.get(
                    "changes",
                    0
                )
                or 0
            )

            files[filename]["Additions"] += int(
                file_info.get(
                    "additions",
                    0
                )
                or 0
            )

            files[filename]["Deletions"] += int(
                file_info.get(
                    "deletions",
                    0
                )
                or 0
            )

            files[filename]["Developers"].add(
                developer
            )

    result = []

    for data in files.values():

        result.append(
            {
                "File": data["File"],
                "Commits": data["Commits"],
                "Changes": data["Changes"],
                "Additions": data["Additions"],
                "Deletions": data["Deletions"],
                "Developers": ", ".join(
                    sorted(
                        data["Developers"]
                    )
                )
            }
        )

    return pd.DataFrame(result)


# ============================================================
# 20. COLLABORATOR PERMISSION HELPERS
# ============================================================

def _permission_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "write", "maintain", "admin"}
    return bool(value)


def get_effective_permission(user):
    """Return the effective GitHub repository permission."""
    role = user.get("role_name", user.get("role"))
    if isinstance(role, str) and role.strip():
        role = role.strip().lower()
        mapping = {
            "admin": "Admin",
            "maintain": "Maintain",
            "write": "Write",
            "triage": "Triage",
            "read": "Read",
            "pull": "Read",
        }
        if role in mapping:
            return mapping[role]

    permissions = user.get("permissions", {})
    if not isinstance(permissions, dict):
        permissions = {}

    if _permission_bool(permissions.get("admin")):
        return "Admin"
    if _permission_bool(permissions.get("maintain")):
        return "Maintain"
    if _permission_bool(permissions.get("push")):
        return "Write"
    if _permission_bool(permissions.get("triage")):
        return "Triage"
    if _permission_bool(permissions.get("pull")):
        return "Read"
    return "Unknown"


def collaborators_to_dataframe(collaborators):
    """
    Convert GitHub collaborator records into a dashboard dataframe.

    The synchronized collaborators.json produced by app.py stores the
    permission flags at the top level:
        admin, maintain, push, triage, pull

    Some GitHub API responses may instead contain these values inside a
    nested "permissions" object, so this function supports both formats.
    """
    rows = []

    for user in collaborators:
        if not isinstance(user, dict):
            continue

        nested_permissions = user.get("permissions", {})
        if not isinstance(nested_permissions, dict):
            nested_permissions = {}

        def permission_value(name, default=False):
            if name in user:
                return _permission_bool(user.get(name))
            return _permission_bool(
                nested_permissions.get(name, default)
            )

        role = get_effective_permission(user)

        admin = permission_value(
            "admin",
            role == "Admin"
        )

        maintain = permission_value(
            "maintain",
            role in {"Maintain", "Admin"}
        )

        write_access = permission_value(
            "push",
            role in {"Write", "Maintain", "Admin"}
        )

        triage = permission_value(
            "triage",
            role in {"Triage", "Write", "Maintain", "Admin"}
        )

        read_access = permission_value(
            "pull",
            role in {"Read", "Triage", "Write", "Maintain", "Admin"}
        )

        # app.py stores the profile as profile_url.
        # html_url is retained as a fallback for compatibility.
        profile_url = user.get(
            "profile_url",
            user.get("html_url", "")
        )

        rows.append({
            "User": user.get("login", "Unknown"),
            "Permission": role,
            "Admin": admin,
            "Maintain": maintain,
            "Write": write_access,
            "Triage": triage,
            "Read": read_access,
            "Profile": profile_url,
        })

    return pd.DataFrame(rows)


# ============================================================
# 21. EXCEL EXPORT HELPER
# ============================================================

def dataframes_to_excel(dataframes):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, dataframe in dataframes.items():
            df = dataframe.copy() if isinstance(dataframe, pd.DataFrame) else pd.DataFrame()
            for column in df.columns:
                if pd.api.types.is_datetime64tz_dtype(df[column]):
                    df[column] = df[column].dt.tz_convert("UTC").dt.tz_localize(None)
            df.to_excel(writer, sheet_name=str(sheet_name)[:31], index=False)
    return output.getvalue()


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

with st.sidebar:

    st.header("⚙️ Controls")

    sync_button = st.button(
        "🔄 Sync with GitHub",
        use_container_width=True
    )

    if sync_button:

        with st.spinner(
            "Synchronizing GitHub data..."
        ):

            success, output = sync_github_data()

        if success:

            st.success(
                "GitHub data synchronized successfully."
            )

            # Clear cached JSON data.

            st.cache_data.clear()

            st.rerun()

        else:

            st.error(
                "GitHub synchronization failed."
            )

            with st.expander(
                "View synchronization output"
            ):

                st.code(output)

    st.divider()

    st.subheader("🔎 Filters")


# ============================================================
# 22. REPOSITORY-AWARE DATA LOADING
# ============================================================

def normalize_repo_name(value):
    """Return a clean repository name from a value."""
    if value is None:
        return ""
    value = str(value).strip()
    if "/" in value:
        return value.rsplit("/", 1)[-1]
    return value


def repository_payload(repo_name):
    """
    Load synchronized data for one repository.

    The multi-repository synchronization stores per-repository data under
    data/repositories/<repo>/ when available. The helper also falls back to
    the legacy single-repository files for TEST.
    """
    repo_name = normalize_repo_name(repo_name)

    repo_dir = DATA_DIR / "repositories" / repo_name

    def repo_file(filename, fallback_file):
        candidate = repo_dir / filename
        if candidate.exists():
            return load_json_file(candidate, {})
        return load_json_file(fallback_file, {})

    commit_data = repo_file("commits.json", COMMITS_FILE)
    pr_data = repo_file("pull_requests.json", PULL_REQUESTS_FILE)
    issue_data = repo_file("issues.json", ISSUES_FILE)
    branch_data = repo_file("branches.json", BRANCHES_FILE)
    repo_data = repo_file("repository.json", REPOSITORY_FILE)
    contributor_data = repo_file("contributors.json", CONTRIBUTORS_FILE)
    collaborator_data = repo_file("collaborators.json", COLLABORATORS_FILE)

    def list_value(data, key):
        if isinstance(data, dict):
            value = data.get(key, [])
            return value if isinstance(value, list) else []
        return data if isinstance(data, list) else []

    return {
        "commits": list_value(commit_data, "commits"),
        "pull_requests": list_value(pr_data, "pull_requests"),
        "issues": list_value(issue_data, "issues"),
        "branches": list_value(branch_data, "branches"),
        "repository": repo_data if isinstance(repo_data, dict) else {},
        "contributors": list_value(contributor_data, "contributors"),
        "collaborators": list_value(collaborator_data, "collaborators"),
    }


def discover_repositories():
    """
    Discover repositories from synchronized multi-repository folders.

    Also includes the legacy configured repository so existing TEST data
    continues to work.
    """
    names = set()

    repo_root = DATA_DIR / "repositories"
    if repo_root.exists():
        for child in repo_root.iterdir():
            if child.is_dir():
                names.add(child.name)

    # Support a repositories.json file if the synchronization layer creates it.
    repositories_file = DATA_DIR / "repositories.json"
    repositories_data = load_json_file(
        repositories_file,
        {"repositories": []}
    )

    if isinstance(repositories_data, dict):
        repo_items = repositories_data.get("repositories", [])
    elif isinstance(repositories_data, list):
        repo_items = repositories_data
    else:
        repo_items = []

    for item in repo_items:
        if isinstance(item, str):
            names.add(normalize_repo_name(item))
        elif isinstance(item, dict):
            name = (
                item.get("name")
                or item.get("repository")
                or item.get("full_name")
            )
            if name:
                names.add(normalize_repo_name(name))

    if REPO_NAME:
        names.add(normalize_repo_name(REPO_NAME))

    return sorted(name for name in names if name)


# ============================================================
# 23. LOAD ALL REPOSITORIES
# ============================================================

repositories = discover_repositories()

if not repositories:
    st.warning(
        "No repositories were discovered. "
        "Run GitHub synchronization from the sidebar."
    )
    st.stop()


# ============================================================
# 24. GLOBAL SIDEBAR FILTERS
# ============================================================

# Repository selection must affect every repository-specific dashboard
# section, while the Repository-wise Activity tab remains the comparison
# view across all repositories.

with st.sidebar:
    selected_repository = st.selectbox(
        "📦 Select Repository",
        ["All Repositories"] + repositories,
        key="selected_repository_filter",
    )

    all_repository_data = {
        repo_name: repository_payload(repo_name)
        for repo_name in repositories
    }

    # Developers are based on the selected repository when one is selected.
    if selected_repository == "All Repositories":
        developer_source_commits = []
        for payload in all_repository_data.values():
            developer_source_commits.extend(payload["commits"])
    else:
        developer_source_commits = all_repository_data[
            selected_repository
        ]["commits"]

    developer_source_df = commits_to_dataframe(
        developer_source_commits
    )

    developers = sorted(
        developer_source_df["Developer"]
        .dropna()
        .unique()
        .tolist()
    ) if not developer_source_df.empty else []

    selected_developer = st.selectbox(
        "👤 Developer",
        ["All Developers"] + developers,
        key="selected_developer_filter",
    )

    date_filter = st.selectbox(
        "📅 Commit Date Range",
        [
            "All Time",
            "Last 7 Days",
            "Last 30 Days",
            "Last 90 Days",
            "Custom Range",
        ],
        key="date_range_filter",
    )

    custom_start = None
    custom_end = None

    if date_filter == "Custom Range":
        valid_dates = developer_source_df["Date"].dropna()

        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            custom_start = st.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="custom_start_date",
            )

            custom_end = st.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="custom_end_date",
            )

            if custom_start > custom_end:
                st.error(
                    "Start Date cannot be after End Date."
                )


# ============================================================
# 25. SELECTED REPOSITORY DATA
# ============================================================

if selected_repository == "All Repositories":
    selected_data = None

    selected_commits = []
    selected_pull_requests = []
    selected_issues = []
    selected_branches = []
    selected_repository_info = {}
    selected_contributors = []
    selected_collaborators = []

    for payload in all_repository_data.values():
        selected_commits.extend(payload["commits"])
        selected_pull_requests.extend(payload["pull_requests"])
        selected_issues.extend(payload["issues"])
        selected_branches.extend(payload["branches"])
        selected_contributors.extend(payload["contributors"])
        selected_collaborators.extend(payload["collaborators"])

else:
    selected_data = all_repository_data[selected_repository]

    selected_commits = selected_data["commits"]
    selected_pull_requests = selected_data["pull_requests"]
    selected_issues = selected_data["issues"]
    selected_branches = selected_data["branches"]
    selected_repository_info = selected_data["repository"]
    selected_contributors = selected_data["contributors"]
    selected_collaborators = selected_data["collaborators"]


# ============================================================
# 26. APPLY COMMIT FILTERS
# ============================================================

commit_df = commits_to_dataframe(selected_commits)

filtered_df = commit_df.copy()

if (
    selected_developer != "All Developers"
    and not filtered_df.empty
):
    filtered_df = filtered_df[
        filtered_df["Developer"] == selected_developer
    ]

if not filtered_df.empty:
    latest_date = filtered_df["Date"].max()

    if pd.notna(latest_date):

        if date_filter == "Last 7 Days":
            filtered_df = filtered_df[
                filtered_df["Date"]
                >= latest_date - pd.Timedelta(days=7)
            ]

        elif date_filter == "Last 30 Days":
            filtered_df = filtered_df[
                filtered_df["Date"]
                >= latest_date - pd.Timedelta(days=30)
            ]

        elif date_filter == "Last 90 Days":
            filtered_df = filtered_df[
                filtered_df["Date"]
                >= latest_date - pd.Timedelta(days=90)
            ]

        elif (
            date_filter == "Custom Range"
            and custom_start is not None
            and custom_end is not None
            and custom_start <= custom_end
        ):
            start_ts = pd.Timestamp(
                custom_start,
                tz="UTC"
            )

            end_ts = (
                pd.Timestamp(
                    custom_end,
                    tz="UTC"
                )
                + pd.Timedelta(days=1)
            )

            filtered_df = filtered_df[
                (filtered_df["Date"] >= start_ts)
                & (filtered_df["Date"] < end_ts)
            ]


# ============================================================
# 27. FILTER PR / ISSUE DATA USING THE SAME DATE RANGE
# ============================================================

def filter_activity_dataframe(
    dataframe,
    date_columns,
    selected_range,
    start_date,
    end_date,
):
    if dataframe.empty:
        return dataframe

    result = dataframe.copy()

    date_column = None
    for candidate in date_columns:
        if candidate in result.columns:
            date_column = candidate
            break

    if date_column is None:
        return result

    result[date_column] = pd.to_datetime(
        result[date_column],
        errors="coerce",
        utc=True,
    )

    valid = result[date_column].notna()

    if selected_range == "All Time":
        return result

    if not valid.any():
        return result.iloc[0:0]

    latest = result.loc[valid, date_column].max()

    if selected_range == "Last 7 Days":
        return result[
            result[date_column]
            >= latest - pd.Timedelta(days=7)
        ]

    if selected_range == "Last 30 Days":
        return result[
            result[date_column]
            >= latest - pd.Timedelta(days=30)
        ]

    if selected_range == "Last 90 Days":
        return result[
            result[date_column]
            >= latest - pd.Timedelta(days=90)
        ]

    if (
        selected_range == "Custom Range"
        and start_date is not None
        and end_date is not None
        and start_date <= end_date
    ):
        start_ts = pd.Timestamp(
            start_date,
            tz="UTC"
        )
        end_ts = (
            pd.Timestamp(
                end_date,
                tz="UTC"
            )
            + pd.Timedelta(days=1)
        )

        return result[
            (result[date_column] >= start_ts)
            & (result[date_column] < end_ts)
        ]

    return result


pr_df = pull_requests_to_dataframe(
    selected_pull_requests
)

issue_df = issues_to_dataframe(
    selected_issues
)

branch_df = branches_to_dataframe(
    selected_branches
)

filtered_pr_df = filter_activity_dataframe(
    pr_df,
    ["Created", "Updated"],
    date_filter,
    custom_start,
    custom_end,
)

filtered_issue_df = filter_activity_dataframe(
    issue_df,
    ["Created", "Updated"],
    date_filter,
    custom_start,
    custom_end,
)


# ============================================================
# 28. SELECTED REPOSITORY DERIVED REPORTS
# ============================================================

developer_df = developer_report(
    filtered_df
)

files_df = file_report(
    filtered_df.to_dict("records")
)


# ============================================================
# 29. HEADER
# ============================================================

# Phase 1: Incepteo Labs branded header
header_logo_col, header_content_col, header_spacer_col = st.columns(
    [1.35, 5.3, 1.35],
    vertical_alignment="center"
)

# Company logo stays on the far left.
with header_logo_col:
    if LOGO_PATH.exists():
        st.image(
            str(LOGO_PATH),
            width=240
        )

# The application title/subtitle are centered in the middle area.
with header_content_col:
    st.markdown(
        '<div class="brand-content">'
        '<div class="main-title">'
        'GitHub Usage & Access Reporting System'
        '</div>'
        '<div class="subtitle">'
        'Automated GitHub activity monitoring, '
        'developer analytics, repository insights '
        'and access reporting'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

st.divider()

if selected_repository == "All Repositories":
    st.markdown(
        f"""
        <div class="repo-box">
            <b>Repository:</b>
            All repositories under {REPO_OWNER}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f"""
        <div class="repo-box">
            <b>Repository:</b>
            {REPO_OWNER}/{selected_repository}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 30. NAVIGATION
# ============================================================

(
    tab_repository_activity,
    tab_overview,
    tab_developers,
    tab_commits,
    tab_prs,
    tab_issues,
    tab_branches,
    tab_access,
    tab_reports,
) = st.tabs(
    [
        "🏢 Repository-wise Activity",
        "📊 Overview",
        "👥 Developers",
        "📝 Commits",
        "🔀 Pull Requests",
        "⚠️ Issues",
        "🌿 Branches",
        "🔐 Repository & Access",
        "📥 Reports",
    ]
)


# ============================================================
# 31. REPOSITORY-WISE ACTIVITY
# ============================================================

with tab_repository_activity:

    st.header(
        "🏢 Repository-wise Activity"
    )

    st.write(
        "This section compares activity across all repositories "
        "available to the current GitHub token."
    )

    comparison_rows = []

    for repo_name, payload in all_repository_data.items():

        repo_commit_df = commits_to_dataframe(
            payload["commits"]
        )

        comparison_rows.append(
            {
                "Repository": repo_name,
                "Commits": len(repo_commit_df),
                "Pull Requests": len(
                    payload["pull_requests"]
                ),
                "Issues": len(
                    payload["issues"]
                ),
                "Branches": len(
                    payload["branches"]
                ),
                "Contributors": len(
                    payload["contributors"]
                ),
                "Collaborators": len(
                    payload["collaborators"]
                ),
                "Additions": int(
                    repo_commit_df["Additions"].sum()
                ) if not repo_commit_df.empty else 0,
                "Deletions": int(
                    repo_commit_df["Deletions"].sum()
                ) if not repo_commit_df.empty else 0,
            }
        )

    comparison_df = pd.DataFrame(
        comparison_rows
    )

    if comparison_df.empty:
        st.info(
            "No repository activity is available."
        )
    else:
        st.dataframe(
            comparison_df.sort_values(
                "Commits",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "📈 Commits by Repository"
        )

        repo_commit_chart = px.bar(
            comparison_df.sort_values(
                "Commits",
                ascending=False
            ),
            x="Repository",
            y="Commits",
            text="Commits",
        )

        repo_commit_chart.update_layout(
            **COMMON_LAYOUT
        )

        st.plotly_chart(
            repo_commit_chart,
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="repository_activity_commits_chart",
        )

        st.subheader(
            "📊 Pull Requests & Issues by Repository"
        )

        repo_activity_long = comparison_df.melt(
            id_vars=["Repository"],
            value_vars=[
                "Pull Requests",
                "Issues",
            ],
            var_name="Activity",
            value_name="Count",
        )

        repo_pr_issue_chart = px.bar(
            repo_activity_long,
            x="Repository",
            y="Count",
            color="Activity",
            barmode="group",
            text="Count",
        )

        repo_pr_issue_chart.update_layout(
            **COMMON_LAYOUT
        )

        st.plotly_chart(
            repo_pr_issue_chart,
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="repository_activity_pr_issue_chart",
        )


# ============================================================
# 32. OVERVIEW / OVERALL GITHUB USAGE SUMMARY
# ============================================================

with tab_overview:

    if selected_repository == "All Repositories":
        st.header(
            "📊 Overall GitHub Usage Summary"
        )
        st.caption(
            "Showing combined GitHub usage across all synchronized repositories."
        )
    else:
        st.header(
            f"📊 {selected_repository} — GitHub Usage Summary"
        )
        st.caption(
            f"Showing GitHub usage for {REPO_OWNER}/{selected_repository}."
        )

    total_commits = len(filtered_df)
    total_prs = len(filtered_pr_df)
    total_issues = len(filtered_issue_df)
    total_branches = len(branch_df)
    total_developers = (
        filtered_df["Developer"].nunique()
        if not filtered_df.empty
        else 0
    )

    total_additions = int(
        filtered_df["Additions"].sum()
    ) if not filtered_df.empty else 0

    total_deletions = int(
        filtered_df["Deletions"].sum()
    ) if not filtered_df.empty else 0

    total_files = int(
        filtered_df["Files Changed"].sum()
    ) if not filtered_df.empty else 0

    total_contributors = len(
        selected_contributors
    )

    total_collaborators = len(
        selected_collaborators
    )

    if selected_repository == "All Repositories":
        total_repositories = len(repositories)
    else:
        total_repositories = 1

    repository_info_for_summary = (
        selected_repository_info
        if selected_repository != "All Repositories"
        else {}
    )

    if selected_repository == "All Repositories":
        total_stars = 0
        total_forks = 0
        total_watchers = 0
        total_open_issues = 0

        for payload in all_repository_data.values():
            info = payload["repository"]
            total_stars += int(
                info.get("stars", info.get("stargazers_count", 0))
                or 0
            )
            total_forks += int(
                info.get("forks", info.get("forks_count", 0))
                or 0
            )
            total_watchers += int(
                info.get("watchers", info.get("watchers_count", 0))
                or 0
            )

            # GitHub's open_issues_count can include pull requests.
            # Count only records from issues.json that are actual issues.
            repository_issue_df = issues_to_dataframe(
                payload["issues"]
            )
            if not repository_issue_df.empty:
                total_open_issues += int(
                    (
                        repository_issue_df["State"]
                        .astype(str)
                        .str.lower()
                        == "open"
                    ).sum()
                )
    else:
        total_stars = int(
            repository_info_for_summary.get(
                "stars",
                repository_info_for_summary.get(
                    "stargazers_count",
                    0
                )
            )
            or 0
        )

        total_forks = int(
            repository_info_for_summary.get(
                "forks",
                repository_info_for_summary.get(
                    "forks_count",
                    0
                )
            )
            or 0
        )

        total_watchers = int(
            repository_info_for_summary.get(
                "watchers",
                repository_info_for_summary.get(
                    "watchers_count",
                    0
                )
            )
            or 0
        )

        # Count actual open issues from issues.json rather than using
        # GitHub's repository open_issues_count, which can include PRs.
        total_open_issues = int(
            (
                issue_df["State"]
                .astype(str)
                .str.lower()
                == "open"
            ).sum()
        ) if not issue_df.empty else 0

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Repositories",
        total_repositories
    )

    c2.metric(
        "Developers",
        total_developers
    )

    c3.metric(
        "Commits",
        total_commits
    )

    c4.metric(
        "Pull Requests",
        total_prs
    )

    c5.metric(
        "Issues",
        total_issues
    )

    c6, c7, c8, c9, c10 = st.columns(5)

    c6.metric(
        "Branches",
        total_branches
    )

    c7.metric(
        "Contributors",
        total_contributors
    )

    c8.metric(
        "Collaborators",
        total_collaborators
    )

    c9.metric(
        "Lines Added",
        total_additions
    )

    c10.metric(
        "Lines Deleted",
        total_deletions
    )

    st.divider()

    st.subheader(
        "💻 Code Activity"
    )

    code1, code2, code3 = st.columns(3)

    code1.metric(
        "Files Changed",
        total_files
    )

    code2.metric(
        "Lines Added",
        total_additions
    )

    code3.metric(
        "Lines Deleted",
        total_deletions
    )

    st.divider()

    st.subheader(
        "📈 Commit Activity"
    )

    overview_developer_counts = (
        filtered_df
        .groupby("Developer")
        .size()
        .reset_index(name="Commits")
        .sort_values(
            "Commits",
            ascending=False
        )
    ) if not filtered_df.empty else pd.DataFrame()

    if not overview_developer_counts.empty:

        overview_commits_chart = px.bar(
            overview_developer_counts,
            x="Developer",
            y="Commits",
            text="Commits",
        )

        overview_commits_chart.update_layout(
            **COMMON_LAYOUT
        )

        st.plotly_chart(
            overview_commits_chart,
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="overview_commits_by_developer_chart",
        )

    activity = (
        filtered_df
        .dropna(subset=["Date"])
        .assign(
            Day=lambda x: x["Date"].dt.date
        )
        .groupby("Day")
        .size()
        .reset_index(name="Commits")
    ) if not filtered_df.empty else pd.DataFrame()

    if not activity.empty:

        overview_timeline_chart = px.line(
            activity,
            x="Day",
            y="Commits",
            markers=True,
        )

        overview_timeline_chart.update_layout(
            **COMMON_LAYOUT
        )

        st.plotly_chart(
            overview_timeline_chart,
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="overview_commit_timeline_chart",
        )

    st.divider()

    st.subheader(
        "📦 Repository Health / Snapshot"
    )

    h1, h2, h3, h4 = st.columns(4)

    h1.metric(
        "Stars",
        total_stars
    )

    h2.metric(
        "Forks",
        total_forks
    )

    h3.metric(
        "Watchers",
        total_watchers
    )

    h4.metric(
        "Open Issues",
        total_open_issues
    )

    if selected_repository != "All Repositories":
        st.write(
            "**Repository:**",
            repository_info_for_summary.get(
                "full_name",
                f"{REPO_OWNER}/{selected_repository}"
            )
        )

        st.write(
            "**Default Branch:**",
            repository_info_for_summary.get(
                "default_branch",
                "Unknown"
            )
        )

        st.write(
            "**Visibility:**",
            repository_info_for_summary.get(
                "visibility",
                "Unknown"
            )
        )


# ============================================================
# 33. DEVELOPERS
# ============================================================

with tab_developers:

    st.header(
        "👥 Developer Analysis"
    )

    if developer_df.empty:
        st.info(
            "No developer activity for the selected filters."
        )
    else:
        display_df = developer_df.copy()

        display_df["Last Activity"] = (
            display_df["Last Activity"]
            .dt.strftime(
                "%Y-%m-%d %H:%M UTC"
            )
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "⏱️ Developer Activity Status"
        )

        now = pd.Timestamp.now(
            tz="UTC"
        )

        status_rows = []

        for _, row in developer_df.iterrows():

            last_activity = row[
                "Last Activity"
            ]

            if pd.isna(last_activity):

                status = "Unknown"
                days_inactive = None

            else:

                if last_activity.tzinfo is None:
                    last_activity = (
                        last_activity
                        .tz_localize("UTC")
                    )

                days_inactive = (
                    now - last_activity
                ).days

                if days_inactive <= 7:
                    status = "Active"
                elif days_inactive <= 30:
                    status = "Low Activity"
                else:
                    status = "Inactive"

            status_rows.append(
                {
                    "Developer":
                    row["Developer"],

                    "Last Activity":
                    last_activity,

                    "Days Since Activity":
                    days_inactive,

                    "Status":
                    status
                }
            )

        status_df = pd.DataFrame(
            status_rows
        )

        if not status_df.empty:

            status_display = status_df.copy()

            status_display[
                "Last Activity"
            ] = (
                pd.to_datetime(
                    status_display[
                        "Last Activity"
                    ],
                    errors="coerce"
                )
                .dt.strftime(
                    "%Y-%m-%d %H:%M UTC"
                )
            )

            st.dataframe(
                status_display,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Activity status is based only on tracked commit history."
            )

        st.divider()

        ranking = developer_report(
            filtered_df
        )

        if not ranking.empty:

            st.subheader(
                "🏆 Developer Contribution Ranking"
            )

            ranking_chart = px.bar(
                ranking,
                x="Developer",
                y="Changes",
                text="Changes",
            )

            ranking_chart.update_layout(
                **COMMON_LAYOUT
            )

            st.plotly_chart(
                ranking_chart,
                use_container_width=True,
                config=PLOTLY_CONFIG,
                key="developer_contribution_ranking_chart",
            )


# ============================================================
# 34. COMMITS
# ============================================================

with tab_commits:

    st.header(
        "📝 Commit History"
    )

    if filtered_df.empty:
        st.info(
            "No commits match the selected filters."
        )
    else:

        commit_display = filtered_df.copy()

        commit_display["Date"] = (
            commit_display["Date"]
            .dt.strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        )

        st.dataframe(
            commit_display[
                [
                    "Developer",
                    "Email",
                    "Date",
                    "Message",
                    "Additions",
                    "Deletions",
                    "Changes",
                    "Files Changed",
                    "SHA"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "🔎 Detailed Commit Information"
        )

        for index, commit in enumerate(
            selected_commits,
            start=1
        ):

            author = commit.get(
                "author",
                {}
            )

            developer = author.get(
                "name",
                "Unknown"
            )

            if (
                selected_developer
                != "All Developers"
                and developer
                != selected_developer
            ):
                continue

            message = commit.get(
                "message",
                "No commit message"
            )

            with st.expander(
                f"{index}. {message}"
            ):

                left, right = st.columns(2)

                with left:

                    st.write(
                        "**Developer:**",
                        developer
                    )

                    st.write(
                        "**Email:**",
                        author.get(
                            "email",
                            "Unknown"
                        )
                    )

                    st.write(
                        "**Date:**",
                        commit.get(
                            "date",
                            "Unknown"
                        )
                    )

                with right:

                    st.write(
                        "**SHA:**",
                        commit.get(
                            "sha",
                            "Unknown"
                        )
                    )

                    statistics = commit.get(
                        "statistics",
                        {}
                    )

                    st.write(
                        "**Additions:**",
                        statistics.get(
                            "additions",
                            0
                        )
                    )

                    st.write(
                        "**Deletions:**",
                        statistics.get(
                            "deletions",
                            0
                        )
                    )

                files = commit.get(
                    "files",
                    []
                )

                if files:

                    st.write(
                        "**Files Changed**"
                    )

                    file_rows = []

                    for file_info in files:

                        file_rows.append(
                            {
                                "File":
                                file_info.get(
                                    "filename",
                                    "Unknown"
                                ),

                                "Status":
                                file_info.get(
                                    "status",
                                    "Unknown"
                                ),

                                "Additions":
                                file_info.get(
                                    "additions",
                                    0
                                ),

                                "Deletions":
                                file_info.get(
                                    "deletions",
                                    0
                                ),

                                "Changes":
                                file_info.get(
                                    "changes",
                                    0
                                )
                            }
                        )

                    st.dataframe(
                        pd.DataFrame(
                            file_rows
                        ),
                        use_container_width=True,
                        hide_index=True
                    )


# ============================================================
# 35. PULL REQUESTS
# ============================================================

with tab_prs:

    st.header(
        "🔀 Pull Request Analytics"
    )

    if filtered_pr_df.empty:

        st.info(
            "No pull request data matches the selected filters."
        )

    else:

        open_prs = int(
            (
                filtered_pr_df["State"]
                .astype(str)
                .str.lower()
                == "open"
            ).sum()
        )

        merged_prs = int(
            filtered_pr_df["Merged"]
            .notna()
            .sum()
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total PRs",
            len(filtered_pr_df)
        )

        c2.metric(
            "Open PRs",
            open_prs
        )

        c3.metric(
            "Merged PRs",
            merged_prs
        )

        display_pr = filtered_pr_df.copy()

        # Use a simple serial number for dashboard display instead of the
        # actual GitHub PR number. The original "Number" value is preserved
        # in filtered_pr_df for reports, exports and all other functionality.
        display_pr["Number"] = range(1, len(display_pr) + 1)

        for column in [
            "Created",
            "Updated",
            "Merged"
        ]:
            if column in display_pr.columns:
                display_pr[column] = (
                    pd.to_datetime(
                        display_pr[column],
                        errors="coerce"
                    )
                    .dt.strftime(
                        "%Y-%m-%d %H:%M UTC"
                    )
                )

        st.dataframe(
            display_pr[
                [
                    "Number",
                    "Title",
                    "Author",
                    "State",
                    "Created",
                    "Updated",
                    "Merged",
                    "URL"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        state_counts = (
            filtered_pr_df["State"]
            .astype(str)
            .str.title()
            .value_counts()
            .reset_index()
        )

        state_counts.columns = [
            "State",
            "Count"
        ]

        fig = px.bar(
            state_counts,
            x="State",
            y="Count",
            text="Count",
            title="Pull Request Status",
        )

        fig.update_layout(
            **COMMON_LAYOUT
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="pull_request_status_chart",
        )


# ============================================================
# 36. ISSUES
# ============================================================

with tab_issues:

    st.header(
        "⚠️ Issue Analytics"
    )

    if filtered_issue_df.empty:

        st.info(
            "No issue data matches the selected filters."
        )

    else:

        open_issues = int(
            (
                filtered_issue_df["State"]
                .astype(str)
                .str.lower()
                == "open"
            ).sum()
        )

        closed_issues = int(
            (
                filtered_issue_df["State"]
                .astype(str)
                .str.lower()
                == "closed"
            ).sum()
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total Issues",
            len(filtered_issue_df)
        )

        c2.metric(
            "Open Issues",
            open_issues
        )

        c3.metric(
            "Closed Issues",
            closed_issues
        )

        issue_display = filtered_issue_df.copy()

        for column in [
            "Created",
            "Updated"
        ]:
            if column in issue_display.columns:
                issue_display[column] = (
                    pd.to_datetime(
                        issue_display[column],
                        errors="coerce"
                    )
                    .dt.strftime(
                        "%Y-%m-%d %H:%M UTC"
                    )
                )

        st.dataframe(
            issue_display[
                [
                    "Number",
                    "Title",
                    "Author",
                    "State",
                    "Created",
                    "Updated",
                    "Labels",
                    "URL"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        state_counts = (
            filtered_issue_df["State"]
            .astype(str)
            .str.title()
            .value_counts()
            .reset_index()
        )

        state_counts.columns = [
            "State",
            "Count"
        ]

        fig = px.bar(
            state_counts,
            x="State",
            y="Count",
            text="Count",
            title="Issue Status",
        )

        fig.update_layout(
            **COMMON_LAYOUT
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="issue_status_chart",
        )


# ============================================================
# 37. BRANCHES
# ============================================================

with tab_branches:

    st.header(
        "🌿 Branch Management"
    )

    if branch_df.empty:

        st.info(
            "No branch information is available."
        )

    else:

        protected_count = int(
            branch_df["Protected"]
            .fillna(False)
            .astype(bool)
            .sum()
        )

        unprotected_count = (
            len(branch_df)
            - protected_count
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total Branches",
            len(branch_df)
        )

        c2.metric(
            "Protected",
            protected_count
        )

        c3.metric(
            "Unprotected",
            unprotected_count
        )

        # Display only the branch information needed in the dashboard.
        # Keep branch_df unchanged so Commit SHA remains available to
        # existing reports/exports and other functionality.
        branch_display = branch_df.copy()

        if "Commit SHA" in branch_display.columns:
            branch_display = branch_display[
                [
                    "Branch",
                    "Protected",
                ]
            ]

        st.dataframe(
            branch_display,
            use_container_width=True,
            hide_index=True
        )

        branch_status = pd.DataFrame(
            {
                "Status": [
                    "Protected",
                    "Unprotected"
                ],
                "Branches": [
                    protected_count,
                    unprotected_count
                ]
            }
        )

        fig = px.pie(
            branch_status,
            names="Status",
            values="Branches",
            title="Branch Protection Overview",
        )

        fig.update_layout(
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20
            ),
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="branch_protection_chart",
        )


# ============================================================
# 38. REPOSITORY & ACCESS
# ============================================================

with tab_access:

    st.header(
        "🔐 Repository & Access"
    )

    st.subheader(
        "📦 Repository Information"
    )

    if selected_repository == "All Repositories":

        st.info(
            "Select a specific repository to view its detailed "
            "repository information."
        )

    elif selected_repository_info:

        info = selected_repository_info

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "Stars",
            info.get(
                "stars",
                info.get(
                    "stargazers_count",
                    0
                )
            )
        )

        c2.metric(
            "Forks",
            info.get(
                "forks",
                info.get(
                    "forks_count",
                    0
                )
            )
        )

        c3.metric(
            "Open Issues",
            int(
                (
                    issue_df["State"]
                    .astype(str)
                    .str.lower()
                    == "open"
                ).sum()
            ) if not issue_df.empty else 0
        )

        c4.metric(
            "Watchers",
            info.get(
                "watchers",
                info.get(
                    "watchers_count",
                    0
                )
            )
        )

        c5.metric(
            "Size (KB)",
            info.get(
                "size",
                0
            )
        )

        st.write(
            "**Repository:**",
            info.get(
                "full_name",
                f"{REPO_OWNER}/{selected_repository}"
            )
        )

        st.write(
            "**Default Branch:**",
            info.get(
                "default_branch",
                "Unknown"
            )
        )

        st.write(
            "**Visibility:**",
            info.get(
                "visibility",
                "Unknown"
            )
        )

        st.write(
            "**Description:**",
            info.get(
                "description",
                "No description available."
            )
        )

        repo_url = info.get(
            "html_url",
            ""
        )

        if repo_url:
            st.markdown(
                f"[🔗 Open Repository]({repo_url})"
            )

    else:

        st.warning(
            "Repository information is unavailable."
        )

    st.divider()

    st.subheader(
        "👨‍💻 GitHub Contributors"
    )

    if selected_contributors:

        contributor_rows = []

        for user in selected_contributors:

            if not isinstance(
                user,
                dict
            ):
                continue

            contributor_rows.append(
                {
                    "Login":
                    user.get(
                        "login",
                        "Anonymous"
                    ),

                    "Contributions":
                    user.get(
                        "contributions",
                        0
                    ),

                    "Profile":
                    user.get(
                        "html_url",
                        user.get(
                            "profile_url",
                            ""
                        )
                    )
                }
            )

        st.dataframe(
            pd.DataFrame(
                contributor_rows
            ),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Contributor information is unavailable."
        )

    st.divider()

    st.subheader(
        "🔑 Repository Collaborators & Permissions"
    )

    access_df = collaborators_to_dataframe(
        selected_collaborators
    )

    if access_df.empty:

        st.info(
            "Collaborator information is unavailable "
            "for this repository."
        )

    else:

        st.dataframe(
            access_df[
                [
                    "User",
                    "Permission",
                    "Admin",
                    "Maintain",
                    "Write",
                    "Triage",
                    "Read",
                    "Profile",
                ]
            ],
            column_config={
                "Admin": st.column_config.CheckboxColumn(
                    "Admin",
                    disabled=True,
                ),
                "Maintain": st.column_config.CheckboxColumn(
                    "Maintain",
                    disabled=True,
                ),
                "Write": st.column_config.CheckboxColumn(
                    "Write",
                    disabled=True,
                ),
                "Triage": st.column_config.CheckboxColumn(
                    "Triage",
                    disabled=True,
                ),
                "Read": st.column_config.CheckboxColumn(
                    "Read",
                    disabled=True,
                ),
                "Profile": st.column_config.LinkColumn(
                    "Profile",
                    display_text="🔗 Open Profile",
                    validate="^https?://",
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Permission is the effective repository permission "
            "returned by GitHub. Write means the collaborator "
            "has push/write access."
        )

        permission_counts = (
            access_df["Permission"]
            .value_counts()
            .rename_axis("Permission")
            .reset_index(name="Users")
        )

        st.dataframe(
            permission_counts,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader(
        "⚠️ Login / Audit Activity"
    )

    st.info(
        "Commit activity cannot prove that a developer logged "
        "into GitHub. Actual GitHub login and organization/"
        "enterprise audit events require appropriate GitHub "
        "organization or enterprise audit-log access. "
        "This feature is intentionally excluded from the "
        "current project scope because the current account/token "
        "does not provide that access."
    )


# ============================================================
# 39. REPORTS & EXPORT
# ============================================================

with tab_reports:

    st.header(
        "📥 Reports & Data Export"
    )

    report_developer_df = developer_report(
        filtered_df
    )

    report_files_df = file_report(
        filtered_df.to_dict("records")
    )

    report_access_df = collaborators_to_dataframe(
        selected_collaborators
    )

    report_repository_name = (
        "All Repositories"
        if selected_repository == "All Repositories"
        else f"{REPO_OWNER}/{selected_repository}"
    )

    excel_sheets = {
        "Summary": pd.DataFrame(
            [{
                "Repository": report_repository_name,
                "Developer": selected_developer,
                "Date Range": date_filter,
                "Commits": len(filtered_df),
                "Pull Requests": len(filtered_pr_df),
                "Issues": len(filtered_issue_df),
                "Branches": len(branch_df),
                "Contributors": len(selected_contributors),
                "Collaborators": len(report_access_df),
                "Lines Added": total_additions,
                "Lines Deleted": total_deletions,
            }]
        ),

        "Developers":
        report_developer_df,

        "Commits":
        filtered_df,

        "Pull Requests":
        filtered_pr_df,

        "Issues":
        filtered_issue_df,

        "Branches":
        branch_df,

        "Collaborators":
        report_access_df,

        "File Activity":
        report_files_df,
    }

    try:

        excel_bytes = dataframes_to_excel(
            excel_sheets
        )

        st.download_button(
            "⬇️ Download Complete Excel Report",
            data=excel_bytes,
            file_name="github_usage_complete_report.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
            key="download_complete_excel_report",
        )

        st.caption(
            "The Excel report respects the selected repository, "
            "developer and date filters."
        )

    except ImportError:

        st.error(
            "Excel export requires openpyxl. "
            "Install it with: pip install openpyxl"
        )

    st.divider()

    st.subheader(
        "👥 Developer Report"
    )

    if not report_developer_df.empty:

        st.download_button(
            "⬇️ Download Developer CSV",
            report_developer_df.to_csv(
                index=False
            ),
            file_name="developer_report.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_developer_csv",
        )

    else:

        st.info(
            "No developer data is available."
        )

    st.subheader(
        "📝 Commit Report"
    )

    st.download_button(
        "⬇️ Download Commit CSV",
        filtered_df.to_csv(
            index=False
        ),
        file_name="commit_report.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_commit_csv",
    )
    

    st.subheader(
        "🔀 Pull Request Report"
    )

    if filtered_pr_df.empty:

        st.info(
            "No pull request records are currently available "
            "for the selected repository and filters."
        )

    else:

        st.download_button(
            "⬇️ Download Pull Request CSV",
            filtered_pr_df.to_csv(
                index=False
            ),
            file_name="pull_request_report.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_pull_request_csv",
        )

    st.subheader(
        "⚠️ Issue Report"
    )

    if filtered_issue_df.empty:

        st.info(
            "No issue records are currently available "
            "for the selected repository and filters."
        )

    else:

        st.download_button(
            "⬇️ Download Issue CSV",
            filtered_issue_df.to_csv(
                index=False
            ),
            file_name="issue_report.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_issue_csv",
        )

    st.subheader(
        "🌿 Branch Report"
    )

    if not branch_df.empty:

        st.download_button(
            "⬇️ Download Branch CSV",
            branch_df.to_csv(
                index=False
            ),
            file_name="branch_report.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_branch_csv",
        )

    else:

        st.info(
            "No branch data is available."
        )

    st.subheader(
        "📦 Complete GitHub JSON Report"
    )

    complete_report = {
        "repository": report_repository_name,

        "generated_at":
        datetime.utcnow().isoformat() + "Z",

        "filters": {
            "developer":
            selected_developer,

            "date_range":
            date_filter,

            "custom_start":
            (
                str(custom_start)
                if custom_start is not None
                else None
            ),

            "custom_end":
            (
                str(custom_end)
                if custom_end is not None
                else None
            ),
        },

        "repository_info":
        selected_repository_info,

        "commits":
        selected_commits,

        "pull_requests":
        selected_pull_requests,

        "issues":
        selected_issues,

        "branches":
        selected_branches,

        "contributors":
        selected_contributors,

        "collaborators":
        selected_collaborators,
    }

    st.download_button(
        "⬇️ Download Complete JSON Report",
        json.dumps(
            complete_report,
            indent=4,
            ensure_ascii=False,
            default=str,
        ),
        file_name="github_usage_complete_report.json",
        mime="application/json",
        use_container_width=True,
        key="download_complete_json_report",
    )


# ============================================================
# 40. FOOTER
# ============================================================

st.divider()

st.caption(
    "GitHub Usage & Access Reporting System | "
    "Automated GitHub activity, analytics and "
    "access reporting"
)









