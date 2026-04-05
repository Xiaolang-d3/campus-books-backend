"""
添加AI聊天历史表的迁移脚本
运行方式: python migrations/add_chat_history.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db
from main import create_app

def migrate():
    app = create_app()
    
    with app.app_context():
        # 执行SQL文件
        sql_file = os.path.join(os.path.dirname(__file__), 'add_chat_tables.sql')
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句并执行
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        for statement in statements:
            try:
                db.session.execute(db.text(statement))
                print(f"✓ 执行成功: {statement[:50]}...")
            except Exception as e:
                print(f"✗ 执行失败: {statement[:50]}...")
                print(f"  错误: {e}")
        
        db.session.commit()
        print("\n✓ 数据库迁移完成！")
        print("已添加表:")
        print("  - chat_session (聊天会话表)")
        print("  - chat_message (聊天消息表)")

if __name__ == '__main__':
    migrate()
