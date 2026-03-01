"""
检查数据库中的书籍数据
"""
import pymysql
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config

# 解析数据库连接字符串
uri = Config.SQLALCHEMY_DATABASE_URI
parts = uri.replace('mysql+pymysql://', '').split('@')
user_pass = parts[0].split(':')
host_db = parts[1].split('/')
host_port = host_db[0].split(':')

DB_CONFIG = {
    'host': host_port[0],
    'port': int(host_port[1]) if len(host_port) > 1 else 3306,
    'user': user_pass[0],
    'password': user_pass[1] if len(user_pass) > 1 else '',
    'database': host_db[1].split('?')[0],
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 查询书籍总数
    cursor.execute("SELECT COUNT(*) FROM ershoushuji")
    total = cursor.fetchone()[0]
    print(f"数据库中共有 {total} 本书籍\n")

    # 查询最近的书籍
    cursor.execute("""
        SELECT id, shujibianhao, shujimingcheng, shujifengmian, shujifenlei,
               shangjiariqi, price, kucun
        FROM ershoushuji
        ORDER BY id DESC
        LIMIT 10
    """)

    books = cursor.fetchall()

    if books:
        print("最近的10本书籍:")
        print("-" * 100)
        for book in books:
            print(f"ID: {book[0]}")
            print(f"  编号: {book[1]}")
            print(f"  名称: {book[2]}")
            print(f"  封面: {book[3]}")
            print(f"  分类: {book[4]}")
            print(f"  上架日期: {book[5]}")
            print(f"  价格: {book[6]}")
            print(f"  库存: {book[7]}")
            print()

    # 按分类统计
    cursor.execute("""
        SELECT shujifenlei, COUNT(*) as count, SUM(kucun) as total_stock
        FROM ershoushuji
        GROUP BY shujifenlei
    """)

    categories = cursor.fetchall()
    if categories:
        print("\n分类统计:")
        print("-" * 50)
        for cat in categories:
            print(f"  {cat[0]}: {cat[1]}本, 总库存{cat[2]}件")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
