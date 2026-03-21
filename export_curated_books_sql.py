from __future__ import annotations

import csv
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CSV_FILES = [
    SCRIPT_DIR / "data" / "verified_books_seed.csv",
    SCRIPT_DIR / "data" / "online_books_batch_20260321.csv",
    SCRIPT_DIR / "data" / "general_books_batch_20260321.csv",
]
OUTPUT_SQL = SCRIPT_DIR.parent / "db" / "seed_curated_books.sql"

CATEGORY_IDS = {
    "文学": 1,
    "计算机": 2,
    "历史": 3,
    "哲学": 4,
    "经济": 5,
    "教育": 6,
    "艺术": 7,
    "科学": 8,
}

CONDITION_IDS = {
    "全新": 1,
    "九成新": 2,
    "八成新": 3,
    "七成新": 4,
    "六成及以下": 5,
}


def sql_string(value: str | None) -> str:
    if value is None or value == "":
        return "NULL"
    escaped = value.replace("\\", "\\\\").replace("'", "''")
    return f"'{escaped}'"


def sql_decimal(value: str | None) -> str:
    if value is None or value == "":
        return "NULL"
    return value


def sql_int(value: str | None, default: int | None = None) -> str:
    if value is None or value == "":
        return "NULL" if default is None else str(default)
    return str(int(value))


def load_rows() -> list[dict[str, str]]:
    seen: dict[str, dict[str, str]] = {}
    for csv_file in CSV_FILES:
        with csv_file.open("r", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                seen[row["isbn"]] = row
    return list(seen.values())


def build_values(row: dict[str, str]) -> str:
    category_id = CATEGORY_IDS[row["category"]]
    condition_id = CONDITION_IDS[row["condition"]]
    seller_id = int(row["seller_id"]) if row.get("seller_id") else 1
    return "(" + ", ".join(
        [
            sql_string(row["isbn"]),
            sql_string(row["title"]),
            sql_string(row.get("author")),
            sql_string(row.get("cover_url")),
            sql_string(row.get("publisher")),
            sql_string(row.get("description")),
            str(category_id),
            str(condition_id),
            str(seller_id),
            sql_decimal(row.get("price")),
            sql_decimal(row.get("original_price")),
            sql_int(row.get("stock"), 1),
            sql_int(row.get("status"), 1),
        ]
    ) + ")"


def generate_sql(rows: list[dict[str, str]]) -> str:
    header = [
        "USE `secondhand_books`;",
        "",
        "-- Curated books batch generated from CSV sources.",
        "-- Safe to run repeatedly because it upserts by unique `isbn`.",
        "",
        "INSERT INTO `book` (",
        "  `isbn`, `title`, `author`, `cover`, `publisher`, `description`,",
        "  `category_id`, `condition_id`, `seller_id`, `price`,",
        "  `original_price`, `stock`, `status`",
        ") VALUES",
    ]
    values = [build_values(row) for row in rows]
    footer = [
        "ON DUPLICATE KEY UPDATE",
        "  `title` = VALUES(`title`),",
        "  `author` = VALUES(`author`),",
        "  `cover` = VALUES(`cover`),",
        "  `publisher` = VALUES(`publisher`),",
        "  `description` = VALUES(`description`),",
        "  `category_id` = VALUES(`category_id`),",
        "  `condition_id` = VALUES(`condition_id`),",
        "  `seller_id` = VALUES(`seller_id`),",
        "  `price` = VALUES(`price`),",
        "  `original_price` = VALUES(`original_price`),",
        "  `stock` = VALUES(`stock`),",
        "  `status` = VALUES(`status`),",
        "  `updatetime` = NOW();",
        "",
    ]
    return "\n".join(header) + "\n" + ",\n".join(values) + "\n" + "\n".join(footer)


def main() -> None:
    rows = load_rows()
    sql = generate_sql(rows)
    OUTPUT_SQL.write_text(sql, encoding="utf-8")
    print(f"rows={len(rows)}")
    print(f"output={OUTPUT_SQL}")


if __name__ == "__main__":
    main()
