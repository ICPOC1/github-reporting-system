CREATE DATABASE IF NOT EXISTS github_reporting_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE github_reporting_db;

CREATE TABLE IF NOT EXISTS repositories (
    id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(512) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    description TEXT NULL,
    private TINYINT(1) NOT NULL DEFAULT 0,
    visibility VARCHAR(50) NULL,
    default_branch VARCHAR(255) NULL,
    html_url VARCHAR(1024) NULL,
    clone_url VARCHAR(1024) NULL,
    ssh_url VARCHAR(1024) NULL,
    language VARCHAR(100) NULL,
    created_at DATETIME NULL,
    updated_at DATETIME NULL,
    pushed_at DATETIME NULL,
    size BIGINT NULL DEFAULT 0,
    stars INT NULL DEFAULT 0,
    forks INT NULL DEFAULT 0,
    open_issues INT NULL DEFAULT 0,
    watchers INT NULL DEFAULT 0,
    archived TINYINT(1) NOT NULL DEFAULT 0,
    disabled TINYINT(1) NOT NULL DEFAULT 0,
    last_synced_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_repositories_full_name (full_name),
    KEY idx_repositories_owner (owner),
    KEY idx_repositories_updated_at (updated_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS commits (
    id BIGINT NOT NULL AUTO_INCREMENT,
    repository_id BIGINT NOT NULL,
    sha VARCHAR(40) NOT NULL,
    author_login VARCHAR(255) NULL,
    author_name VARCHAR(255) NULL,
    author_email VARCHAR(320) NULL,
    commit_date DATETIME NULL,
    message TEXT NULL,
    additions INT NOT NULL DEFAULT 0,
    deletions INT NOT NULL DEFAULT 0,
    total_changes INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_commit_repository_sha (repository_id, sha),
    KEY idx_commits_repository_date (repository_id, commit_date),
    KEY idx_commits_author (author_login),
    CONSTRAINT fk_commits_repository
        FOREIGN KEY (repository_id) REFERENCES repositories(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS commit_files (
    id BIGINT NOT NULL AUTO_INCREMENT,
    commit_id BIGINT NOT NULL,
    filename VARCHAR(1024) NOT NULL,
    status VARCHAR(50) NULL,
    additions INT NOT NULL DEFAULT 0,
    deletions INT NOT NULL DEFAULT 0,
    changes INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_commit_files_commit (commit_id),
    CONSTRAINT fk_commit_files_commit
        FOREIGN KEY (commit_id) REFERENCES commits(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pull_requests (
    id BIGINT NOT NULL AUTO_INCREMENT,
    repository_id BIGINT NOT NULL,
    number INT NOT NULL,
    title TEXT NULL,
    state VARCHAR(30) NULL,
    draft TINYINT(1) NOT NULL DEFAULT 0,
    merged TINYINT(1) NOT NULL DEFAULT 0,
    author_login VARCHAR(255) NULL,
    author_url VARCHAR(1024) NULL,
    created_at DATETIME NULL,
    updated_at DATETIME NULL,
    closed_at DATETIME NULL,
    merged_at DATETIME NULL,
    url VARCHAR(1024) NULL,
    head_branch VARCHAR(255) NULL,
    base_branch VARCHAR(255) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_pr_repository_number (repository_id, number),
    KEY idx_pr_repository_updated (repository_id, updated_at),
    KEY idx_pr_author (author_login),
    CONSTRAINT fk_pr_repository
        FOREIGN KEY (repository_id) REFERENCES repositories(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS issues (
    id BIGINT NOT NULL AUTO_INCREMENT,
    repository_id BIGINT NOT NULL,
    number INT NOT NULL,
    title TEXT NULL,
    state VARCHAR(30) NULL,
    author_login VARCHAR(255) NULL,
    author_url VARCHAR(1024) NULL,
    created_at DATETIME NULL,
    updated_at DATETIME NULL,
    closed_at DATETIME NULL,
    comments INT NOT NULL DEFAULT 0,
    labels JSON NULL,
    url VARCHAR(1024) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_issue_repository_number (repository_id, number),
    KEY idx_issues_repository_updated (repository_id, updated_at),
    KEY idx_issues_author (author_login),
    CONSTRAINT fk_issues_repository
        FOREIGN KEY (repository_id) REFERENCES repositories(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS branches (
    id BIGINT NOT NULL AUTO_INCREMENT,
    repository_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_default TINYINT(1) NOT NULL DEFAULT 0,
    protected TINYINT(1) NOT NULL DEFAULT 0,
    commit_sha VARCHAR(40) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_branch_repository_name (repository_id, name),
    KEY idx_branches_repository (repository_id),
    CONSTRAINT fk_branches_repository
        FOREIGN KEY (repository_id) REFERENCES repositories(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS contributors (
    id BIGINT NOT NULL AUTO_INCREMENT,
    repository_id BIGINT NOT NULL,
    github_user_id BIGINT NULL,
    login VARCHAR(255) NOT NULL,
    user_type VARCHAR(50) NULL,
    contributions INT NOT NULL DEFAULT 0,
    profile_url VARCHAR(1024) NULL,
    avatar_url VARCHAR(1024) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_contributor_repository_login (repository_id, login),
    KEY idx_contributors_login (login),
    CONSTRAINT fk_contributors_repository
        FOREIGN KEY (repository_id) REFERENCES repositories(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS collaborators (
    id BIGINT NOT NULL AUTO_INCREMENT,
    repository_id BIGINT NOT NULL,
    github_user_id BIGINT NULL,
    login VARCHAR(255) NOT NULL,
    user_type VARCHAR(50) NULL,
    role_name VARCHAR(100) NULL,
    admin TINYINT(1) NOT NULL DEFAULT 0,
    maintain TINYINT(1) NOT NULL DEFAULT 0,
    push_permission TINYINT(1) NOT NULL DEFAULT 0,
    triage TINYINT(1) NOT NULL DEFAULT 0,
    pull_permission TINYINT(1) NOT NULL DEFAULT 0,
    profile_url VARCHAR(1024) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_collaborator_repository_login (repository_id, login),
    KEY idx_collaborators_login (login),
    CONSTRAINT fk_collaborators_repository
        FOREIGN KEY (repository_id) REFERENCES repositories(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(100) NOT NULL,
    organization VARCHAR(255) NOT NULL,
    number INT NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NULL,
    url VARCHAR(1024) NULL,
    public TINYINT(1) NOT NULL DEFAULT 0,
    closed TINYINT(1) NOT NULL DEFAULT 0,
    updated_at DATETIME NULL,
    last_synced_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_project_org_number (organization, number),
    KEY idx_projects_organization (organization)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS project_repositories (
    project_id VARCHAR(100) NOT NULL,
    repository_id BIGINT NOT NULL,
    PRIMARY KEY (project_id, repository_id),
    CONSTRAINT fk_project_repositories_project
        FOREIGN KEY (project_id) REFERENCES projects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_project_repositories_repository
        FOREIGN KEY (repository_id) REFERENCES repositories(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS project_items (
    id BIGINT NOT NULL AUTO_INCREMENT,
    project_id VARCHAR(100) NOT NULL,
    github_item_id VARCHAR(150) NOT NULL,
    item_type VARCHAR(50) NULL,
    title TEXT NULL,
    item_number INT NULL,
    url VARCHAR(1024) NULL,
    repository_full_name VARCHAR(512) NULL,
    status VARCHAR(255) NULL,
    due_date DATE NULL,
    priority VARCHAR(255) NULL,
    labels JSON NULL,
    assignees JSON NULL,
    field_values JSON NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_project_item (project_id, github_item_id),
    KEY idx_project_items_project (project_id),
    KEY idx_project_items_repository (repository_full_name),
    KEY idx_project_items_status (status),
    KEY idx_project_items_priority (priority),
    CONSTRAINT fk_project_items_project
        FOREIGN KEY (project_id) REFERENCES projects(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sync_history (
    id BIGINT NOT NULL AUTO_INCREMENT,
    started_at DATETIME NOT NULL,
    completed_at DATETIME NULL,
    status VARCHAR(30) NOT NULL,
    repositories_discovered INT NOT NULL DEFAULT 0,
    repositories_synced INT NOT NULL DEFAULT 0,
    message TEXT NULL,
    PRIMARY KEY (id),
    KEY idx_sync_history_started (started_at)
) ENGINE=InnoDB;
