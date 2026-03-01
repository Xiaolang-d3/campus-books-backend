"""
导入书籍测试数据 - 调试版本
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

def import_books():
    try:
        print("正在连接数据库...")
        print(f"配置: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 读取 SQL 文件
        sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'seed_books_data.sql')
        print(f"正在读取 SQL 文件: {sql_file}")

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(f"SQL 文件大小: {len(sql_content)} 字符")

        # 分割语句
        statements = []
        current = []
        in_insert = False

        for line in sql_content.split('\n'):
            line = line.strip()

            # 跳过注释
            if line.startswith('--') or not line:
                continue

            # 检测 INSERT 语句开始
            if line.upper().startswith('INSERT'):
                in_insert = True
                current = [line]
            elif in_insert:
                current.append(line)
                # 检测语句结束
                if line.endswith(';'):
                    statements.append('\n'.join(current))
                    current = []
                    in_insert = False
            elif line.endswith(';'):
                statements.append(line)

        print(f"找到 {len(statements)} 条 SQL 语句")

        # 执行语句
        success_count = 0
        error_count = 0

        for i, statement in enumerate(statements, 1):
            try:
                print(f"\n执行语句 {i}/{len(statements)}:")
                # 只显示前100个字符
                preview = statement[:100].replace('\n', ' ')
                print(f"  {preview}...")

                cursor.execute(statement)
                affected = cursor.rowcount
                print(f"  ✓ 成功，影响 {affected} 行")
                success_count += 1

            except Exception as e:
                error_msg = str(e)
                if 'Duplicate entry' in error_msg:
                    print(f"  ⚠ 跳过（数据已存在）")
                else:
                    print(f"  ✗ 错误: {e}")
                    error_count += 1

        conn.commit()
        print(f"\n执行完成: 成功 {success_count} 条, 错误 {error_count} 条")

        # 统计结果
        cursor.execute("SELECT COUNT(*) FROM ershoushuji")
        book_count = cursor.fetchone()[0]

        cursor.execute("SELECT shujifenlei, COUNT(*) FROM ershoushuji GROUP BY shujifenlei")
        categories = cursor.fetchall()

        print(f"\n✓ 数据导入完成！")
        print(f"✓ 数据库中共有 {book_count} 本书籍")

        if categories:
            print(f"\n分类统计:")
            for cat, count in categories:
                print(f"  - {cat}: {count}本")
        else:
            print("\n⚠ 警告：数据库中没有书籍数据！")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n❌ 导入失败：{e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 60)
    print("导入书籍测试数据 - 调试版本")
    print("=" * 60)
    import_books()
