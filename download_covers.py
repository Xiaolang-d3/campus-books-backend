"""
一次性脚本：将数据库中所有外部链接封面图片下载到本地 static/upload/covers/
并更新数据库 book.cover 字段为本地路径
"""
import os
import re
import sys
import time
import hashlib

import pymysql
import requests
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'config.yaml')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'upload')
COVER_DIR = os.path.join(UPLOAD_DIR, 'covers')

with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

db_uri = cfg['database']['uri']
match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)', db_uri)
DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME = match.groups()


def get_conn():
    return pymysql.connect(
        host=DB_HOST, port=int(DB_PORT),
        user=DB_USER, password=DB_PASS,
        database=DB_NAME, charset='utf8mb4',
    )


def download_image(url, save_path, timeout=15):
    """下载图片到指定路径，成功返回 True"""
    try:
        resp = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; CampusBooks/1.0)',
            'Accept': 'image/*',
        }, stream=True)
        if resp.status_code != 200:
            return False
        content_type = resp.headers.get('Content-Type', '')
        if 'image' not in content_type and 'octet-stream' not in content_type:
            return False
        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        # 检查文件大小，太小可能是错误页面
        if os.path.getsize(save_path) < 500:
            os.remove(save_path)
            return False
        return True
    except Exception as e:
        print(f'    下载失败: {e}')
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except OSError:
                pass
        return False


def main():
    os.makedirs(COVER_DIR, exist_ok=True)

    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 查找所有外部链接封面
    cursor.execute("SELECT id, title, cover FROM book WHERE cover LIKE 'http%%'")
    books = cursor.fetchall()

    if not books:
        print('没有需要下载的外部封面图片')
        return

    print(f'找到 {len(books)} 本书的封面需要下载\n')

    success = 0
    failed = 0

    for i, book in enumerate(books, 1):
        url = book['cover'].strip()
        if not url:
            continue

        # 用 book id 作为文件名前缀，保证唯一
        ext = '.jpg'
        path_part = url.split('?')[0]
        if '.' in path_part.split('/')[-1]:
            raw_ext = '.' + path_part.split('/')[-1].rsplit('.', 1)[-1].lower()
            if raw_ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
                ext = raw_ext

        filename = f"cover_{book['id']}{ext}"
        save_path = os.path.join(COVER_DIR, filename)
        # 数据库存储的相对路径（相对于 upload 目录）
        db_path = f"upload/covers/{filename}"

        print(f'[{i}/{len(books)}] {book["title"][:30]}...')

        # 如果本地已存在且大小合理，跳过下载
        if os.path.exists(save_path) and os.path.getsize(save_path) > 500:
            print(f'    已存在，跳过下载')
            cursor.execute("UPDATE book SET cover = %s WHERE id = %s", (db_path, book['id']))
            conn.commit()
            success += 1
            continue

        ok = download_image(url, save_path)
        if ok:
            cursor.execute("UPDATE book SET cover = %s WHERE id = %s", (db_path, book['id']))
            conn.commit()
            size_kb = os.path.getsize(save_path) / 1024
            print(f'    ✓ 已下载 ({size_kb:.0f} KB)')
            success += 1
        else:
            print(f'    ✗ 下载失败，保留原始链接')
            failed += 1

        # 避免请求过快
        time.sleep(0.3)

    cursor.close()
    conn.close()

    print(f'\n{"=" * 40}')
    print(f'完成! 成功: {success}, 失败: {failed}')
    print(f'封面存储在: {COVER_DIR}')
    print(f'{"=" * 40}')


if __name__ == '__main__':
    main()
