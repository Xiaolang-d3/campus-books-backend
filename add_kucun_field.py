"""
添加库存字段到数据库
运行方法: python add_kucun_field.py
"""
import pymysql

# 数据库配置（从 config.yaml 读取）
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',  # 请修改为你的MySQL密码
    'database': 'secondhand_books',
    'charset': 'utf8mb4'
}

def add_kucun_column():
    try:
        # 连接数据库
        print("正在连接数据库...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 检查字段是否已存在
        cursor.execute("SHOW COLUMNS FROM ershoushuji LIKE 'kucun'")
        if cursor.fetchone():
            print("✓ 库存字段已存在，无需添加")
            return

        # 添加库存字段
        print("正在添加库存字段...")
        cursor.execute("""
            ALTER TABLE ershoushuji
            ADD COLUMN kucun INT DEFAULT 1 COMMENT '库存数量' AFTER price
        """)

        # 为现有数据设置默认库存
        print("正在设置默认库存...")
        cursor.execute("UPDATE ershoushuji SET kucun = 1 WHERE kucun IS NULL")

        # 提交事务
        conn.commit()

        # 验证结果
        cursor.execute("SELECT COUNT(*) FROM ershoushuji")
        count = cursor.fetchone()[0]

        print(f"\n✓ 库存字段添加成功！")
        print(f"✓ 已为 {count} 本书籍设置默认库存")

        # 显示表结构
        print("\n当前表结构：")
        cursor.execute("DESCRIBE ershoushuji")
        for row in cursor.fetchall():
            if row[0] in ['price', 'kucun']:
                print(f"  {row[0]}: {row[1]}")

    except pymysql.err.OperationalError as e:
        if e.args[0] == 1045:
            print(f"\n❌ 数据库连接失败：密码错误")
            print(f"请修改脚本中的 DB_CONFIG['password'] 为你的MySQL密码")
        else:
            print(f"\n❌ 数据库错误：{e}")
    except Exception as e:
        print(f"\n❌ 执行失败：{e}")
        conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("添加库存字段到 ershoushuji 表")
    print("=" * 50)
    add_kucun_column()
    print("\n完成！请重启后端服务。")
