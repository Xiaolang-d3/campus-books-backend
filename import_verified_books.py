"""
Batch import curated book data with optional cover caching.

Usage:
    python import_verified_books.py
    python import_verified_books.py --csv data/verified_books_seed.csv --cache-covers

CSV columns:
    isbn,title,author,publisher,publish_date,source_url,cover_url,fallback_cover_url,
    description,category,condition,price,original_price,stock,status,seller_id

Notes:
    - Rows are upserted by ISBN.
    - By default the script stores the remote cover URL from `cover_url` or
      `fallback_cover_url`.
    - Use `--cache-covers` to download the cover into `static/upload/imported-books/`
      and store the local `/upload/...` path instead.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import pymysql
import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = SCRIPT_DIR / "data" / "verified_books_seed.csv"
CONFIG_FILE = SCRIPT_DIR / "config" / "config.yaml"
UPLOAD_SUBDIR = Path("imported-books")
UPLOAD_DIR = SCRIPT_DIR / "static" / "upload" / UPLOAD_SUBDIR


@dataclass
class ImportStats:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    cover_cached: int = 0


def load_config() -> dict:
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_connection():
    cfg = load_config()
    db_uri = cfg["database"]["uri"]
    parsed = urlparse(db_uri.replace("mysql+pymysql://", "mysql://"))
    return pymysql.connect(
        host=parsed.hostname or "127.0.0.1",
        port=parsed.port or 3306,
        user=parsed.username or "root",
        password=parsed.password or "",
        database=parsed.path.lstrip("/").split("?")[0],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def fetch_mapping(conn, table_name: str) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(f"SELECT id, name FROM {table_name}")
        return {row["name"]: row["id"] for row in cur.fetchall()}


def ensure_default_seller(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM user ORDER BY id LIMIT 1")
        row = cur.fetchone()
        if row:
            return row["id"]

        student_no = f"AUTO{str(uuid.uuid4().int)[:8]}"
        cur.execute(
            """
            INSERT INTO user (student_no, name, password, gender, phone, balance, addtime)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                student_no,
                "图书导入卖家",
                "e10adc3949ba59abbe56e057f20f883e",
                "未知",
                "13800000000",
                Decimal("0.00"),
            ),
        )
        conn.commit()
        return cur.lastrowid


def parse_decimal(value: str, field_name: str, row_number: int) -> Optional[Decimal]:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"第 {row_number} 行字段 {field_name} 不是有效数字: {raw}") from exc


def parse_int(value: str, default: int) -> int:
    raw = (value or "").strip()
    return int(raw) if raw else default


def detect_extension(url: str, content_type: str | None) -> str:
    if content_type:
        lowered = content_type.lower()
        if "jpeg" in lowered or "jpg" in lowered:
            return ".jpg"
        if "png" in lowered:
            return ".png"
        if "webp" in lowered:
            return ".webp"
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"


def download_cover(url: str, isbn: str) -> Optional[str]:
    if not url:
        return None

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urlopen(request, timeout=20) as response:
            content = response.read()
            content_type = response.headers.get("Content-Type")
    except (HTTPError, URLError, TimeoutError, OSError):
        return None

    extension = detect_extension(url, content_type)
    filename = f"{isbn}{extension}"
    file_path = UPLOAD_DIR / filename
    with file_path.open("wb") as file:
        file.write(content)

    return f"upload/{UPLOAD_SUBDIR.as_posix()}/{filename}"


def choose_cover(row: dict, cache_covers: bool, stats: ImportStats) -> Optional[str]:
    primary = (row.get("cover_url") or "").strip()
    fallback = (row.get("fallback_cover_url") or "").strip()
    isbn = (row.get("isbn") or "").strip()

    if cache_covers:
        for candidate in (primary, fallback):
            local_path = download_cover(candidate, isbn)
            if local_path:
                stats.cover_cached += 1
                return local_path

    return primary or fallback or None


def upsert_book(conn, row: dict, category_map: dict[str, int], condition_map: dict[str, int],
                default_seller_id: int, cache_covers: bool, row_number: int, stats: ImportStats) -> None:
    isbn = (row.get("isbn") or "").strip()
    title = (row.get("title") or "").strip()
    if not isbn or not title:
        raise ValueError(f"第 {row_number} 行缺少 isbn 或 title")

    category_name = (row.get("category") or "").strip()
    condition_name = (row.get("condition") or "").strip()
    category_id = category_map.get(category_name)
    condition_id = condition_map.get(condition_name)

    if category_name and category_id is None:
        raise ValueError(f"第 {row_number} 行分类不存在: {category_name}")
    if condition_name and condition_id is None:
        raise ValueError(f"第 {row_number} 行品相不存在: {condition_name}")

    price = parse_decimal(row.get("price", ""), "price", row_number)
    if price is None:
        raise ValueError(f"第 {row_number} 行缺少 price")

    original_price = parse_decimal(row.get("original_price", ""), "original_price", row_number)
    stock = parse_int(row.get("stock", ""), 1)
    status = parse_int(row.get("status", ""), 1)
    seller_id = parse_int(row.get("seller_id", ""), default_seller_id)
    cover = choose_cover(row, cache_covers, stats)

    data = {
        "isbn": isbn,
        "title": title,
        "author": (row.get("author") or "").strip() or None,
        "cover": cover,
        "publisher": (row.get("publisher") or "").strip() or None,
        "description": (row.get("description") or "").strip() or None,
        "category_id": category_id,
        "condition_id": condition_id,
        "seller_id": seller_id,
        "price": price,
        "original_price": original_price,
        "stock": stock,
        "status": status,
    }

    with conn.cursor() as cur:
        cur.execute("SELECT id FROM book WHERE isbn=%s", (isbn,))
        existing = cur.fetchone()
        if existing:
            cur.execute(
                """
                UPDATE book
                SET title=%s, author=%s, cover=%s, publisher=%s, description=%s,
                    category_id=%s, condition_id=%s, seller_id=%s, price=%s,
                    original_price=%s, stock=%s, status=%s, updatetime=NOW()
                WHERE id=%s
                """,
                (
                    data["title"],
                    data["author"],
                    data["cover"],
                    data["publisher"],
                    data["description"],
                    data["category_id"],
                    data["condition_id"],
                    data["seller_id"],
                    data["price"],
                    data["original_price"],
                    data["stock"],
                    data["status"],
                    existing["id"],
                ),
            )
            stats.updated += 1
        else:
            cur.execute(
                """
                INSERT INTO book (
                    isbn, title, author, cover, publisher, description,
                    category_id, condition_id, seller_id, price,
                    original_price, stock, status, addtime, updatetime
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """,
                (
                    data["isbn"],
                    data["title"],
                    data["author"],
                    data["cover"],
                    data["publisher"],
                    data["description"],
                    data["category_id"],
                    data["condition_id"],
                    data["seller_id"],
                    data["price"],
                    data["original_price"],
                    data["stock"],
                    data["status"],
                ),
            )
            stats.inserted += 1


def import_books(csv_path: Path, cache_covers: bool) -> ImportStats:
    if not csv_path.exists():
        raise FileNotFoundError(f"找不到数据文件: {csv_path}")

    conn = get_connection()
    stats = ImportStats()
    try:
        category_map = fetch_mapping(conn, "book_category")
        condition_map = fetch_mapping(conn, "condition_level")
        default_seller_id = ensure_default_seller(conn)

        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row_number, row in enumerate(reader, start=2):
                try:
                    upsert_book(
                        conn=conn,
                        row=row,
                        category_map=category_map,
                        condition_map=condition_map,
                        default_seller_id=default_seller_id,
                        cache_covers=cache_covers,
                        row_number=row_number,
                        stats=stats,
                    )
                except ValueError as exc:
                    stats.skipped += 1
                    print(f"[SKIP] {exc}")

        conn.commit()
        return stats
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import curated verified books into the platform database.")
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="CSV file path")
    parser.add_argument(
        "--cache-covers",
        action="store_true",
        help="Download remote cover images to static/upload/imported-books and store local paths",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    stats = import_books(Path(args.csv), cache_covers=args.cache_covers)
    print("=" * 60)
    print(f"导入完成: 新增 {stats.inserted} 本，更新 {stats.updated} 本，跳过 {stats.skipped} 本")
    print(f"封面缓存: {stats.cover_cached} 张")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
