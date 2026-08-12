import os
import json
import requests
from dotenv import load_dotenv


# ============================================================
# GitHub Organization Audit Log Test
# ============================================================

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
ORGANIZATION = "ICPOC1"

URL = f"https://api.github.com/orgs/{ORGANIZATION}/audit-log"


HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2026-03-10"
}


print()
print("=" * 80)
print("GITHUB ORGANIZATION AUDIT LOG ACCESS TEST")
print("=" * 80)

print()
print(f"Organization : {ORGANIZATION}")
print("Endpoint     : /orgs/ICPOC1/audit-log")
print()


if not TOKEN:

    print("ERROR: GITHUB_TOKEN was not found.")
    print()
    print("Check your .env file.")
    raise SystemExit(1)


try:

    response = requests.get(
        URL,
        headers=HEADERS,
        params={
            "include": "all",
            "per_page": 10
        },
        timeout=30
    )


except requests.RequestException as error:

    print("ERROR: Could not connect to GitHub.")
    print(error)
    raise SystemExit(1)


print(f"HTTP Status : {response.status_code}")
print()


try:

    data = response.json()

except ValueError:

    print("GitHub returned invalid JSON.")
    print(response.text)
    raise SystemExit(1)


# ============================================================
# SUCCESS
# ============================================================

if response.status_code == 200:

    print("=" * 80)
    print("SUCCESS")
    print("=" * 80)

    print()
    print("Organization audit-log access is working.")
    print()

    if isinstance(data, list):

        print(
            f"Audit events received: {len(data)}"
        )

        print()

        for index, event in enumerate(
            data,
            start=1
        ):

            print("-" * 80)

            print(
                f"Event #{index}"
            )

            print(
                "Actor      :",
                event.get(
                    "actor",
                    "Unknown"
                )
            )

            print(
                "Action     :",
                event.get(
                    "action",
                    "Unknown"
                )
            )

            print(
                "Repository :",
                event.get(
                    "repo",
                    "N/A"
                )
            )

            print(
                "Timestamp  :",
                event.get(
                    "@timestamp",
                    "Unknown"
                )
            )

            print(
                "Created At :",
                event.get(
                    "created_at",
                    "Unknown"
                )
            )

    else:

        print(
            "Unexpected response format:"
        )

        print(
            json.dumps(
                data,
                indent=4
            )
        )


# ============================================================
# FORBIDDEN
# ============================================================

elif response.status_code == 403:

    print("=" * 80)
    print("AUDIT LOG ACCESS DENIED")
    print("=" * 80)

    print()

    print(
        "GitHub returned HTTP 403."
    )

    print()

    print(
        json.dumps(
            data,
            indent=4
        )
    )

    print()

    print("Possible causes:")
    print("1. Organization Administration permission is missing.")
    print("2. Fine-grained PAT requires organization approval.")
    print("3. PAT was not updated successfully.")
    print("4. Organization policy restricts PAT access.")
    print("5. Token being used by .env is not the updated token.")


# ============================================================
# NOT FOUND
# ============================================================

elif response.status_code == 404:

    print("=" * 80)
    print("ORGANIZATION / AUDIT LOG NOT FOUND")
    print("=" * 80)

    print()

    print(
        json.dumps(
            data,
            indent=4
        )
    )

    print()

    print(
        "Check that the organization name is exactly:"
    )

    print(
        "ICPOC1"
    )


# ============================================================
# OTHER ERROR
# ============================================================

else:

    print("=" * 80)
    print("GITHUB API REQUEST FAILED")
    print("=" * 80)

    print()

    print(
        json.dumps(
            data,
            indent=4
        )
    )

print()
print("=" * 80)
print("AUDIT LOG TEST FINISHED")
print("=" * 80)
print()