import database as db


def main():
    print("=" * 70)
    print("MYSQL CONNECTION TEST")
    print("=" * 70)
    db.test_connection()
    print("MySQL connection: PASSED")
    repositories = db.list_repositories()
    print(f"Repositories in MySQL: {len(repositories)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
