"""One-time migration from the prototype JSON data to MySQL.

This migration preserves the existing JSON files. It normalizes older
repository records before inserting them into MySQL, including deriving
repositories.owner from full_name when the prototype JSON does not contain
an explicit owner field.
"""

import json
import os
from pathlib import Path

import database as db

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPOSITORIES_DIR = DATA_DIR / "repositories"


def read_json(path, default):
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"WARNING: Could not read {path}: {error}")
        return default


def normalize_repository(repository, folder_name):
    """Normalize repository metadata from old and new JSON formats."""
    if not isinstance(repository, dict):
        repository = {}

    owner_data = repository.get("owner")

    if isinstance(owner_data, dict):
        owner = owner_data.get("login") or owner_data.get("name")
    else:
        owner = owner_data

    owner = str(owner).strip() if owner else ""

    full_name = repository.get("full_name")
    full_name = str(full_name).strip() if full_name else ""

    # The prototype JSON stores full_name even though older repository.json
    # files do not always contain a separate owner property.
    if not owner and "/" in full_name:
        owner = full_name.split("/", 1)[0].strip()

    name = repository.get("name")
    name = str(name).strip() if name else str(folder_name).strip()

    if not full_name and owner and name:
        full_name = f"{owner}/{name}"

    if not owner:
        owner = os.getenv("GITHUB_REPO_OWNER") or os.getenv("GITHUB_OWNER") or ""

    if not owner:
        raise ValueError(
            f"Could not determine owner for repository {name!r}. "
            "The repository JSON must contain owner or full_name."
        )

    if not full_name:
        full_name = f"{owner}/{name}"

    normalized = dict(repository)
    normalized["name"] = name
    normalized["owner"] = owner
    normalized["full_name"] = full_name

    return normalized


def migrate_repository(folder):
    repository_raw = read_json(folder / "repository.json", {})

    if not repository_raw.get("id"):
        print(f"Skipping {folder.name}: repository.json has no GitHub id.")
        return False

    try:
        repository = normalize_repository(repository_raw, folder.name)
    except ValueError as error:
        print(f"ERROR: {error}")
        return False

    print(
        f"Migrating repository: {repository['full_name']} "
        f"(GitHub ID: {repository['id']})"
    )

    db.upsert_repository(repository)

    repository_id = db.repository_id_by_name(
        repository["full_name"]
    )

    if repository_id is None:
        print(
            f"ERROR: Could not find MySQL repository row for "
            f"{repository['full_name']}."
        )
        return False

    commits_data = read_json(folder / "commits.json", {})
    prs_data = read_json(folder / "pull_requests.json", {})
    issues_data = read_json(folder / "issues.json", {})
    branches_data = read_json(folder / "branches.json", {})
    contributors_data = read_json(folder / "contributors.json", {})
    collaborators_data = read_json(folder / "collaborators.json", {})

    commits = (
        commits_data.get("commits", [])
        if isinstance(commits_data, dict)
        else []
    )
    prs = (
        prs_data.get("pull_requests", [])
        if isinstance(prs_data, dict)
        else []
    )
    issues = (
        issues_data.get("issues", [])
        if isinstance(issues_data, dict)
        else []
    )
    branches = (
        branches_data.get("branches", [])
        if isinstance(branches_data, dict)
        else []
    )
    contributors = (
        contributors_data.get("contributors", [])
        if isinstance(contributors_data, dict)
        else []
    )
    collaborators = (
        collaborators_data.get("collaborators", [])
        if isinstance(collaborators_data, dict)
        else []
    )

    db.sync_commits(repository_id, commits)
    db.sync_pull_requests(repository_id, prs)
    db.sync_issues(repository_id, issues)
    db.sync_branches(repository_id, branches)
    db.sync_contributors(repository_id, contributors)
    db.sync_collaborators(repository_id, collaborators)

    print(
        f"  Commits: {len(commits)} | "
        f"PRs: {len(prs)} | "
        f"Issues: {len(issues)} | "
        f"Branches: {len(branches)} | "
        f"Contributors: {len(contributors)} | "
        f"Collaborators: {len(collaborators)}"
    )
    print(f"  Migrated successfully: {repository['full_name']}")
    return True


def migrate_projects():
    """Migrate the organization-level Projects V2 JSON."""
    data = read_json(DATA_DIR / "projects.json", {"projects": []})

    if not isinstance(data, dict):
        data = {"projects": []}

    projects = data.get("projects", [])
    if not isinstance(projects, list):
        projects = []

    organization = (
        data.get("organization")
        or os.getenv("GITHUB_OWNER")
        or os.getenv("GITHUB_REPO_OWNER")
        or "ICPOC1"
    )

    db.replace_projects(organization, projects)

    print(f"Migrated Projects V2: {len(projects)}")


def main():
    print("=" * 80)
    print("JSON -> MYSQL ONE-TIME MIGRATION")
    print("=" * 80)
    print(f"Source: {REPOSITORIES_DIR}")

    if not REPOSITORIES_DIR.exists():
        raise SystemExit(
            "ERROR: data/repositories was not found."
        )

    if not db.test_connection():
        raise SystemExit(
            "ERROR: MySQL connection test failed."
        )

    migrated = 0
    failed = 0

    folders = sorted(
        folder
        for folder in REPOSITORIES_DIR.iterdir()
        if folder.is_dir()
    )

    print(f"Repositories found: {len(folders)}")
    print()

    for folder in folders:
        try:
            if migrate_repository(folder):
                migrated += 1
            else:
                failed += 1
        except Exception as error:
            failed += 1
            print(
                f"ERROR migrating {folder.name}: "
                f"{type(error).__name__}: {error}"
            )

    try:
        migrate_projects()
    except Exception as error:
        print(
            f"ERROR migrating Projects V2: "
            f"{type(error).__name__}: {error}"
        )
        failed += 1

    print()
    print("=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print(f"Repositories found : {len(folders)}")
    print(f"Repositories OK    : {migrated}")
    print(f"Repositories failed: {failed}")
    print()
    print("JSON files were NOT modified or deleted.")
    print("=" * 80)

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()