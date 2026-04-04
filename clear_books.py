"""
清理数据库中的书籍数据

使用方法：
1. 清空所有书籍数据：python clear_books.py --all
2. 清理无效书籍数据：python clear_books.py --invalid
3. 清理测试书籍数据：python clear_books.py --test
4. 清理指定卖家的书籍：python clear_books.py --seller <seller_id>
"""

import sys
import argparse
from pathlib import Path

import pymysql
import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config" / "config.yaml"


def load_db_config() -> dict:
    """加载数据库配置"""
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        cfg = yaml.safe_load(file)
    uri = cfg["database"]["uri"].replace("mysql+pymysql://", "")
    auth, rest = uri.split("@", 1)
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
        "cursorclass": pymysql.cursors.DictCursor,
    }


def clear_all_books(conn) -> int:
    """清空所有书籍数据"""
    with conn.cursor() as cur:
        # 先清理关联数据
        cur.execute("DELETE FROM cart")
        cur.execute("DELETE FROM favorite")
        cur.execute("DELETE FROM review")
        cur.execute("DELETE FROM book_view")
        
        # 清理订单中的书籍关联（保留订单记录，只清除book_id）
        cur.execute("UPDATE `order` SET book_id = NULL")
        
        # 清空书籍表
        cur.execute("DELETE FROM book")
        deleted = cur.rowcount
        
        # 重置自增ID
        cur.execute("ALTER TABLE book AUTO_INCREMENT = 1")
        
    conn.commit()
    return deleted


def clear_invalid_books(conn) -> int:
    """清理无效书籍数据（缺少必要字段的书籍）"""
    with conn.cursor() as cur:
        # 查找无效书籍
        cur.execute("""
            SELECT id FROM book 
            WHERE title IS NULL 
               OR title = '' 
               OR category_id IS NULL 
               OR condition_id IS NULL
               OR seller_id IS NULL
               OR price IS NULL
               OR price <= 0
        """)
        invalid_ids = [row['id'] for row in cur.fetchall()]
        
        if not invalid_ids:
            return 0
        
        # 清理关联数据
        placeholders = ','.join(['%s'] * len(invalid_ids))
        cur.execute(f"DELETE FROM cart WHERE book_id IN ({placeholders})", invalid_ids)
        cur.execute(f"DELETE FROM favorite WHERE book_id IN ({placeholders})", invalid_ids)
        cur.execute(f"DELETE FROM review WHERE book_id IN ({placeholders})", invalid_ids)
        cur.execute(f"DELETE FROM book_view WHERE book_id IN ({placeholders})", invalid_ids)
        
        # 删除无效书籍
        cur.execute(f"DELETE FROM book WHERE id IN ({placeholders})", invalid_ids)
        deleted = cur.rowcount
        
    conn.commit()
    return deleted


def clear_test_books(conn) -> int:
    """清理测试书籍数据（标题包含"测试"的书籍）"""
    with conn.cursor() as cur:
        # 查找测试书籍
        cur.execute("""
            SELECT id FROM book 
            WHERE title LIKE '%测试%' 
               OR title LIKE '%test%'
               OR title LIKE '%Test%'
               OR description LIKE '%测试%'
        """)
        test_ids = [row['id'] for row in cur.fetchall()]
        
        if not test_ids:
            return 0
        
        # 清理关联数据
        placeholders = ','.join(['%s'] * len(test_ids))
        cur.execute(f"DELETE FROM cart WHERE book_id IN ({placeholders})", test_ids)
        cur.execute(f"DELETE FROM favorite WHERE book_id IN ({placeholders})", test_ids)
        cur.execute(f"DELETE FROM review WHERE book_id IN ({placeholders})", test_ids)
        cur.execute(f"DELETE FROM book_view WHERE book_id IN ({placeholders})", test_ids)
        
        # 删除测试书籍
        cur.execute(f"DELETE FROM book WHERE id IN ({placeholders})", test_ids)
        deleted = cur.rowcount
        
    conn.commit()
    return deleted


def clear_seller_books(conn, seller_id: int) -> int:
    """清理指定卖家的书籍"""
    with conn.cursor() as cur:
        # 查找该卖家的书籍
        cur.execute("SELECT id FROM book WHERE seller_id = %s", (seller_id,))
        book_ids = [row['id'] for row in cur.fetchall()]
        
        if not book_ids:
            return 0
        
        # 清理关联数据
        placeholders = ','.join(['%s'] * len(book_ids))
        cur.execute(f"DELETE FROM cart WHERE book_id IN ({placeholders})", book_ids)
        cur.execute(f"DELETE FROM favorite WHERE book_id IN ({placeholders})", book_ids)
        cur.execute(f"DELETE FROM review WHERE book_id IN ({placeholders})", book_ids)
        cur.execute(f"DELETE FROM book_view WHERE book_id IN ({placeholders})", book_ids)
        
        # 删除书籍
        cur.execute(f"DELETE FROM book WHERE id IN ({placeholders})", book_ids)
        deleted = cur.rowcount
        
    conn.commit()
    return deleted


def show_book_stats(conn):
    """显示书籍统计信息"""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) as total FROM book")
        total = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as count FROM book WHERE status = 1")
        on_sale = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM book WHERE stock > 0")
        in_stock = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM book WHERE category_id IS NULL OR condition_id IS NULL")
        invalid = cur.fetchone()['count']
        
        print("\n=== 书籍数据统计 ===")
        print(f"总书籍数：{total}")
        print(f"上架中：{on_sale}")
        print(f"有库存：{in_stock}")
        print(f"无效数据：{invalid}")
        print("=" * 30)


def main():
    parser = argparse.ArgumentParser(description='清理数据库中的书籍数据')
    parser.add_argument('--all', action='store_true', help='清空所有书籍数据')
    parser.add_argument('--invalid', action='store_true', help='清理无效书籍数据')
    parser.add_argument('--test', action='store_true', help='清理测试书籍数据')
    parser.add_argument('--seller', type=int, help='清理指定卖家的书籍')
    parser.add_argument('--stats', action='store_true', help='仅显示统计信息')
    parser.add_argument('--yes', '-y', action='store_true', help='跳过确认提示')
    
    args = parser.parse_args()
    
    # 如果没有指定任何操作，显示帮助
    if not (args.all or args.invalid or args.test or args.seller or args.stats):
        parser.print_help()
        return
    
    # 连接数据库
    conn = pymysql.connect(**load_db_config())
    
    try:
        # 显示统计信息
        show_book_stats(conn)
        
        if args.stats:
            return
        
        # 确认操作
        if not args.yes:
            print("\n警告：此操作将删除数据且不可恢复！")
            confirm = input("确认继续？(yes/no): ")
            if confirm.lower() != 'yes':
                print("操作已取消")
                return
        
        deleted = 0
        
        if args.all:
            print("\n正在清空所有书籍数据...")
            deleted = clear_all_books(conn)
            print(f"✓ 已删除 {deleted} 条书籍记录")
        
        elif args.invalid:
            print("\n正在清理无效书籍数据...")
            deleted = clear_invalid_books(conn)
            print(f"✓ 已删除 {deleted} 条无效书籍记录")
        
        elif args.test:
            print("\n正在清理测试书籍数据...")
            deleted = clear_test_books(conn)
            print(f"✓ 已删除 {deleted} 条测试书籍记录")
        
        elif args.seller:
            print(f"\n正在清理卖家 {args.seller} 的书籍数据...")
            deleted = clear_seller_books(conn, args.seller)
            print(f"✓ 已删除 {deleted} 条书籍记录")
        
        # 显示清理后的统计
        print("\n清理完成！")
        show_book_stats(conn)
        
    except Exception as e:
        print(f"\n错误：{e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
