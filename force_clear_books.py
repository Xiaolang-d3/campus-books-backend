"""强制清空书籍数据"""
import pymysql
import yaml

with open('config/config.yaml', 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

uri = cfg['database']['uri'].replace('mysql+pymysql://', '')
auth, rest = uri.split('@', 1)
user, password = auth.split(':', 1)
host_port, database = rest.split('/', 1)
host, port = host_port.split(':', 1)

conn = pymysql.connect(
    host=host,
    port=int(port),
    user=user,
    password=password,
    database=database.split('?')[0],
    charset='utf8mb4'
)

try:
    cur = conn.cursor()
    
    # 检查当前数据
    cur.execute('SELECT COUNT(*) FROM book')
    before_count = cur.fetchone()[0]
    print(f'清理前书籍数量: {before_count}')
    
    # 清理关联数据
    cur.execute('DELETE FROM cart')
    print(f'清理购物车: {cur.rowcount} 条')
    
    cur.execute('DELETE FROM favorite')
    print(f'清理收藏: {cur.rowcount} 条')
    
    cur.execute('DELETE FROM review')
    print(f'清理评价: {cur.rowcount} 条')
    
    cur.execute('DELETE FROM book_view')
    print(f'清理浏览记录: {cur.rowcount} 条')
    
    # 清空订单中的书籍关联
    cur.execute('UPDATE `order` SET book_id = NULL')
    print(f'清理订单关联: {cur.rowcount} 条')
    
    # 清空书籍表
    cur.execute('DELETE FROM book')
    deleted = cur.rowcount
    print(f'删除书籍: {deleted} 条')
    
    # 重置自增ID
    cur.execute('ALTER TABLE book AUTO_INCREMENT = 1')
    print('重置自增ID')
    
    conn.commit()
    
    # 验证结果
    cur.execute('SELECT COUNT(*) FROM book')
    after_count = cur.fetchone()[0]
    print(f'\n清理后书籍数量: {after_count}')
    
    if after_count == 0:
        print('✓ 清理成功！')
    else:
        print('✗ 清理失败，仍有数据残留')
    
except Exception as e:
    print(f'错误: {e}')
    conn.rollback()
finally:
    conn.close()
