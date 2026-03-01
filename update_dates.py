"""
更新数据库中的书籍日期从2024到2026
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
    print("正在连接数据库...")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 更新日期
    print("正在更新书籍上架日期...")
    cursor.execute("""
        UPDATE ershoushuji
        SET shangjiariqi = REPLACE(shangjiariqi, '2024-', '2026-')
        WHERE shangjiariqi LIKE '2024-%'
    """)

    affected = cursor.rowcount
    conn.commit()

    print(f"成功更新 {affected} 本书籍的日期")

    # 验证结果
    cursor.execute("""
        SELECT COUNT(*) FROM ershoushuji WHERE shangjiariqi LIKE '2026-%'
    """)
    count_2026 = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM ershoushuji WHERE shangjiariqi LIKE '2024-%'
    """)
    count_2024 = cursor.fetchone()[0]

    print(f"\n验证结果:")
    print(f"  2026年的书籍: {count_2026}本")
    print(f"  2024年的书籍: {count_2024}本")

    cursor.close()
    conn.close()

    print("\n完成！")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
