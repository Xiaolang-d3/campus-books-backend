"""
导入书籍测试数据
运行方法: python import_books.py
"""
import pymysql
import sys
import os

# 从 config.yaml 读取数据库配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config

# 解析数据库连接字符串
uri = Config.SQLALCHEMY_DATABASE_URI
# mysql+pymysql://root:root@127.0.0.1:3306/secondhand_books?charset=utf8mb4
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

def import_books():
    try:
        print("正在连接数据库...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 读取 SQL 文件
        sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'seed_books_data.sql')
        print(f"正在读取 SQL 文件: {sql_file}")

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 使用 pymysql 的多语句执行
        print(f"正在执行 SQL 语句...")

        # 分割并执行每个语句
        for statement in sql_content.split(';'):
            statement = statement.strip()
            # 跳过注释和空语句
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    # 忽略重复键错误
                    if 'Duplicate entry' not in str(e) and 'already exists' not in str(e):
                        print(f"  警告: {e}")

        conn.commit()

        # 统计结果
        cursor.execute("SELECT COUNT(*) FROM ershoushuji")
        book_count = cursor.fetchone()[0]

        cursor.execute("SELECT shujifenlei, COUNT(*) FROM ershoushuji GROUP BY shujifenlei")
        categories = cursor.fetchall()

        print(f"\n✓ 数据导入成功！")
        print(f"✓ 总共 {book_count} 本书籍")
        print(f"\n分类统计:")
        for cat, count in categories:
            print(f"  - {cat}: {count}本")

        cursor.close()
        conn.close()

    except FileNotFoundError:
        print(f"\n❌ 找不到 SQL 文件: {sql_file}")
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1045:
            print(f"\n❌ 数据库连接失败：密码错误")
        else:
            print(f"\n❌ 数据库错误：{e}")
    except Exception as e:
        print(f"\n❌ 导入失败：{e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 50)
    print("导入书籍测试数据")
    print("=" * 50)
    import_books()
    print("\n完成！请刷新前端页面查看。")
