import argparse
import os
import sys
import psycopg2
import psycopg2.extras

def process_file(filename: str, title: str) -> None:    
    print(f"Processing file {filename} 🧙")

    _, ext = os.path.splitext(filename)
    if ext.lower() not in {".md", ".markdown"}:
        print(f"Error: file '{filename}' does not look like a Markdown file.", file=sys.stderr)
        raise SystemExit(2)
    try:
        with open(filename, "r", encoding="utf-8") as fh:
            content = fh.read()
    except FileNotFoundError:
        print(f"Error: file '{filename}' not found.", file=sys.stderr)
        raise SystemExit(2)
    except OSError as exc:
        print(f"Error reading '{filename}': {exc}", file=sys.stderr)
        raise SystemExit(2)

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: environment variable DATABASE_URL is not set.", file=sys.stderr)
        raise SystemExit(2)

    try:
        conn = psycopg2.connect(dsn=db_url)

        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO posts (title, content)
                    VALUES (%s, %s)
                    RETURNING id, created_at
                    """,
                    (title, content),
                )
                row = cur.fetchone()
                inserted_id = row["id"] if row and "id" in row else None
                created_at = row["created_at"] if row and "created_at" in row else None
                print(f"Inserted post id={inserted_id} created_at={created_at}")
    except psycopg2.Error as exc:
        print(f"Database error: {exc}", file=sys.stderr)
        raise SystemExit(3)


def create_parser():
    parser = argparse.ArgumentParser(
        prog="bloisdev_cli",
        description="Bloisdev CLI 🧙",
        epilog="Publish content to Bloisdev",
    )

    parser.add_argument("filename", help="The Markdown file to be processed")
    parser.add_argument("--title", "-t", required=True, help="Title to store in the database")

    return parser


def main() -> int:
    parser = create_parser()
    arguments = parser.parse_args()

    filename = arguments.filename
    title = arguments.title

    process_file(filename, title)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())