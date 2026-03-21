"""
书籍批量导入脚本
用法: python import_books.py <csv文件路径>

CSV 格式（第一行为表头）:
isbn,title,author,cover,publisher,description,category,condition,price,original_price,stock,status

示例:
,Python编程从入门到实践,Eric Matthes,http://xxx.jpg,人民邮电出版社,Python入门经典,计算机,九成新,89.00,119.00,5,1

字段说明:
- isbn: 可选，留空则自动生成随机ISBN
- cover: 封面图URL，可选
- category: 分类名称（必须存在于 book_category 表），留空则不设分类
- condition: 新旧程度名称（必须存在于 condition_level 表），留空默认"九成新"
- price: 售价（必填）
- original_price: 原价，可选
- stock: 库存，默认1
- status: 状态(1=上架,0=下架)，默认1
"""
import csv
import os
import sys
import uuid
from datetime import datetime
from urllib.parse import urlparse

import pymysql
import yaml


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config', 'config.yaml')
sys.path.insert(0, SCRIPT_DIR)


def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_connection():
    cfg = load_config()
    db_uri = cfg['database']['uri']
    parsed = urlparse(db_uri.replace('mysql+pymysql://', 'mysql://'))
    return pymysql.connect(
        host=parsed.hostname or '127.0.0.1',
        port=parsed.port or 3306,
        user=parsed.username or 'root',
        password=parsed.password or '',
        database=parsed.path.lstrip('/').split('?')[0],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
    )


def load_category_map(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM book_category")
        return {r['name']: r['id'] for r in cur.fetchall()}


def load_condition_map(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM condition_level")
        return {r['name']: r['id'] for r in cur.fetchall()}


def get_default_seller(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM user LIMIT 1")
        row = cur.fetchone()
        if not row:
            print('系统中没有用户，正在创建示例卖家...')
            cur.execute("""
                INSERT INTO user (student_no, name, password, gender, phone, balance, addtime)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, ('2024001', '示例卖家', 'e10adc3949ba59abbe56e057f20f883e', '男', '13800000001', 0.00))
            conn.commit()
            cur.execute("SELECT id FROM user LIMIT 1")
            row = cur.fetchone()
        return row['id']


def generate_isbn():
    return f"978{str(uuid.uuid4().int)[:9]}"


def import_books(csv_path):
    conn = get_connection()
    try:
        cat_map = load_category_map(conn)
        cond_map = load_condition_map(conn)
        default_seller = get_default_seller(conn)

        print(f'分类映射: {cat_map}')
        print(f'新旧程度映射: {cond_map}')
        print(f'默认卖家ID: {default_seller}')
        print()

        imported = 0
        skipped = 0
        errors = []

        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=2):
                title = (row.get('title') or '').strip()
                price_str = (row.get('price') or '').strip()

                if not title:
                    errors.append(f'行{row_idx}: 书名为空，跳过')
                    skipped += 1
                    continue
                if not price_str:
                    errors.append(f'行{row_idx}: 价格为空的，跳过')
                    skipped += 1
                    continue

                try:
                    price = float(price_str)
                except ValueError:
                    errors.append(f'行{row_idx}: 价格"{price_str}"无效，跳过')
                    skipped += 1
                    continue

                isbn = (row.get('isbn') or '').strip() or generate_isbn()
                cat_name = (row.get('category') or '').strip()
                category_id = cat_map.get(cat_name)
                if cat_name and category_id is None:
                    print(f'警告: 行{row_idx} 分类"{cat_name}"不存在，跳过该分类')
                    category_id = None

                cond_name = (row.get('condition') or '').strip() or '九成新'
                condition_id = cond_map.get(cond_name)
                if cond_name and condition_id is None:
                    print(f'警告: 行{row_idx} 新旧程度"{cond_name}"不存在，使用默认值')
                    condition_id = None

                seller_str = (row.get('seller_id') or '').strip()
                seller_id = int(seller_str) if seller_str else default_seller

                original_price_str = (row.get('original_price') or '').strip()
                original_price = float(original_price_str) if original_price_str else None

                stock_str = (row.get('stock') or '').strip()
                stock = int(stock_str) if stock_str else 1

                status_str = (row.get('status') or '').strip()
                status = int(status_str) if status_str else 1

                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO book (
                            isbn, title, author, cover, publisher, description,
                            category_id, condition_id, seller_id, price,
                            original_price, stock, status, addtime
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        isbn,
                        title,
                        (row.get('author') or '').strip() or None,
                        (row.get('cover') or '').strip() or None,
                        (row.get('publisher') or '').strip() or None,
                        (row.get('description') or '').strip() or None,
                        category_id,
                        condition_id,
                        seller_id,
                        price,
                        original_price,
                        stock,
                        status,
                        now,
                    ))
                imported += 1

                if imported % 50 == 0:
                    conn.commit()
                    print(f'已导入 {imported} 条...')

        conn.commit()
        print()
        print('=' * 50)
        print(f'导入完成: 成功 {imported} 条，跳过 {skipped} 条')

        if errors:
            print(f'错误列表 ({len(errors)} 条):')
            for err in errors[:20]:
                print(f'  - {err}')
            if len(errors) > 20:
                print(f'  ... 还有 {len(errors) - 20} 条错误')
    finally:
        conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    csv_file = sys.argv[1]
    print(f'开始导入书籍数据: {csv_file}')
    print()

    if not os.path.exists(csv_file):
        print(f'错误: 找不到文件 "{csv_file}"')
        sys.exit(1)

    import_books(csv_file)
