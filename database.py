import json
import os
from contextlib import contextmanager
from datetime import datetime

import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "github_reporting_db"),
}

_pool = None


def initialize_pool():
    global _pool
    if _pool is not None:
        return _pool
    _pool = pooling.MySQLConnectionPool(
        pool_name="github_reporting_pool",
        pool_size=int(os.getenv("MYSQL_POOL_SIZE", "5")),
        pool_reset_session=True,
        **DB_CONFIG,
    )
    return _pool


@contextmanager
def get_connection():
    pool = initialize_pool()
    connection = pool.get_connection()
    try:
        yield connection
    finally:
        connection.close()


def _json(value):
    return json.dumps(value or [], ensure_ascii=False)


def _dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
        return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
    except ValueError:
        return None


def _date(value):
    if not value:
        return None
    text = str(value).strip()
    try:
        return datetime.strptime(text[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _repository_id(cursor, repository_name):
    cursor.execute(
        "SELECT id FROM repositories WHERE name=%s OR full_name=%s LIMIT 1",
        (repository_name, repository_name),
    )
    row = cursor.fetchone()
    return row[0] if row else None


def upsert_repository(repo):
    sql = """
        INSERT INTO repositories
        (id,name,full_name,owner,description,private,visibility,default_branch,
         html_url,clone_url,ssh_url,language,created_at,updated_at,pushed_at,
         size,stars,forks,open_issues,watchers,archived,disabled,last_synced_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        ON DUPLICATE KEY UPDATE
          name=VALUES(name), full_name=VALUES(full_name), owner=VALUES(owner),
          description=VALUES(description), private=VALUES(private), visibility=VALUES(visibility),
          default_branch=VALUES(default_branch), html_url=VALUES(html_url), clone_url=VALUES(clone_url),
          ssh_url=VALUES(ssh_url), language=VALUES(language), created_at=VALUES(created_at),
          updated_at=VALUES(updated_at), pushed_at=VALUES(pushed_at), size=VALUES(size),
          stars=VALUES(stars), forks=VALUES(forks), open_issues=VALUES(open_issues),
          watchers=VALUES(watchers), archived=VALUES(archived), disabled=VALUES(disabled),
          last_synced_at=NOW()
    """
    # Older prototype JSON files did not persist an explicit "owner" field.
    # Derive it safely from the nested owner object or full_name so migration
    # and future synchronization cannot violate repositories.owner NOT NULL.
    owner_data = repo.get("owner")
    if isinstance(owner_data, dict):
        owner = owner_data.get("login") or owner_data.get("name")
    else:
        owner = owner_data

    full_name = repo.get("full_name")
    if not owner and isinstance(full_name, str) and "/" in full_name:
        owner = full_name.split("/", 1)[0].strip()

    name = repo.get("name")
    if not full_name and owner and name:
        full_name = f"{owner}/{name}"

    if not owner:
        raise ValueError(
            f"Repository owner could not be determined for repository "
            f"{name!r}. Expected an owner field or full_name such as "
            f"'OWNER/REPOSITORY'."
        )

    values = (
        repo.get("id"), name, full_name, owner,
        repo.get("description"), bool(repo.get("private", False)), repo.get("visibility"),
        repo.get("default_branch"), repo.get("html_url"), repo.get("clone_url"),
        repo.get("ssh_url"), repo.get("language"), _dt(repo.get("created_at")),
        _dt(repo.get("updated_at")), _dt(repo.get("pushed_at")), repo.get("size", 0),
        repo.get("stars", 0), repo.get("forks", 0), repo.get("open_issues", 0),
        repo.get("watchers", 0), bool(repo.get("archived", False)),
        bool(repo.get("disabled", False)),
    )
    with get_connection() as cnx:
        cur = cnx.cursor()
        cur.execute(sql, values)
        cnx.commit()
    return repo.get("id")


def sync_commits(repository_id, commits):
    with get_connection() as cnx:
        cur = cnx.cursor()
        for commit in commits:
            sha = commit.get("sha")
            if not sha:
                continue
            author = commit.get("author") or {}
            stats = commit.get("statistics") or {}
            cur.execute(
                """
                INSERT INTO commits
                (repository_id,sha,author_login,author_name,author_email,commit_date,message,
                 additions,deletions,total_changes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                  author_login=VALUES(author_login), author_name=VALUES(author_name),
                  author_email=VALUES(author_email), commit_date=VALUES(commit_date),
                  message=VALUES(message), additions=VALUES(additions), deletions=VALUES(deletions),
                  total_changes=VALUES(total_changes)
                """,
                (repository_id, sha, author.get("name"), author.get("name"), author.get("email"),
                 _dt(commit.get("date")), commit.get("message"), int(stats.get("additions", 0) or 0),
                 int(stats.get("deletions", 0) or 0), int(stats.get("total_changes", 0) or 0)),
            )
            cur.execute("SELECT id FROM commits WHERE repository_id=%s AND sha=%s", (repository_id, sha))
            commit_id = cur.fetchone()[0]
            cur.execute("DELETE FROM commit_files WHERE commit_id=%s", (commit_id,))
            for file_data in commit.get("files", []) or []:
                cur.execute(
                    """
                    INSERT INTO commit_files
                    (commit_id,filename,status,additions,deletions,changes)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """,
                    (commit_id, file_data.get("filename", "Unknown"), file_data.get("status"),
                     int(file_data.get("additions", 0) or 0), int(file_data.get("deletions", 0) or 0),
                     int(file_data.get("changes", 0) or 0)),
                )
        cnx.commit()


def sync_pull_requests(repository_id, pull_requests):
    with get_connection() as cnx:
        cur = cnx.cursor()
        cur.execute("DELETE FROM pull_requests WHERE repository_id=%s", (repository_id,))
        for pr in pull_requests:
            cur.execute(
                """
                INSERT INTO pull_requests
                (repository_id,number,title,state,draft,merged,author_login,author_url,
                 created_at,updated_at,closed_at,merged_at,url,head_branch,base_branch)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (repository_id, pr.get("number"), pr.get("title"), pr.get("state"),
                 bool(pr.get("draft", False)), bool(pr.get("merged", False)), pr.get("author"),
                 pr.get("author_url"), _dt(pr.get("created_at")), _dt(pr.get("updated_at")),
                 _dt(pr.get("closed_at")), _dt(pr.get("merged_at")), pr.get("url"),
                 pr.get("head_branch"), pr.get("base_branch")),
            )
        cnx.commit()


def sync_issues(repository_id, issues):
    with get_connection() as cnx:
        cur = cnx.cursor()
        cur.execute("DELETE FROM issues WHERE repository_id=%s", (repository_id,))
        for issue in issues:
            cur.execute(
                """
                INSERT INTO issues
                (repository_id,number,title,state,author_login,author_url,created_at,updated_at,
                 closed_at,comments,labels,url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (repository_id, issue.get("number"), issue.get("title"), issue.get("state"),
                 issue.get("author"), issue.get("author_url"), _dt(issue.get("created_at")),
                 _dt(issue.get("updated_at")), _dt(issue.get("closed_at")), int(issue.get("comments", 0) or 0),
                 _json(issue.get("labels", [])), issue.get("url")),
            )
        cnx.commit()


def sync_branches(repository_id, branches):
    with get_connection() as cnx:
        cur = cnx.cursor()
        cur.execute("DELETE FROM branches WHERE repository_id=%s", (repository_id,))
        for branch in branches:
            cur.execute(
                """
                INSERT INTO branches
                (repository_id,name,is_default,protected,commit_sha)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (repository_id, branch.get("name"), bool(branch.get("default", False)),
                 bool(branch.get("protected", False)), branch.get("commit_sha")),
            )
        cnx.commit()


def sync_contributors(repository_id, contributors):
    with get_connection() as cnx:
        cur = cnx.cursor()
        cur.execute("DELETE FROM contributors WHERE repository_id=%s", (repository_id,))
        for user in contributors:
            cur.execute(
                """
                INSERT INTO contributors
                (repository_id,github_user_id,login,user_type,contributions,profile_url,avatar_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (repository_id, user.get("id"), user.get("login", "Unknown"), user.get("type"),
                 int(user.get("contributions", 0) or 0), user.get("profile_url"), user.get("avatar_url")),
            )
        cnx.commit()


def sync_collaborators(repository_id, collaborators):
    with get_connection() as cnx:
        cur = cnx.cursor()
        cur.execute("DELETE FROM collaborators WHERE repository_id=%s", (repository_id,))
        for user in collaborators:
            cur.execute(
                """
                INSERT INTO collaborators
                (repository_id,github_user_id,login,user_type,role_name,admin,maintain,
                 push_permission,triage,pull_permission,profile_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (repository_id, user.get("id"), user.get("login", "Unknown"), user.get("type"),
                 user.get("role_name"), bool(user.get("admin", False)), bool(user.get("maintain", False)),
                 bool(user.get("push", False)), bool(user.get("triage", False)),
                 bool(user.get("pull", False)), user.get("profile_url")),
            )
        cnx.commit()


def replace_projects(organization, projects):
    with get_connection() as cnx:
        cur = cnx.cursor()
        cur.execute("DELETE FROM projects WHERE organization=%s", (organization,))
        for project in projects:
            cur.execute(
                """
                INSERT INTO projects
                (id,organization,number,title,description,url,public,closed,updated_at,last_synced_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                """,
                (project.get("id"), organization, project.get("number"), project.get("title", "Untitled Project"),
                 project.get("description"), project.get("url"), bool(project.get("public", False)),
                 bool(project.get("closed", False)), _dt(project.get("updated_at"))),
            )
            for full_name in project.get("repositories", []) or []:
                cur.execute("SELECT id FROM repositories WHERE full_name=%s", (full_name,))
                row = cur.fetchone()
                if row:
                    cur.execute(
                        "INSERT IGNORE INTO project_repositories (project_id,repository_id) VALUES (%s,%s)",
                        (project.get("id"), row[0]),
                    )
            for item in project.get("items", []) or []:
                cur.execute(
                    """
                    INSERT INTO project_items
                    (project_id,github_item_id,item_type,title,item_number,url,repository_full_name,
                     status,due_date,priority,labels,assignees,field_values)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (project.get("id"), item.get("id"), item.get("type"), item.get("title"),
                     item.get("number"), item.get("url"), item.get("repository"), item.get("status"),
                     _date(item.get("due_date")), str(item.get("priority")) if item.get("priority") not in (None, "") else None,
                     _json(item.get("labels", [])), _json(item.get("assignees", [])), _json(item.get("field_values", {}))),
                )
        cnx.commit()


def list_repositories():
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT * FROM repositories ORDER BY LOWER(name), id")
        return cur.fetchall()


def _load_commit_rows(cur, repository_id=None):
    if repository_id is None:
        cur.execute("SELECT * FROM commits ORDER BY commit_date DESC, id DESC")
    else:
        cur.execute("SELECT * FROM commits WHERE repository_id=%s ORDER BY commit_date DESC, id DESC", (repository_id,))
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT filename,status,additions,deletions,changes FROM commit_files WHERE commit_id=%s ORDER BY id", (row["id"],))
        files = cur.fetchall()
        row["files"] = files
    return rows


def _commit_payload(row):
    return {
        "sha": row["sha"],
        "author": {"name": row.get("author_name") or row.get("author_login") or "Unknown", "email": row.get("author_email") or "Unknown"},
        "date": row.get("commit_date"),
        "message": row.get("message") or "No commit message",
        "statistics": {"additions": row.get("additions", 0), "deletions": row.get("deletions", 0), "total_changes": row.get("total_changes", 0)},
        "files": row.get("files", []),
    }


def _load_projects(cur, repository_id=None):
    if repository_id is None:
        cur.execute("SELECT * FROM projects ORDER BY LOWER(title)")
    else:
        cur.execute(
            """
            SELECT p.* FROM projects p
            JOIN project_repositories pr ON pr.project_id=p.id
            WHERE pr.repository_id=%s
            ORDER BY LOWER(p.title)
            """,
            (repository_id,),
        )
    projects = cur.fetchall()
    for project in projects:
        cur.execute("SELECT r.full_name FROM project_repositories pr JOIN repositories r ON r.id=pr.repository_id WHERE pr.project_id=%s ORDER BY r.full_name", (project["id"],))
        project["repositories"] = [r["full_name"] for r in cur.fetchall()]
        cur.execute("SELECT * FROM project_items WHERE project_id=%s ORDER BY id", (project["id"],))
        items = cur.fetchall()
        for item in items:
            for key in ("labels", "assignees", "field_values"):
                try:
                    item[key] = json.loads(item.get(key) or ("[]" if key != "field_values" else "{}"))
                except (TypeError, json.JSONDecodeError):
                    item[key] = [] if key != "field_values" else {}
            item["due_date"] = item.get("due_date").isoformat() if item.get("due_date") else None
            item["id"] = item["github_item_id"]
            item["number"] = item.get("item_number")
        project["items"] = items
        project["updated_at"] = project.get("updated_at").isoformat() if project.get("updated_at") else None
        project["public"] = bool(project.get("public"))
        project["closed"] = bool(project.get("closed"))
        project["description"] = project.get("description") or ""
    return projects


def get_repository_payload(repository_name):
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT * FROM repositories WHERE name=%s OR full_name=%s LIMIT 1", (repository_name, repository_name))
        repo = cur.fetchone()
        if not repo:
            return {"commits": [], "pull_requests": [], "issues": [], "branches": [], "repository": {}, "contributors": [], "collaborators": [], "projects": []}
        repo_id = repo["id"]
        cur.execute("SELECT * FROM pull_requests WHERE repository_id=%s ORDER BY updated_at DESC, number DESC", (repo_id,))
        prs = cur.fetchall()
        for pr in prs:
            pr["draft"] = bool(pr["draft"]); pr["merged"] = bool(pr["merged"])
        cur.execute("SELECT * FROM issues WHERE repository_id=%s ORDER BY updated_at DESC, number DESC", (repo_id,))
        issues = cur.fetchall()
        for issue in issues:
            try: issue["labels"] = json.loads(issue.get("labels") or "[]")
            except (TypeError, json.JSONDecodeError): issue["labels"] = []
        cur.execute("SELECT * FROM branches WHERE repository_id=%s ORDER BY is_default DESC, name", (repo_id,))
        branches = cur.fetchall()
        for b in branches: b["default"] = bool(b.pop("is_default")); b["protected"] = bool(b["protected"]); b["name"] = b.pop("name")
        cur.execute("SELECT * FROM contributors WHERE repository_id=%s ORDER BY contributions DESC, login", (repo_id,))
        contributors = cur.fetchall()
        for c in contributors: c["id"] = c.pop("github_user_id"); c["type"] = c.pop("user_type"); c["profile_url"] = c.pop("profile_url")
        cur.execute("SELECT * FROM collaborators WHERE repository_id=%s ORDER BY login", (repo_id,))
        collaborators = cur.fetchall()
        for c in collaborators:
            c["id"] = c.pop("github_user_id"); c["type"] = c.pop("user_type"); c["push"] = bool(c.pop("push_permission")); c["pull"] = bool(c.pop("pull_permission")); c["admin"] = bool(c["admin"]); c["maintain"] = bool(c["maintain"]); c["triage"] = bool(c["triage"])
        commits = [_commit_payload(row) for row in _load_commit_rows(cur, repo_id)]
        projects = _load_projects(cur, repo_id)
        for project in projects:
            project.pop("last_synced_at", None)
        repo.pop("last_synced_at", None)
        return {"commits": commits, "pull_requests": prs, "issues": issues, "branches": branches, "repository": repo, "contributors": contributors, "collaborators": collaborators, "projects": projects}


def get_all_commits():
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True)
        return [_commit_payload(row) for row in _load_commit_rows(cur)]


def get_all_pull_requests():
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True); cur.execute("SELECT * FROM pull_requests ORDER BY updated_at DESC, id DESC"); return cur.fetchall()


def get_all_issues():
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True); cur.execute("SELECT * FROM issues ORDER BY updated_at DESC, id DESC"); rows=cur.fetchall()
        for row in rows:
            try: row["labels"] = json.loads(row.get("labels") or "[]")
            except (TypeError, json.JSONDecodeError): row["labels"]=[]
        return rows


def get_all_branches():
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True); cur.execute("SELECT * FROM branches ORDER BY repository_id, name"); rows=cur.fetchall()
        for row in rows: row["default"] = bool(row.pop("is_default")); row["protected"] = bool(row["protected"])
        return rows


def get_all_contributors():
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True); cur.execute("SELECT * FROM contributors ORDER BY repository_id, contributions DESC"); return cur.fetchall()


def get_all_collaborators():
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True); cur.execute("SELECT * FROM collaborators ORDER BY repository_id, login"); return cur.fetchall()


def get_all_projects():
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True); return _load_projects(cur)


def begin_sync(repository_count):
    with get_connection() as cnx:
        cur=cnx.cursor(); cur.execute("INSERT INTO sync_history (started_at,status,repositories_discovered) VALUES (NOW(),'RUNNING',%s)", (repository_count,)); cnx.commit(); return cur.lastrowid


def finish_sync(sync_id, status, repositories_synced, message=None):
    with get_connection() as cnx:
        cur=cnx.cursor(); cur.execute("UPDATE sync_history SET completed_at=NOW(),status=%s,repositories_synced=%s,message=%s WHERE id=%s", (status,repositories_synced,message,sync_id)); cnx.commit()


def test_connection():
    with get_connection() as cnx:
        cur=cnx.cursor(); cur.execute("SELECT 1"); return cur.fetchone()[0] == 1

# Compatibility/query helpers used by app.py.
def repository_id_by_name(repository_name):
    with get_connection() as cnx:
        cur = cnx.cursor()
        cur.execute("SELECT id FROM repositories WHERE name=%s OR full_name=%s LIMIT 1", (repository_name, repository_name))
        row = cur.fetchone()
        return row[0] if row else None


def get_repository_commits(repository_id):
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True)
        return [_commit_payload(row) for row in _load_commit_rows(cur, repository_id)]


def count_projects_for_repository(repository_name):
    with get_connection() as cnx:
        cur = cnx.cursor()
        cur.execute(
            """
            SELECT COUNT(*) FROM project_repositories pr
            JOIN repositories r ON r.id=pr.repository_id
            WHERE r.name=%s OR r.full_name=%s
            """,
            (repository_name, repository_name),
        )
        return int(cur.fetchone()[0])


def repository_index_rows():
    with get_connection() as cnx:
        cur = cnx.cursor(dictionary=True)
        cur.execute(
            """
            SELECT
                r.id, r.name, r.full_name, r.owner, r.private, r.visibility,
                r.default_branch, r.html_url, r.description, r.updated_at, r.pushed_at,
                (SELECT COUNT(*) FROM commits c WHERE c.repository_id=r.id) AS commits,
                (SELECT COUNT(*) FROM pull_requests p WHERE p.repository_id=r.id) AS pull_requests,
                (SELECT COUNT(*) FROM issues i WHERE i.repository_id=r.id) AS issues,
                (SELECT COUNT(*) FROM branches b WHERE b.repository_id=r.id) AS branches,
                (SELECT COUNT(*) FROM contributors c2 WHERE c2.repository_id=r.id) AS contributors,
                (SELECT COUNT(*) FROM collaborators c3 WHERE c3.repository_id=r.id) AS collaborators,
                (SELECT COUNT(*) FROM project_repositories pr WHERE pr.repository_id=r.id) AS projects
            FROM repositories r
            ORDER BY LOWER(r.name)
            """
        )
        return cur.fetchall()