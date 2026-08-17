import os
import requests
from dotenv import load_dotenv


# ============================================================
# GitHub Organization Projects V2 Access Test
# ============================================================

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

# The Projects belong to the ICPOC1 organization.
ORG = "ICPOC1"


# ============================================================
# Token validation
# ============================================================

if not TOKEN:
    raise SystemExit(
        "ERROR: GITHUB_TOKEN is empty. Set it in .env first."
    )


# ============================================================
# GitHub API configuration
# ============================================================

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2026-03-10",
}


GRAPHQL_URL = "https://api.github.com/graphql"


# ============================================================
# GraphQL query
# ============================================================

QUERY = """
query($login: String!) {

    organization(login: $login) {

        projectsV2(first: 100) {

            nodes {

                id
                number
                title
                url
                shortDescription

                repositories(first: 100) {

                    nodes {
                        nameWithOwner
                    }

                }
            }
        }
    }
}
"""


# ============================================================
# Request Projects
# ============================================================

try:

    response = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        json={
            "query": QUERY,
            "variables": {
                "login": ORG
            }
        },
        timeout=30
    )

except requests.RequestException as error:

    print()
    print("=" * 80)
    print("GITHUB CONNECTION ERROR")
    print("=" * 80)
    print()

    print(error)

    raise SystemExit(1)


# ============================================================
# HTTP response
# ============================================================

print()
print("=" * 80)
print("GITHUB ORGANIZATION PROJECTS V2 ACCESS TEST")
print("=" * 80)

print()
print(f"Organization : {ORG}")
print(f"Endpoint     : {GRAPHQL_URL}")
print()

print(
    f"HTTP Status  : {response.status_code}"
)

print()


# ============================================================
# Parse response
# ============================================================

try:

    payload = response.json()

except ValueError:

    print("ERROR: GitHub returned invalid JSON.")
    print()

    print(response.text)

    raise SystemExit(1)


# ============================================================
# Check GraphQL errors
# ============================================================

if response.status_code != 200:

    print("=" * 80)
    print("GITHUB API REQUEST FAILED")
    print("=" * 80)

    print()

    print(payload)

    raise SystemExit(1)


if payload.get("errors"):

    print("=" * 80)
    print("GITHUB GRAPHQL ERROR")
    print("=" * 80)

    print()

    for error in payload["errors"]:

        print(
            error.get(
                "message",
                "Unknown GraphQL error"
            )
        )

    print()

    print("Full response:")

    print(payload)

    raise SystemExit(1)


# ============================================================
# Extract organization
# ============================================================

organization = payload.get(
    "data",
    {}
).get(
    "organization"
)


if not organization:

    print("=" * 80)
    print("ORGANIZATION NOT FOUND OR NOT ACCESSIBLE")
    print("=" * 80)

    print()

    print(f"Organization: {ORG}")

    print()

    print("GitHub response:")

    print(payload)

    raise SystemExit(1)


# ============================================================
# Extract Projects
# ============================================================

projects_data = organization.get(
    "projectsV2"
) or {}


projects = projects_data.get(
    "nodes"
) or []


# Remove possible null project entries.
projects = [
    project
    for project in projects
    if project
]


# ============================================================
# Display project summary
# ============================================================

print("=" * 80)
print("PROJECT ACCESS SUCCESSFUL")
print("=" * 80)

print()

print(
    f"Organization       : {ORG}"
)

print(
    f"Projects returned  : {len(projects)}"
)

print()


# ============================================================
# No projects
# ============================================================

if not projects:

    print("No Projects V2 were found for this organization.")

    print()

    print("=" * 80)
    print("PROJECT ACCESS TEST PASSED")
    print("=" * 80)

    raise SystemExit(0)


# ============================================================
# Display every project
# ============================================================

for index, project in enumerate(
    projects,
    start=1
):

    print("-" * 80)

    print(
        f"PROJECT #{index}"
    )

    print("-" * 80)

    print(
        "Project ID          :",
        project.get(
            "id",
            "Unknown"
        )
    )

    print(
        "Project Number      :",
        project.get(
            "number",
            "Unknown"
        )
    )

    print(
        "Project Title       :",
        project.get(
            "title",
            "Unknown"
        )
    )

    print(
        "Project Description :",
        project.get(
            "shortDescription"
        ) or "None"
    )

    print(
        "Project URL         :",
        project.get(
            "url",
            "Unknown"
        )
    )

    # --------------------------------------------------------
    # Repository information
    # --------------------------------------------------------

    repositories_data = project.get(
        "repositories"
    )

    repositories = []

    if isinstance(
        repositories_data,
        dict
    ):

        repository_nodes = (
            repositories_data.get(
                "nodes"
            )
            or []
        )

        for repository in repository_nodes:

            if not repository:
                continue

            repository_name = repository.get(
                "nameWithOwner"
            )

            if repository_name:

                repositories.append(
                    repository_name
                )

    # --------------------------------------------------------
    # Display repositories
    # --------------------------------------------------------

    if repositories:

        print(
            "Linked repositories  :"
        )

        for repository in repositories:

            print(
                f"  - {repository}"
            )

    else:

        print(
            "Linked repositories  : None"
        )

    print()


# ============================================================
# Final result
# ============================================================

print("=" * 80)
print("PROJECT ACCESS TEST PASSED")
print("=" * 80)

print()

print(
    f"Successfully accessed {len(projects)} "
    f"Projects V2 from organization {ORG}."
)

print()