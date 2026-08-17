import json
import io
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

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
PROJECTS_FILE = DATA_DIR / "projects.json"


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
GITHUB_PROJECT_TOKEN = os.getenv("GITHUB_PROJECT_TOKEN")


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


/* ============================================================
   PHASE 3 — PROFESSIONAL REPOSITORY INFORMATION PANEL
   ============================================================ */

    .repo-box {
        padding: 18px 24px;
        border-radius: 12px;
        background: linear-gradient(135deg, #f8fbff, #eef5ff);
        border: 1px solid #d6e4f0;
        margin-bottom: 22px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
        color: #172554 !important;
    }

    .repo-label {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.2px;
        color: #64748b !important;
        margin-bottom: 6px;
    }

    .repo-name {
        font-size: 21px;
        font-weight: 700;
        color: #172554 !important;
        margin-bottom: 14px;
    }

    .repo-meta {
        display: flex;
        gap: 28px;
        flex-wrap: wrap;
        align-items: center;
    }

    .repo-meta-item {
        font-size: 14px;
        color: #475569 !important;
    }

    .repo-meta-label {
        font-weight: 600;
        color: #334155 !important;
    }

    .repo-public {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background-color: #dcfce7;
        color: #166534;
        font-size: 13px;
        font-weight: 600;
    }

    .repo-private {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background-color: #fee2e2;
        color: #991b1b;
        font-size: 13px;
        font-weight: 600;
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

    /* Sidebar container */
    section[data-testid="stSidebar"] {
        padding-top: 0.8rem;
    }

    /* Sidebar main content */
    section[data-testid="stSidebar"] > div {
        padding-left: 1.15rem;
        padding-right: 1.15rem;
    }

    /* Sidebar headings */
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-weight: 650;
        letter-spacing: 0.1px;
    }

    /* Main sidebar title */
    .sidebar-section-title {
        font-size: 19px;
        font-weight: 650;
        line-height: 1.3;
        margin-top: 4px;
        margin-bottom: 20px;
        color: inherit;
    }

    /* Sidebar subsection */
    .sidebar-filter-title {
        font-size: 13px;
        font-weight: 650;
        letter-spacing: 0.7px;
        text-transform: uppercase;
        margin-top: 4px;
        margin-bottom: 12px;
        opacity: 0.72;
    }

    /* Sync button */
    section[data-testid="stSidebar"] button {
        border-radius: 7px;
        min-height: 40px;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.15s ease;
    }

    /* Sync button emphasis */
    section[data-testid="stSidebar"] button[kind="primary"] {
        min-height: 42px;
        border-radius: 7px;
        font-size: 14px;
        font-weight: 650;
        margin-bottom: 4px;
    }

    /* Selectbox spacing */
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] {
        margin-bottom: 16px;
    }

    /* Date input spacing */
    section[data-testid="stSidebar"] div[data-testid="stDateInput"] {
        margin-bottom: 12px;
    }

    /* Sidebar labels */
    section[data-testid="stSidebar"] label {
        font-size: 13px;
        font-weight: 550;
    }

    /* Sidebar divider */
    section[data-testid="stSidebar"] hr {
        margin-top: 20px;
        margin-bottom: 20px;
        opacity: 0.35;
    }

    /* Sidebar informational text */
    section[data-testid="stSidebar"] .stCaption {
        font-size: 12px;
        line-height: 1.45;
    }

    /* Better selectbox appearance */
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        border-radius: 7px;
        min-height: 40px;
    }

    /* Better date input appearance */
    section[data-testid="stSidebar"] [data-baseweb="input"] {
        border-radius: 7px;
    }

    /* Error message spacing */
    section[data-testid="stSidebar"] [data-testid="stAlert"] {
        border-radius: 7px;
        margin-top: 6px;
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
# 13. LOAD GITHUB PROJECTS V2
# ============================================================

def load_projects():
    data = load_json_file(PROJECTS_FILE, {"projects": []})
    if isinstance(data, dict):
        projects = data.get("projects", [])
        if isinstance(projects, list):
            return projects
    return []


# ============================================================
# 14. SYNC WITH GITHUB
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

    st.markdown(
        '<div class="sidebar-section-title">Dashboard Controls</div>',
        unsafe_allow_html=True
    )

    sync_button = st.button(
        "Sync with GitHub",
        type="primary",
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

    st.markdown(
        '<div class="sidebar-filter-title">Filters</div>',
        unsafe_allow_html=True
    )

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


def repository_full_name(repo_name, repository_info=None):
    """Return the authoritative GitHub owner/repository name."""
    repo_name = normalize_repo_name(repo_name)
    if isinstance(repository_info, dict):
        full_name = repository_info.get("full_name")
        if isinstance(full_name, str) and full_name.strip():
            return full_name.strip()
        owner = repository_info.get("owner")
        name = repository_info.get("name", repo_name)
        if isinstance(owner, str) and owner.strip() and name:
            return f"{owner.strip()}/{normalize_repo_name(name)}"
    return f"{REPO_OWNER}/{repo_name}"


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
    project_data = repo_file("projects.json", PROJECTS_FILE)

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
        "projects": list_value(project_data, "projects"),
    }


def discover_repositories():
    """Discover repositories synchronized by app.py, including future repos."""
    names = set()

    # The synchronization index is authoritative because app.py refreshes it
    # from the live ICPOC1 organization repository list.
    index_data = load_json_file(
        DATA_DIR / "repository_index.json",
        {"repositories": []},
    )
    if isinstance(index_data, dict):
        for item in index_data.get("repositories", []) or []:
            if isinstance(item, dict):
                name = item.get("name") or item.get("full_name")
            else:
                name = item
            if name:
                names.add(normalize_repo_name(name))

    # Also discover any repository folders that already exist locally.
    repo_root = DATA_DIR / "repositories"
    if repo_root.exists():
        for child in repo_root.iterdir():
            if child.is_dir():
                names.add(child.name)

    # Backward compatibility with older synchronization output.
    repositories_file = DATA_DIR / "repositories.json"
    repositories_data = load_json_file(repositories_file, {"repositories": []})
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
            name = item.get("name") or item.get("repository") or item.get("full_name")
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
        "Select Repository",
        ["All Repositories"] + repositories,
        key="selected_repository_filter",
    )

    all_repository_data = {
        repo_name: repository_payload(repo_name)
        for repo_name in repositories
    }

    # Developer and Date are section-specific filters.
    # They are intentionally not placed in the global sidebar.


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
    selected_projects = []

    for payload in all_repository_data.values():
        selected_commits.extend(payload["commits"])
        selected_pull_requests.extend(payload["pull_requests"])
        selected_issues.extend(payload["issues"])
        selected_branches.extend(payload["branches"])
        selected_contributors.extend(payload["contributors"])
        selected_collaborators.extend(payload["collaborators"])
        selected_projects.extend(payload.get("projects", []))

else:
    selected_data = all_repository_data[selected_repository]

    selected_commits = selected_data["commits"]
    selected_pull_requests = selected_data["pull_requests"]
    selected_issues = selected_data["issues"]
    selected_branches = selected_data["branches"]
    selected_repository_info = selected_data["repository"]
    selected_contributors = selected_data["contributors"]
    selected_collaborators = selected_data["collaborators"]
    selected_projects = selected_data.get("projects", [])


# ============================================================
# 26. BASE DATAFRAMES (NO SECTION-SPECIFIC FILTERS)
# ============================================================

# Developer and Date filters are applied inside the Commit and Pull Request
# sections only. Keeping the base data unfiltered prevents those filters from
# affecting Overview, Developers, Reports, or other dashboard sections.
commit_df = commits_to_dataframe(selected_commits)
filtered_df = commit_df.copy()


# ============================================================
# 27. BASE PR / ISSUE DATAFRAMES (NO SECTION-SPECIFIC FILTERS)
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
            result[date_column] >= latest - pd.Timedelta(days=7)
        ]

    if selected_range == "Last 30 Days":
        return result[
            result[date_column] >= latest - pd.Timedelta(days=30)
        ]

    if selected_range == "Last 90 Days":
        return result[
            result[date_column] >= latest - pd.Timedelta(days=90)
        ]

    if (
        selected_range == "Custom Range"
        and start_date is not None
        and end_date is not None
        and start_date <= end_date
    ):
        start_ts = pd.Timestamp(start_date, tz="UTC")
        end_ts = pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1)
        return result[
            (result[date_column] >= start_ts)
            & (result[date_column] < end_ts)
        ]

    return result


pr_df = pull_requests_to_dataframe(selected_pull_requests)
issue_df = issues_to_dataframe(selected_issues)
branch_df = branches_to_dataframe(selected_branches)

# Keep these unfiltered because Developer/Date are not global filters.
filtered_pr_df = pr_df.copy()
filtered_issue_df = issue_df.copy()


# ============================================================
# 28. SELECTED REPOSITORY DERIVED REPORTS
# ============================================================

developer_df = developer_report(
    filtered_df
)

files_df = file_report(
    filtered_df.to_dict("records")
)


# Report/export filters are intentionally not tied to Commit or Pull Request
# section filters. Reports use the complete data for the selected repository.
selected_developer = "All Developers"
date_filter = "All Time"
custom_start = None
custom_end = None


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
    selected_full_name = repository_full_name(
        selected_repository,
        selected_repository_info
    )

    st.markdown(
        f"""
        <div class="repo-box">
            <b>Repository:</b>
            {selected_full_name}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 30. NAVIGATION
# ============================================================

(
    tab_repository_activity,
    tab_projects,
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
        "🏢 Summary",
        "📋 Projects",
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
# 30A. PROJECT STATUS / PRIORITY SUMMARY HELPERS
# ============================================================

def _clean_project_value(value):
    """Normalize Project V2 status/priority values for summaries."""
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def _project_item_repository(item):
    """
    Resolve the real repository of a Project V2 item.

    The synchronized data normally contains `repository` directly. For
    backward compatibility, also inspect nested repository objects and the
    Issue/PR URL. This intentionally never assigns repository-less Draft
    Issues to a repository.
    """
    if not isinstance(item, dict):
        return ""

    def clean_repository(value):
        if isinstance(value, str):
            value = value.strip()
            return value if "/" in value else ""

        if isinstance(value, dict):
            for key in (
                "nameWithOwner",
                "full_name",
                "fullName",
                "repository",
            ):
                candidate = value.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    candidate = candidate.strip()
                    if "/" in candidate:
                        return candidate

        return ""

    # 1. Normalized repository field.
    for key in (
        "repository",
        "repo",
        "repository_full_name",
        "repositoryFullName",
    ):
        repository = clean_repository(item.get(key))
        if repository:
            return repository

    # 2. Nested content / field representations.
    for container_key in (
        "content",
        "fields",
        "field_values",
        "fieldValues",
    ):
        container = item.get(container_key)

        if isinstance(container, dict):
            for key in (
                "repository",
                "Repository",
            ):
                repository = clean_repository(container.get(key))
                if repository:
                    return repository

    # 3. Issue/PR URL is authoritative when present.
    url = item.get("url") or item.get("html_url")

    if isinstance(url, str) and url.strip():
        try:
            parsed = urlparse(url.strip())
            parts = [
                part
                for part in parsed.path.split("/")
                if part
            ]

            # /OWNER/REPOSITORY/issues/N
            # /OWNER/REPOSITORY/pull/N
            # /OWNER/REPOSITORY/pulls/N
            if (
                len(parts) >= 4
                and parts[2].lower() in {
                    "issues",
                    "pull",
                    "pulls",
                }
            ):
                return f"{parts[0]}/{parts[1]}"
        except Exception:
            pass

    return ""


def _repository_matches_selected(item_repository, selected_repository,
                                 selected_repository_info):
    """
    Compare a Project V2 item's repository with the sidebar repository.

    Full owner/repository matching is preferred. If older repository metadata
    contains a different/legacy owner but the actual repository name is the
    same, the repository name is accepted as a compatibility fallback.
    """
    item_repository = str(item_repository or "").strip().lower()

    if not item_repository:
        return False

    selected_full_name = repository_full_name(
        selected_repository,
        selected_repository_info,
    ).strip().lower()

    if item_repository == selected_full_name:
        return True

    # Compatibility fallback for legacy synchronized data.
    item_repo_name = normalize_repo_name(item_repository).strip().lower()
    selected_repo_name = normalize_repo_name(selected_repository).strip().lower()

    return (
        bool(item_repo_name)
        and bool(selected_repo_name)
        and item_repo_name == selected_repo_name
    )



def _project_items_for_selected_repository(project, selected_repository, selected_repository_info):
    """
    Return only Project V2 items that actually belong to the selected
    repository. Blank/unknown repositories are never assigned to a repository.
    """
    if not isinstance(project, dict):
        return []

    all_items = [
        item for item in (project.get("items") or [])
        if isinstance(item, dict)
    ]

    if selected_repository == "All Repositories":
        return all_items

    selected_full_name = repository_full_name(
        selected_repository,
        selected_repository_info,
    ).strip().lower()

    result = []
    for item in all_items:
        item_repository = _project_item_repository(item).strip().lower()

        # IMPORTANT: do not allow an item with an unknown repository to leak
        # into a repository-specific view.
        if _repository_matches_selected(
            item_repository,
            selected_repository,
            selected_repository_info,
        ):
            result.append(item)

    return result


def _extract_project_field(item, field_name):
    """
    Return a Project V2 field value from every supported synchronized shape.

    Priority/Status can appear as:
      - item["priority"] / item["status"]
      - item["field_values"]["Priority"] / ["Status"]
      - item["fieldValues"]
      - item["fields"]
      - nested {"name": "..."} / {"value": "..."} / {"text": "..."} objects

    The function always returns a clean string when a value is available.
    """
    if not isinstance(item, dict):
        return ""

    wanted = str(field_name).strip().lower()

    def scalar(value):
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            if isinstance(value, float) and pd.isna(value):
                return ""
            return str(value).strip()

        if isinstance(value, dict):
            # Prefer the human-readable Project option name.
            for key in (
                "name",
                "value",
                "text",
                "raw",
                "optionName",
                "option_name",
                "label",
            ):
                if key in value:
                    result = scalar(value.get(key))
                    if result:
                        return result

            # Some representations nest the selected option.
            for key in ("singleSelectOption", "option", "value"):
                nested = value.get(key)
                if nested is not None:
                    result = scalar(nested)
                    if result:
                        return result

            return ""

        if isinstance(value, list):
            for entry in value:
                result = scalar(entry)
                if result:
                    return result
            return ""

        return str(value).strip()

    # Direct normalized field first.
    direct = scalar(item.get(field_name.lower()))
    if direct:
        return direct

    # Handle capitalized or differently cased top-level keys.
    for key, value in item.items():
        if str(key).strip().lower() == wanted:
            result = scalar(value)
            if result:
                return result

    def scan_container(container):
        if isinstance(container, dict):
            # Direct field-name mapping.
            for key, value in container.items():
                if str(key).strip().lower() == wanted:
                    result = scalar(value)
                    if result:
                        return result

            # Field objects often carry the field name separately.
            field_name_value = container.get("field")
            if isinstance(field_name_value, dict):
                actual_name = scalar(
                    field_name_value.get("name")
                )
                if actual_name.strip().lower() == wanted:
                    for value_key in (
                        "name",
                        "value",
                        "text",
                        "raw",
                        "optionName",
                        "option_name",
                    ):
                        result = scalar(container.get(value_key))
                        if result:
                            return result

            # Another common shape: {"field": "Priority", "value": "High"}.
            actual_field = scalar(container.get("field"))
            if actual_field.strip().lower() == wanted:
                for value_key in (
                    "name",
                    "value",
                    "text",
                    "raw",
                    "optionName",
                    "option_name",
                ):
                    result = scalar(container.get(value_key))
                    if result:
                        return result

            # Recursively inspect nested objects.
            for value in container.values():
                if isinstance(value, (dict, list)):
                    result = scan_container(value)
                    if result:
                        return result

        elif isinstance(container, list):
            for entry in container:
                result = scan_container(entry)
                if result:
                    return result

        return ""

    # Search the known Project field containers.
    for key in (
        "field_values",
        "fieldValues",
        "fields",
        "values",
    ):
        if key in item:
            result = scan_container(item.get(key))
            if result:
                return result

    return ""


def _project_items_for_repository_summary():
    """
    Read the latest global projects.json and return Project V2 items belonging
    to the repository selected in the sidebar.

    No project number or project name is hard-coded. Every synchronized
    Project V2 is considered, so future Projects are included automatically
    after app.py synchronization.
    """
    projects = load_projects()

    if not isinstance(projects, list):
        projects = []

    selected_repo_full_name = ""
    if selected_repository != "All Repositories":
        selected_repo_full_name = repository_full_name(
            selected_repository,
            selected_repository_info,
        ).strip().lower()

    items = []
    seen_item_keys = set()

    for project in projects:
        if not isinstance(project, dict):
            continue

        for raw_item in project.get("items", []) or []:
            if not isinstance(raw_item, dict):
                continue

            item = dict(raw_item)

            item_repository = _project_item_repository(item)

            # Repository-specific filtering.
            if selected_repo_full_name:
                if not _repository_matches_selected(
                    item_repository,
                    selected_repository,
                    selected_repository_info,
                ):
                    continue

            # Normalize Status and Priority into guaranteed top-level strings.
            item["status"] = _extract_project_field(item, "status")
            item["priority"] = _extract_project_field(item, "priority")

            item_key = (
                _clean_project_value(item.get("id"))
                or "|".join(
                    [
                        _clean_project_value(item.get("title")),
                        item_repository,
                        _clean_project_value(item.get("number")),
                        str(project.get("id", "")),
                    ]
                )
            )

            if item_key in seen_item_keys:
                continue

            seen_item_keys.add(item_key)
            items.append(item)

    return items

def _normalize_status(value):
    value = _clean_project_value(value)
    lowered = value.lower()

    if lowered in {"done", "completed", "complete"}:
        return "Done"
    if lowered in {"in progress", "in-progress", "in_progress"}:
        return "In Progress"
    if lowered in {"todo", "to do", "to-do", "not started"}:
        return "Todo"
    return value or "Unknown"


def _normalize_priority(value):
    value = _clean_project_value(value)
    lowered = value.lower()

    if lowered == "high":
        return "High"
    if lowered == "medium":
        return "Medium"
    if lowered == "urgent":
        return "Urgent"
    if lowered == "low":
        return "Low"
    return value or "Unassigned"


def build_project_status_summary(items):
    """Build the Excel-style Status Summary table."""
    status_order = ["Done", "In Progress", "Todo"]

    statuses = [
        _normalize_status(_extract_project_field(item, "status"))
        for item in items
    ]

    custom_statuses = [
        status for status in dict.fromkeys(statuses)
        if status not in status_order
    ]
    ordered_statuses = status_order + custom_statuses

    rows = []
    for status in ordered_statuses:
        rows.append(
            {
                "Status": status,
                "Count of Status": statuses.count(status),
            }
        )

    rows.append(
        {
            "Status": "Grand Total",
            "Count of Status": len(items),
        }
    )

    return pd.DataFrame(rows)


def build_priority_status_summary(items):
    """Build the Excel-style Priority × Status summary table."""
    priority_order = ["High", "Medium", "Urgent", "Low"]
    status_order = ["Done", "In Progress", "Todo"]

    matrix = {
        priority: {status: 0 for status in status_order}
        for priority in priority_order
    }

    custom_priorities = []
    custom_statuses = []

    for item in items:
        priority = _normalize_priority(
            _extract_project_field(item, "priority")
        )
        status = _normalize_status(
            _extract_project_field(item, "status")
        )

        if priority not in matrix:
            custom_priorities.append(priority)
            matrix[priority] = {}

        matrix[priority].setdefault(status, 0)
        matrix[priority][status] += 1

        if status not in status_order:
            custom_statuses.append(status)

    ordered_statuses = status_order + [
        status
        for status in dict.fromkeys(custom_statuses)
        if status not in status_order
    ]

    ordered_priorities = priority_order + [
        priority
        for priority in dict.fromkeys(custom_priorities)
        if priority not in priority_order
    ]

    rows = []

    for priority in ordered_priorities:
        row = {"Task Count": priority}

        for status in ordered_statuses:
            row[status] = int(
                matrix.get(priority, {}).get(status, 0)
            )

        row["Grand Total"] = sum(
            int(row.get(status, 0))
            for status in ordered_statuses
        )

        # Always show the four Excel priorities; custom priorities only when
        # they actually contain tasks.
        if priority in priority_order or row["Grand Total"] > 0:
            rows.append(row)

    total_row = {"Task Count": "Grand Total"}

    for status in ordered_statuses:
        total_row[status] = sum(
            int(row.get(status, 0))
            for row in rows
        )

    total_row["Grand Total"] = sum(
        int(total_row.get(status, 0))
        for status in ordered_statuses
    )

    rows.append(total_row)

    return pd.DataFrame(rows), ordered_statuses


# ============================================================
# 31. REPOSITORY-WISE ACTIVITY
# ============================================================

with tab_repository_activity:

    st.header(
        "🏢 Summary"
    )

    st.write(
        "This section compares activity across all repositories "
        "available to the current GitHub token. The Project V2 task "
        "summaries below follow the repository selected in the sidebar."
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
                "Projects": len(payload.get("projects", [])),
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

        # ------------------------------------------------------------
        # PROJECT TASK STATUS / PRIORITY SUMMARIES
        # ------------------------------------------------------------
        st.divider()
        st.subheader("📋 Project Task Status Summary")

        if selected_repository == "All Repositories":
            summary_scope_text = (
                "Showing task status across all synchronized GitHub Projects "
                "and repositories."
            )
        else:
            summary_scope_text = (
                f"Showing task status for "
                f"{repository_full_name(selected_repository, selected_repository_info)} "
                "across all Projects V2 linked to this repository."
            )

        st.caption(
            summary_scope_text
            + " Newly created projects are included after "
            "'Sync with GitHub'."
        )

        summary_items = _project_items_for_repository_summary()

        if not summary_items:
            st.info(
                "No Project task items are available for the selected "
                "repository scope."
            )
        else:
            summary_status_df = build_project_status_summary(
                summary_items
            )

            st.dataframe(
                summary_status_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn(
                        "Status",
                        width="medium",
                    ),
                    "Count of Status": st.column_config.NumberColumn(
                        "Count of Status",
                        width="small",
                    ),
                },
            )

            st.subheader("📊 Priority × Status Summary")

            summary_priority_df, summary_status_columns = (
                build_priority_status_summary(summary_items)
            )

            priority_display_columns = (
                ["Task Count"]
                + summary_status_columns
                + ["Grand Total"]
            )

            st.dataframe(
                summary_priority_df[priority_display_columns],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Task Count": st.column_config.TextColumn(
                        "Task Count",
                        width="medium",
                    ),
                    **{
                        status: st.column_config.NumberColumn(
                            status,
                            width="small",
                        )
                        for status in summary_status_columns
                    },
                    "Grand Total": st.column_config.NumberColumn(
                        "Grand Total",
                        width="small",
                    ),
                },
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
# 32. GITHUB PROJECTS
# ============================================================

with tab_projects:

    st.header("📋 GitHub Projects")

    # GLOBAL projects.json is the primary Project V2 source.
    # Also merge the selected repository's synchronized project copy as a
    # compatibility fallback. This protects the dashboard if a repository
    # local cache contains a Project V2 item that the global cache does not
    # currently expose.
    project_source = load_projects()

    if selected_repository != "All Repositories":
        local_project_source = selected_data.get("projects", [])

        if isinstance(local_project_source, list):
            merged_projects = {}
            for project in project_source:
                if isinstance(project, dict):
                    key = str(
                        project.get("id")
                        or project.get("number")
                        or project.get("title")
                    )
                    merged_projects[key] = project

            for project in local_project_source:
                if isinstance(project, dict):
                    key = str(
                        project.get("id")
                        or project.get("number")
                        or project.get("title")
                    )
                    if key not in merged_projects:
                        merged_projects[key] = project

            project_source = list(merged_projects.values())

    if selected_repository == "All Repositories":
        st.caption(
            "Showing Projects V2 and their items across all synchronized repositories."
        )
    else:
        selected_full_name_for_projects = repository_full_name(
            selected_repository,
            selected_repository_info,
        )
        st.caption(
            f"Showing Project V2 items belonging to "
            f"{selected_full_name_for_projects}."
        )

    unique_projects = {}

    for project in project_source:
        if not isinstance(project, dict):
            continue

        # A project is relevant to a selected repository when either:
        # 1. GitHub explicitly links the repository to the project, OR
        # 2. at least one Project V2 item belongs to that repository.
        if selected_repository != "All Repositories":

            selected_full_name = repository_full_name(
                selected_repository,
                selected_repository_info,
            ).strip().lower()

            linked_repositories = {
                str(repo).strip().lower()
                for repo in (project.get("repositories") or [])
                if repo
            }

            repository_items = _project_items_for_selected_repository(
                project,
                selected_repository,
                selected_repository_info,
            )

            linked_repo_names = {
                normalize_repo_name(repo).strip().lower()
                for repo in linked_repositories
                if repo
            }

            selected_repo_name = (
                normalize_repo_name(selected_repository)
                .strip()
                .lower()
            )

            if (
                selected_full_name not in linked_repositories
                and selected_repo_name not in linked_repo_names
                and not repository_items
            ):
                continue

        project_id = (
            project.get("id")
            or project.get("number")
            or project.get("title")
        )

        if project_id is not None:
            unique_projects[str(project_id)] = project

    project_source = sorted(
        unique_projects.values(),
        key=lambda item: str(item.get("title", "")).lower()
    )

    if not project_source:

        st.info(
            "No GitHub Projects V2 are currently linked to the selected "
            "repository scope. Create or link a project in GitHub, then "
            "click 'Sync with GitHub'."
        )

    else:

        project_labels = [
            f"#{project.get('number', '')} — "
            f"{project.get('title', 'Untitled Project')}"
            for project in project_source
        ]

        selected_project_label = st.selectbox(
            "Select Project",
            project_labels,
            key="selected_project_filter",
        )

        selected_project = project_source[
            project_labels.index(selected_project_label)
        ]

        # Filter the selected project's items BEFORE calculating the item
        # count or displaying rows.
        visible_project_items = _project_items_for_selected_repository(
            selected_project,
            selected_repository,
            selected_repository_info,
        )

        meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)

        meta_col1.metric(
            "Items",
            len(visible_project_items)
        )

        meta_col2.metric(
            "Repositories",
            len(selected_project.get("repositories", []))
        )

        meta_col3.metric(
            "Status",
            "Closed" if selected_project.get("closed") else "Open"
        )

        meta_col4.metric(
            "Visibility",
            "Public" if selected_project.get("public") else "Private"
        )

        if selected_project.get("description"):
            st.caption(selected_project["description"])

        if selected_project.get("url"):
            st.markdown(
                f"[Open project in GitHub ↗]({selected_project['url']})"
            )

        linked_repositories = selected_project.get("repositories", [])

        if linked_repositories:
            st.caption(
                "Linked repositories: "
                + ", ".join(linked_repositories)
            )

        rows = []

        for item in visible_project_items:

            repository = _project_item_repository(item)

            item_type = item.get("type", "")
            item_number = item.get("number")

            if (
                item_number not in (None, "")
                and item_type in {"Issue", "Pull Request"}
            ):
                issue_pr = f"#{item_number}"
            else:
                issue_pr = "—"

            labels = item.get("labels", [])

            if isinstance(labels, list):
                labels_text = (
                    ", ".join(
                        str(label)
                        for label in labels
                        if label
                    )
                    or "—"
                )
            else:
                labels_text = str(labels or "—")

            field_values = item.get("field_values") or {}

            priority = item.get("priority", "")

            if not priority and isinstance(field_values, dict):

                for key, value in field_values.items():

                    if (
                        str(key).strip().lower() == "priority"
                        and value not in (None, "")
                    ):
                        priority = value
                        break

            rows.append(
                {
                    "Title": item.get(
                        "title",
                        "Untitled"
                    ),
                    "Assignees": ", ".join(
                        item.get(
                            "assignees",
                            []
                        )
                    ) or "Unassigned",
                    "Status": item.get(
                        "status",
                        ""
                    ) or "—",
                    "Due Date": item.get(
                        "due_date",
                        ""
                    ) or "—",
                    "Priority": priority or "—",
                    "Repository": repository or "—",
                    "Item Type": item_type or "—",
                    "Issue/PR #": issue_pr,
                    "Labels": labels_text,
                    "URL": item.get(
                        "url",
                        ""
                    ),
                }
            )

        project_df = pd.DataFrame(rows)

        if project_df.empty:

            st.info(
                "This project has no items belonging to the selected "
                "repository."
            )

        else:

            st.subheader("Project Items")

            project_search = st.text_input(
                "Search project items",
                placeholder=(
                    "Search by title, assignee, status, repository, "
                    "type, issue/PR number, or label..."
                ),
                key="project_item_search",
            ).strip().lower()

            filtered_project_df = project_df.copy()

            if project_search:

                searchable = (
                    filtered_project_df
                    .fillna("")
                    .astype(str)
                    .agg(" ".join, axis=1)
                    .str.lower()
                )

                filtered_project_df = filtered_project_df[
                    searchable.str.contains(
                        project_search,
                        regex=False
                    )
                ]

            st.caption(
                f"Showing {len(filtered_project_df)} of "
                f"{len(project_df)} project items"
            )

            display_columns = [
                "Title",
                "Assignees",
                "Status",
                "Due Date",
                "Priority",
            ]

            if selected_repository == "All Repositories":
                display_columns += [
                    "Repository",
                    "Item Type",
                    "Issue/PR #",
                    "Labels",
                ]

            st.dataframe(
                filtered_project_df[display_columns],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Title": st.column_config.TextColumn(
                        "Title",
                        width="large",
                    ),
                    "Assignees": st.column_config.TextColumn(
                        "Assignees",
                        width="medium",
                    ),
                    "Status": st.column_config.TextColumn(
                        "Status",
                        width="small",
                    ),
                    "Due Date": st.column_config.TextColumn(
                        "Due Date",
                        width="small",
                    ),
                    "Priority": st.column_config.TextColumn(
                        "Priority",
                        width="small",
                    ),
                    "Repository": st.column_config.TextColumn(
                        "Repository",
                        width="medium",
                    ),
                    "Item Type": st.column_config.TextColumn(
                        "Item Type",
                        width="small",
                    ),
                    "Issue/PR #": st.column_config.TextColumn(
                        "Issue/PR #",
                        width="small",
                    ),
                    "Labels": st.column_config.TextColumn(
                        "Labels",
                        width="medium",
                    ),
                },
            )

# 33. OVERVIEW / OVERALL GITHUB USAGE SUMMARY
# ============================================================

def _repository_owner_from_payload(repo_name, payload):
    """Return the actual GitHub owner for a synchronized repository."""
    info = payload.get("repository", {}) if isinstance(payload, dict) else {}

    if isinstance(info, dict):
        full_name = info.get("full_name")
        if isinstance(full_name, str) and "/" in full_name:
            return full_name.split("/", 1)[0].strip()

        owner = info.get("owner")
        if isinstance(owner, dict):
            login = owner.get("login") or owner.get("name")
            if login:
                return str(login).strip()
        elif isinstance(owner, str) and owner.strip():
            return owner.strip()

    # Fall back to the synchronized repository name.
    if isinstance(repo_name, str) and "/" in repo_name:
        return repo_name.split("/", 1)[0].strip()

    # The legacy single-repository setup uses GITHUB_REPO_OWNER.
    return REPO_OWNER.strip()


def _repository_group(repo_name, payload):
    """
    Classify a repository dynamically.

    A repository is an organization repository when its actual GitHub owner
    matches GITHUB_OWNER. Everything else is treated as outside the
    organization.
    """
    owner = _repository_owner_from_payload(repo_name, payload)
    organization_owner = os.getenv("GITHUB_OWNER", REPO_OWNER).strip()

    if owner.lower() == organization_owner.lower():
        return "Organization Repositories"

    return "Outside Organization Repositories"


def _overview_repository_names():
    """Return the repositories that should be displayed in Overview."""
    if selected_repository != "All Repositories":
        return [selected_repository]

    return list(all_repository_data.keys())


def _overview_filtered_data(repo_names):
    """
    Aggregate the same kinds of data used by the existing Overview tab,
    but only for the supplied repository group.
    """
    commits = []
    pull_requests = []
    issues = []
    branches = []
    contributors = []
    collaborators = []

    for repo_name in repo_names:
        payload = all_repository_data.get(repo_name, {})
        commits.extend(payload.get("commits", []))
        pull_requests.extend(payload.get("pull_requests", []))
        issues.extend(payload.get("issues", []))
        branches.extend(payload.get("branches", []))
        contributors.extend(payload.get("contributors", []))
        collaborators.extend(payload.get("collaborators", []))

    commit_df = commits_to_dataframe(commits)

    # Overview always uses the complete repository data.
    filtered_commit_df = commit_df.copy()

    pr_df = pull_requests_to_dataframe(pull_requests)
    issue_df_group = issues_to_dataframe(issues)
    branch_df_group = branches_to_dataframe(branches)

    filtered_pr_df_group = pr_df.copy()
    filtered_issue_df_group = issue_df_group.copy()

    return {
        "commit_df": filtered_commit_df,
        "pull_requests_df": filtered_pr_df_group,
        "issues_df": filtered_issue_df_group,
        "branches_df": branch_df_group,
        "contributors": contributors,
        "collaborators": collaborators,
    }


def _render_overview_section(section_title, repo_names, section_key):
    """
    Render the existing Overview information for one repository category.

    The metrics and charts are intentionally the same information that was
    previously shown in the combined Overview; the only change is that the
    data is calculated separately for the selected repository group.
    """
    if not repo_names:
        st.info(f"No {section_title.lower()} were discovered.")
        return

    data = _overview_filtered_data(repo_names)

    group_commit_df = data["commit_df"]
    group_pr_df = data["pull_requests_df"]
    group_issue_df = data["issues_df"]
    group_branch_df = data["branches_df"]
    group_contributors = data["contributors"]
    group_collaborators = data["collaborators"]

    total_commits = len(group_commit_df)
    total_prs = len(group_pr_df)
    total_issues = len(group_issue_df)
    total_branches = len(group_branch_df)

    total_developers = (
        group_commit_df["Developer"].nunique()
        if not group_commit_df.empty
        else 0
    )

    total_additions = (
        int(group_commit_df["Additions"].sum())
        if not group_commit_df.empty
        else 0
    )

    total_deletions = (
        int(group_commit_df["Deletions"].sum())
        if not group_commit_df.empty
        else 0
    )

    total_files = (
        int(group_commit_df["Files Changed"].sum())
        if not group_commit_df.empty
        else 0
    )

    # Count unique contributors/collaborators rather than double-counting
    # the same person across multiple repositories.
    contributor_logins = set()
    for contributor in group_contributors:
        if isinstance(contributor, dict):
            login = (
                contributor.get("login")
                or contributor.get("username")
                or contributor.get("name")
            )
            if login:
                contributor_logins.add(str(login).strip())
        elif contributor:
            contributor_logins.add(str(contributor).strip())

    collaborator_logins = set()
    for collaborator in group_collaborators:
        if isinstance(collaborator, dict):
            login = (
                collaborator.get("login")
                or collaborator.get("username")
                or collaborator.get("name")
            )
            if login:
                collaborator_logins.add(str(login).strip())
        elif collaborator:
            collaborator_logins.add(str(collaborator).strip())

    total_contributors = len(contributor_logins)
    total_collaborators = len(collaborator_logins)

    # Repository health values are summed across the repositories in this
    # category, matching the old "All Repositories" Overview behavior.
    total_stars = 0
    total_forks = 0
    total_watchers = 0
    total_open_issues = 0

    for repo_name in repo_names:
        payload = all_repository_data.get(repo_name, {})
        info = payload.get("repository", {})

        if not isinstance(info, dict):
            info = {}

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

        repository_issue_df = issues_to_dataframe(
            payload.get("issues", [])
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

    total_repositories = len(repo_names)

    st.subheader(section_title)

    st.caption(
        f"Repositories included: {', '.join(repo_names)}"
    )

    # ------------------------------------------------------------
    # EXISTING OVERVIEW METRICS
    # ------------------------------------------------------------
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Repositories", total_repositories)
    c2.metric("Developers", total_developers)
    c3.metric("Commits", total_commits)
    c4.metric("Pull Requests", total_prs)
    c5.metric("Issues", total_issues)

    c6, c7, c8, c9, c10 = st.columns(5)

    c6.metric("Branches", total_branches)
    c7.metric("Contributors", total_contributors)
    c8.metric("Collaborators", total_collaborators)
    c9.metric("Lines Added", total_additions)
    c10.metric("Lines Deleted", total_deletions)

    st.divider()

    # ------------------------------------------------------------
    # EXISTING CODE ACTIVITY
    # ------------------------------------------------------------
    st.subheader("💻 Code Activity")

    code1, code2, code3 = st.columns(3)

    code1.metric("Files Changed", total_files)
    code2.metric("Lines Added", total_additions)
    code3.metric("Lines Deleted", total_deletions)

    st.divider()

    # ------------------------------------------------------------
    # EXISTING COMMIT ACTIVITY
    # ------------------------------------------------------------
    st.subheader("📈 Commit Activity")

    overview_developer_counts = (
        group_commit_df
        .groupby("Developer")
        .size()
        .reset_index(name="Commits")
        .sort_values("Commits", ascending=False)
        if not group_commit_df.empty
        else pd.DataFrame()
    )

    if not overview_developer_counts.empty:
        overview_commits_chart = px.bar(
            overview_developer_counts,
            x="Developer",
            y="Commits",
            text="Commits",
        )

        overview_commits_chart.update_layout(**COMMON_LAYOUT)

        st.plotly_chart(
            overview_commits_chart,
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key=f"overview_commits_by_developer_{section_key}",
        )

    activity = (
        group_commit_df
        .dropna(subset=["Date"])
        .assign(Day=lambda x: x["Date"].dt.date)
        .groupby("Day")
        .size()
        .reset_index(name="Commits")
        if not group_commit_df.empty
        else pd.DataFrame()
    )

    if not activity.empty:
        overview_timeline_chart = px.line(
            activity,
            x="Day",
            y="Commits",
            markers=True,
        )

        overview_timeline_chart.update_layout(**COMMON_LAYOUT)

        st.plotly_chart(
            overview_timeline_chart,
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key=f"overview_commit_timeline_{section_key}",
        )

    st.divider()

    # ------------------------------------------------------------
    # EXISTING REPOSITORY HEALTH / SNAPSHOT
    # ------------------------------------------------------------
    st.subheader("📦 Repository Health / Snapshot")

    h1, h2, h3, h4 = st.columns(4)

    h1.metric("Stars", total_stars)
    h2.metric("Forks", total_forks)
    h3.metric("Watchers", total_watchers)
    h4.metric("Open Issues", total_open_issues)

    if len(repo_names) == 1:
        repo_name = repo_names[0]
        payload = all_repository_data.get(repo_name, {})
        info = payload.get("repository", {})

        if not isinstance(info, dict):
            info = {}

        st.write(
            "**Repository:**",
            repository_full_name(repo_name, info)
        )

        st.write(
            "**Default Branch:**",
            info.get("default_branch", "Unknown")
        )

        st.write(
            "**Visibility:**",
            info.get("visibility", "Unknown")
        )


with tab_overview:

    all_repo_names = _overview_repository_names()

    organization_repositories = [
        repo_name
        for repo_name in all_repo_names
        if _repository_group(
            repo_name,
            all_repository_data.get(repo_name, {})
        ) == "Organization Repositories"
    ]

    outside_organization_repositories = [
        repo_name
        for repo_name in all_repo_names
        if _repository_group(
            repo_name,
            all_repository_data.get(repo_name, {})
        ) == "Outside Organization Repositories"
    ]

    if selected_repository == "All Repositories":
        st.header("📊 GitHub Usage Summary")
        st.caption(
            "GitHub usage is separated into Organization Repositories "
            "and Outside Organization Repositories."
        )

        # --------------------------------------------------------
        # ORGANIZATION REPOSITORIES
        # --------------------------------------------------------
        _render_overview_section(
            "🏢 Organization Repositories",
            organization_repositories,
            "organization",
        )

        st.divider()

        # --------------------------------------------------------
        # OUTSIDE ORGANIZATION REPOSITORIES
        # --------------------------------------------------------
        _render_overview_section(
            "🌐 Outside Organization Repositories",
            outside_organization_repositories,
            "outside_organization",
        )

    else:
        # If a specific repository is selected, preserve the existing
        # repository-specific Overview behavior, while clearly identifying
        # which category the repository belongs to.
        selected_group = _repository_group(
            selected_repository,
            selected_repository_info,
        )

        if selected_group == "Organization Repositories":
            section_title = (
                f"🏢 Organization Repository — "
                f"{selected_repository}"
            )
        else:
            section_title = (
                f"🌐 Outside Organization Repository — "
                f"{selected_repository}"
            )

        st.header("📊 GitHub Usage Summary")

        st.caption(
            f"Showing GitHub usage for "
            f"{repository_full_name(selected_repository, selected_repository_info)}."
        )

        _render_overview_section(
            section_title,
            [selected_repository],
            "selected_repository",
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
# SECTION-SPECIFIC FILTER HELPERS
# ============================================================

def render_commit_filters(commit_dataframe):
    """Render filters used only by the Commit History section."""
    developers = sorted(
        commit_dataframe["Developer"].dropna().astype(str).unique().tolist()
    ) if not commit_dataframe.empty else []

    c1, c2 = st.columns(2)

    with c1:
        selected = st.selectbox(
            "Select Developer",
            ["All Developers"] + developers,
            key="commits_developer_filter",
        )

    with c2:
        date_range = st.selectbox(
            "Select Date",
            [
                "All Time",
                "Last 7 Days",
                "Last 30 Days",
                "Last 90 Days",
                "Custom Range",
            ],
            key="commits_date_filter",
        )

    start_date = None
    end_date = None

    if date_range == "Custom Range":
        valid_dates = commit_dataframe["Date"].dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            d1, d2 = st.columns(2)
            with d1:
                start_date = st.date_input(
                    "Start Date",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="commits_start_date",
                )
            with d2:
                end_date = st.date_input(
                    "End Date",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="commits_end_date",
                )
            if start_date > end_date:
                st.error("Start Date cannot be after End Date.")

    result = commit_dataframe.copy()

    if selected != "All Developers" and not result.empty:
        result = result[result["Developer"] == selected]

    if not result.empty and date_range != "All Time":
        valid = result["Date"].notna()
        if valid.any():
            latest = result.loc[valid, "Date"].max()
            if date_range == "Last 7 Days":
                result = result[result["Date"] >= latest - pd.Timedelta(days=7)]
            elif date_range == "Last 30 Days":
                result = result[result["Date"] >= latest - pd.Timedelta(days=30)]
            elif date_range == "Last 90 Days":
                result = result[result["Date"] >= latest - pd.Timedelta(days=90)]
            elif (
                date_range == "Custom Range"
                and start_date is not None
                and end_date is not None
                and start_date <= end_date
            ):
                start_ts = pd.Timestamp(start_date, tz="UTC")
                end_ts = pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1)
                result = result[
                    (result["Date"] >= start_ts)
                    & (result["Date"] < end_ts)
                ]

    return result, selected, date_range, start_date, end_date


def render_pr_filters(pr_dataframe):
    """Render filters used only by the Pull Request section."""
    developers = sorted(
        pr_dataframe["Author"].dropna().astype(str).unique().tolist()
    ) if not pr_dataframe.empty else []

    c1, c2 = st.columns(2)

    with c1:
        selected = st.selectbox(
            "Select Developer",
            ["All Developers"] + developers,
            key="prs_developer_filter",
        )

    with c2:
        date_range = st.selectbox(
            "Select Date",
            [
                "All Time",
                "Last 7 Days",
                "Last 30 Days",
                "Last 90 Days",
                "Custom Range",
            ],
            key="prs_date_filter",
        )

    start_date = None
    end_date = None

    if date_range == "Custom Range":
        valid_dates = pr_dataframe["Created"].dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            d1, d2 = st.columns(2)
            with d1:
                start_date = st.date_input(
                    "Start Date",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="prs_start_date",
                )
            with d2:
                end_date = st.date_input(
                    "End Date",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="prs_end_date",
                )
            if start_date > end_date:
                st.error("Start Date cannot be after End Date.")

    result = pr_dataframe.copy()

    if selected != "All Developers" and not result.empty:
        result = result[result["Author"] == selected]

    if not result.empty and date_range != "All Time":
        valid = result["Created"].notna()
        if valid.any():
            latest = result.loc[valid, "Created"].max()
            if date_range == "Last 7 Days":
                result = result[result["Created"] >= latest - pd.Timedelta(days=7)]
            elif date_range == "Last 30 Days":
                result = result[result["Created"] >= latest - pd.Timedelta(days=30)]
            elif date_range == "Last 90 Days":
                result = result[result["Created"] >= latest - pd.Timedelta(days=90)]
            elif (
                date_range == "Custom Range"
                and start_date is not None
                and end_date is not None
                and start_date <= end_date
            ):
                start_ts = pd.Timestamp(start_date, tz="UTC")
                end_ts = pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1)
                result = result[
                    (result["Created"] >= start_ts)
                    & (result["Created"] < end_ts)
                ]

    return result, selected, date_range, start_date, end_date


# ============================================================
# 34. COMMITS
# ============================================================

with tab_commits:

    st.header(
        "📝 Commit History"
    )

    commit_section_df, commit_selected_developer, commit_date_filter, commit_custom_start, commit_custom_end = render_commit_filters(commit_df)

    if commit_section_df.empty:
        st.info(
            "No commits match the selected filters."
        )
    else:

        commit_display = commit_section_df.copy()

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
                commit_selected_developer != "All Developers"
                and developer != commit_selected_developer
            ):
                continue

            commit_date = pd.to_datetime(
                commit.get("date"),
                errors="coerce",
                utc=True,
            )

            if commit_date_filter != "All Time" and pd.notna(commit_date):
                if commit_date_filter == "Last 7 Days":
                    latest = commit_df["Date"].dropna().max()
                    if pd.notna(latest) and commit_date < latest - pd.Timedelta(days=7):
                        continue
                elif commit_date_filter == "Last 30 Days":
                    latest = commit_df["Date"].dropna().max()
                    if pd.notna(latest) and commit_date < latest - pd.Timedelta(days=30):
                        continue
                elif commit_date_filter == "Last 90 Days":
                    latest = commit_df["Date"].dropna().max()
                    if pd.notna(latest) and commit_date < latest - pd.Timedelta(days=90):
                        continue
                elif (
                    commit_date_filter == "Custom Range"
                    and commit_custom_start is not None
                    and commit_custom_end is not None
                    and commit_custom_start <= commit_custom_end
                ):
                    start_ts = pd.Timestamp(commit_custom_start, tz="UTC")
                    end_ts = pd.Timestamp(commit_custom_end, tz="UTC") + pd.Timedelta(days=1)
                    if not (start_ts <= commit_date < end_ts):
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

    pr_section_df, pr_selected_developer, pr_date_filter, pr_custom_start, pr_custom_end = render_pr_filters(pr_df)

    if pr_section_df.empty:

        st.info(
            "No pull request data matches the selected filters."
        )

    else:

        open_prs = int(
            (
                pr_section_df["State"]
                .astype(str)
                .str.lower()
                == "open"
            ).sum()
        )

        merged_prs = int(
            pr_section_df["Merged"]
            .notna()
            .sum()
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total PRs",
            len(pr_section_df)
        )

        c2.metric(
            "Open PRs",
            open_prs
        )

        c3.metric(
            "Merged PRs",
            merged_prs
        )

        display_pr = pr_section_df.copy()

        # Use a simple serial number for dashboard display instead of the
        # actual GitHub PR number. The original "Number" value is preserved
        # in pr_section_df for reports, exports and all other functionality.
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
            pr_section_df["State"]
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
            repository_full_name(
                selected_repository,
                info
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
# REPORT TOTALS
# ============================================================

# These totals are used by the Reports & Export section.
# Keep them outside the Overview function so they remain available
# to the rest of the dashboard.

total_additions = (
    int(filtered_df["Additions"].sum())
    if not filtered_df.empty
    else 0
)

total_deletions = (
    int(filtered_df["Deletions"].sum())
    if not filtered_df.empty
    else 0
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
        else repository_full_name(
            selected_repository,
            selected_repository_info
        )
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

        "Projects": pd.DataFrame(
            [
                {
                    "Project": project.get("title", ""),
                    "Number": project.get("number", ""),
                    "Repositories": ", ".join(project.get("repositories", [])),
                    "Items": len(project.get("items", [])),
                    "URL": project.get("url", ""),
                }
                for project in (load_projects() if selected_repository == "All Repositories" else selected_projects)
                if isinstance(project, dict)
            ]
        ),

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














