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

cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM book')
count = cur.fetchone()[0]
print(f'书籍总数: {count}')

if count > 0:
    cur.execute('SELECT id, title, author FROM book LIMIT 10')
    books = cur.fetchall()
    print('\n前10条记录:')
    for b in books:
        print(f'ID: {b[0]}, 标题: {b[1]}, 作者: {b[2]}')

conn.close()
