from __future__ import annotations

from pathlib import Path

import pymysql
import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config" / "config.yaml"
UPLOAD_DIR = SCRIPT_DIR / "static" / "upload"


def load_db_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        cfg = yaml.safe_load(file)
    uri = cfg["database"]["uri"].replace("mysql+pymysql://", "")
    auth, rest = uri.split("@", 1)
    user, password = auth.split(":", 1)
    host_port, database = rest.split("/", 1)
    host, port = host_port.split(":", 1)
    return {
        "host": host,
        "port": int(port),
        "user": user,
        "password": password,
        "database": database.split("?", 1)[0],
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }


def main() -> None:
    conn = pymysql.connect(**load_db_config())
    prefixed_cover = 0
    nulled_isbn = 0
    deleted_rows = 0

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, cover FROM book WHERE cover IS NOT NULL AND cover <> '' AND cover NOT LIKE 'upload/%' AND cover NOT LIKE 'http%'")
            for row in cur.fetchall():
                filename = row["cover"]
                if (UPLOAD_DIR / filename).exists():
                    cur.execute("UPDATE book SET cover=%s, updatetime=NOW() WHERE id=%s", (f"upload/{filename}", row["id"]))
                    prefixed_cover += 1

            cur.execute("SELECT id, isbn FROM book WHERE isbn IS NOT NULL AND isbn <> '' AND CHAR_LENGTH(isbn) NOT IN (10, 13)")
            for row in cur.fetchall():
                cur.execute("UPDATE book SET isbn=NULL, updatetime=NOW() WHERE id=%s", (row["id"],))
                nulled_isbn += 1

            cur.execute("DELETE FROM book WHERE category_id IS NULL OR condition_id IS NULL")
            deleted_rows = cur.rowcount

        conn.commit()
        print(f"prefixed_cover={prefixed_cover}")
        print(f"nulled_isbn={nulled_isbn}")
        print(f"deleted_rows={deleted_rows}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
