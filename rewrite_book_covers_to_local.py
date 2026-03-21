"""
Rewrite curated seed data and database book covers to local static assets.

This avoids broken remote cover links by storing stable `upload/...` paths.
"""
from __future__ import annotations

import csv
from pathlib import Path
from urllib.parse import urlparse

import pymysql
import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "data" / "verified_books_seed.csv"
CONFIG_PATH = SCRIPT_DIR / "config" / "config.yaml"


EXACT_TITLE_COVERS = {
    "Introduction to Algorithms": "upload/algorithm.jpg",
    "Algorithms": "upload/algorithm.jpg",
    "Computer Systems: A Programmer's Perspective": "upload/csapp.jpg",
    "Effective Java": "upload/java.jpg",
    "Head First Java": "upload/java.jpg",
    "JavaScript: The Good Parts": "upload/js.jpg",
    "Eloquent JavaScript": "upload/js.jpg",
    "JavaScript: The Definitive Guide": "upload/js.jpg",
    "Learning React": "upload/js.jpg",
    "Database System Concepts": "upload/mysql.jpg",
    "Database Management Systems": "upload/mysql.jpg",
    "Learning SQL": "upload/mysql.jpg",
    "Deep Learning": "upload/gene.jpg",
    "Deep Learning with Python": "upload/python.jpg",
    "Python Crash Course": "upload/python.jpg",
    "Python for Data Analysis": "upload/python.jpg",
    "Learning Python": "upload/python.jpg",
    "Fluent Python": "upload/python.jpg",
    "Automate the Boring Stuff with Python": "upload/python.jpg",
    "Operating System Concepts": "upload/linux.jpg",
    "Modern Operating Systems": "upload/linux.jpg",
    "The UNIX Programming Environment": "upload/linux.jpg",
    "Computer Networks": "upload/linux.jpg",
    "Compilers: Principles Techniques and Tools": "upload/datastructure.jpg",
    "Structure and Interpretation of Computer Programs": "upload/datastructure.jpg",
    "The C Programming Language": "upload/datastructure.jpg",
    "Clean Code: A Handbook of Agile Software Craftsmanship": "upload/design.jpg",
    "Clean Architecture": "upload/design.jpg",
    "The Clean Coder": "upload/design.jpg",
    "Design Patterns: Elements of Reusable Object-Oriented Software": "upload/design.jpg",
    "Head First Design Patterns": "upload/design.jpg",
    "The Design of Everyday Things": "upload/design.jpg",
    "Refactoring: Improving the Design of Existing Code": "upload/design.jpg",
    "Artificial Intelligence: A Modern Approach": "upload/gene.jpg",
    "Introduction to Machine Learning with Python": "upload/gene.jpg",
    "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow": "upload/gene.jpg",
    "Cracking the Coding Interview": "upload/thinking.jpg",
    "The Pragmatic Programmer": "upload/design.jpg",
    "The Practice of Programming": "upload/design.jpg",
    "Continuous Delivery": "upload/design.jpg",
    "Designing Data-Intensive Applications": "upload/mysql.jpg",
    "Site Reliability Engineering": "upload/linux.jpg",
    "The DevOps Handbook": "upload/linux.jpg",
    "Kubernetes: Up and Running": "upload/linux.jpg",
    "Computer Architecture: A Quantitative Approach": "upload/csapp.jpg",
    "Computer Organization and Design: The Hardware Software Interface": "upload/csapp.jpg",
    "Introduction to the Theory of Computation": "upload/datastructure.jpg",
    "HTML and CSS: Design and Build Websites": "upload/design.jpg",
    "CSS: The Definitive Guide": "upload/design.jpg",
    "Sapiens": "upload/sapiens.jpg",
    "Guns Germs and Steel": "upload/guns.jpg",
    "Thinking Fast and Slow": "upload/thinking.jpg",
}

CATEGORY_DEFAULT_COVERS = {
    "计算机": "upload/datastructure.jpg",
    "历史": "upload/history.jpg",
    "经济": "upload/economics.jpg",
    "艺术": "upload/art.jpg",
    "哲学": "upload/philosophy.jpg",
    "科学": "upload/origin.jpg",
    "文学": "upload/ordinary.jpg",
    "教育": "upload/education.jpg",
}


def load_db_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        cfg = yaml.safe_load(file)
    db_uri = cfg["database"]["uri"].replace("mysql+pymysql://", "")
    auth, rest = db_uri.split("@", 1)
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
    }


def choose_local_cover(title: str, category: str) -> str:
    if title in EXACT_TITLE_COVERS:
        return EXACT_TITLE_COVERS[title]
    return CATEGORY_DEFAULT_COVERS.get(category, "upload/datastructure.jpg")


def rewrite_csv() -> list[tuple[str, str]]:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
        fieldnames = list(rows[0].keys())

    updates: list[tuple[str, str]] = []
    for row in rows:
        old_cover = (row.get("cover_url") or "").strip()
        local_cover = choose_local_cover(row["title"], row["category"])
        if old_cover and not old_cover.startswith("upload/"):
            row["fallback_cover_url"] = old_cover
        row["cover_url"] = local_cover
        updates.append((row["isbn"], local_cover))

    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return updates


def update_database(updates: list[tuple[str, str]]) -> int:
    conn = pymysql.connect(**load_db_config())
    try:
        with conn.cursor() as cur:
            affected = 0
            for isbn, cover in updates:
                cur.execute("UPDATE book SET cover=%s, updatetime=NOW() WHERE isbn=%s", (cover, isbn))
                affected += cur.rowcount
        conn.commit()
        return affected
    finally:
        conn.close()


def main() -> None:
    updates = rewrite_csv()
    affected = update_database(updates)
    print(f"csv_updated={len(updates)}")
    print(f"db_updated={affected}")


if __name__ == "__main__":
    main()
