"""
导入清理后的书籍数据到数据库
将书籍关联到指定用户作为卖家
"""
import json
import sys
from datetime import datetime
import pymysql
from config.config import Config


def get_db_connection():
    """获取数据库连接"""
    config = Config()
    db_uri = config.SQLALCHEMY_DATABASE_URI
    
    # 解析数据库URI: mysql+pymysql://user:password@host:port/database?charset=utf8mb4
    import re
    match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)', db_uri)
    if not match:
        raise ValueError(f"无法解析数据库URI: {db_uri}")
    
    user, password, host, port, database = match.groups()
    
    conn = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    return conn


def import_books_to_user(json_file: str, user_id: int = None):
    """
    导入书籍数据到指定用户
    
    Args:
        json_file: JSON文件路径
        user_id: 用户ID（如果不指定，会列出所有用户供选择）
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 如果没有指定用户ID，列出所有用户
        if not user_id:
            cursor.execute("SELECT id, student_no, name FROM user")
            users = cursor.fetchall()
            
            if not users:
                print("错误: 数据库中没有用户，请先创建用户")
                return
            
            print("\n=== 可用用户列表 ===")
            for user in users:
                print(f"ID: {user['id']} | 学号: {user['student_no']} | 姓名: {user['name']}")
            
            user_id_input = input("\n请输入用户ID: ").strip()
            if not user_id_input.isdigit():
                print("错误: 无效的用户ID")
                return
            user_id = int(user_id_input)
        
        # 验证用户是否存在
        cursor.execute("SELECT id, student_no, name FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"错误: 用户ID {user_id} 不存在")
            return
        
        print(f"\n将书籍导入到用户: {user['name']} (学号: {user['student_no']})")
        
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            books_data = json.load(f)
        
        print(f"读取到 {len(books_data)} 本书籍数据")
        
        # 获取或创建分类和新旧程度
        categories = {}
        conditions = {}
        
        # 预加载所有分类
        cursor.execute("SELECT id, name FROM book_category")
        for row in cursor.fetchall():
            categories[row['name']] = row['id']
        
        # 预加载所有新旧程度
        cursor.execute("SELECT id, name FROM condition_level")
        for row in cursor.fetchall():
            conditions[row['name']] = row['id']
        
        # 如果没有默认分类和新旧程度，创建它们
        if '计算机' not in categories:
            cursor.execute(
                "INSERT INTO book_category (name, icon, sort, addtime) VALUES (%s, %s, %s, %s)",
                ('计算机', 'computer', 1, datetime.now())
            )
            categories['计算机'] = cursor.lastrowid
        
        if '数学' not in categories:
            cursor.execute(
                "INSERT INTO book_category (name, icon, sort, addtime) VALUES (%s, %s, %s, %s)",
                ('数学', 'math', 2, datetime.now())
            )
            categories['数学'] = cursor.lastrowid
        
        if '九成新' not in conditions:
            cursor.execute(
                "INSERT INTO condition_level (name) VALUES (%s)",
                ('九成新',)
            )
            conditions['九成新'] = cursor.lastrowid
        
        conn.commit()
        
        # 导入书籍
        success_count = 0
        skip_count = 0
        error_count = 0
        
        print("\n开始导入书籍...")
        
        for book_data in books_data:
            try:
                isbn = book_data.get('isbn', '')
                
                # 检查是否已存在
                cursor.execute("SELECT id FROM book WHERE isbn = %s", (isbn,))
                if cursor.fetchone():
                    print(f"  跳过: {book_data['title']} (ISBN已存在)")
                    skip_count += 1
                    continue
                
                # 获取分类
                category_name = book_data.get('category', '计算机')
                if category_name not in categories:
                    category_name = '计算机'
                category_id = categories[category_name]
                
                # 获取新旧程度
                condition_name = book_data.get('condition', '九成新')
                if condition_name not in conditions:
                    condition_name = '九成新'
                condition_id = conditions[condition_name]
                
                # 插入书籍记录
                cursor.execute("""
                    INSERT INTO book (
                        isbn, title, author, publisher, description, cover,
                        category_id, condition_id, seller_id,
                        price, original_price, stock, status, addtime
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    isbn,
                    book_data['title'][:100],
                    book_data['author'][:50],
                    book_data['publisher'][:50],
                    book_data.get('description', '')[:500],
                    book_data.get('cover_url', ''),
                    category_id,
                    condition_id,
                    user_id,
                    float(book_data.get('price', 0)),
                    float(book_data.get('original_price', 0)),
                    int(book_data.get('stock', 1)),
                    1,  # status: 1=上架
                    datetime.now()
                ))
                
                conn.commit()
                
                print(f"  ✓ {book_data['title']} - ¥{book_data.get('price', 0)}")
                success_count += 1
                
            except Exception as e:
                print(f"  ✗ 错误: {book_data.get('title', 'Unknown')} - {str(e)}")
                error_count += 1
                conn.rollback()
        
        print(f"\n{'='*50}")
        print(f"导入完成!")
        print(f"成功: {success_count} 本")
        print(f"跳过: {skip_count} 本")
        print(f"失败: {error_count} 本")
        print(f"{'='*50}")
        
        # 显示用户的书籍统计
        cursor.execute("""
            SELECT COUNT(*) as count, SUM(price * stock) as total_value
            FROM book WHERE seller_id = %s
        """, (user_id,))
        stats = cursor.fetchone()
        
        print(f"\n用户 {user['name']} 现在有 {stats['count']} 本书籍")
        print(f"总价值: ¥{stats['total_value']:.2f}")
        
    except FileNotFoundError:
        print(f"错误: 文件 {json_file} 不存在")
    except json.JSONDecodeError:
        print(f"错误: 文件 {json_file} 不是有效的JSON格式")
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


def main():
    """主函数"""
    print("=== 书籍数据导入工具 ===\n")
    
    # 默认使用清理后的数据文件
    json_file = 'data/books_data_cleaned.json'
    
    # 检查文件是否存在
    import os
    if not os.path.exists(json_file):
        print(f"错误: 文件 {json_file} 不存在")
        print("请先运行 get_books_by_isbn.py 获取书籍数据")
        return
    
    # 导入书籍
    import_books_to_user(json_file)


if __name__ == '__main__':
    main()
