#!/usr/bin/env -S uv run python

import os
import sys
import subprocess
import psycopg2

PLACEHOLDER = "{{org}}"


def main():
    if len(sys.argv) < 2:
        print(f'Uso: python {sys.argv[0]} "comando con {PLACEHOLDER}"', file=sys.stderr)
        sys.exit(1)

    command_template = sys.argv[1]

    if PLACEHOLDER not in command_template:
        print(
            f"ERROR: el comando debe contener el placeholder {PLACEHOLDER}",
            file=sys.stderr,
        )
        sys.exit(1)

    db_url = os.getenv("POSTGRES_URL")
    if not db_url:
        print("ERROR: POSTGRES_URL no está definida", file=sys.stderr)
        sys.exit(1)

    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM shared.organizations ORDER BY name;")
            orgs = [row[0] for row in cur.fetchall()]
    finally:
        conn.close()

    for org in orgs:
        cmd = command_template.replace(PLACEHOLDER, org)
        print(f">>> Ejecutando: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print(f"ERROR ejecutando para org={org}", file=sys.stderr)
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
