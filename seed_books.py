"""Verify final database state for image display."""
import pymysql

conn = pymysql.connect(
    host='127.0.0.1', port=3306, user='root', password='root',
    database='secondhand_books', charset='utf8mb4'
)
cur = conn.cursor()

print('=== Books with covers (first 5) ===')
cur.execute('SELECT id, title, cover FROM book LIMIT 5')
for row in cur.fetchall():
    print(f'  id={row[0]}, title={row[1]}, cover={row[2]}')

print('\n=== Books with covers (total) ===')
cur.execute('SELECT COUNT(*) FROM book WHERE cover IS NOT NULL AND cover != ""')
print(f'  {cur.fetchone()[0]} books have covers')

print('\n=== News ===')
cur.execute('SELECT id, title, picture FROM news')
for row in cur.fetchall():
    print(f'  id={row[0]}, title={row[1]}, picture={row[2]}')

print('\n=== Config ===')
cur.execute('SELECT id, name, value FROM config')
for row in cur.fetchall():
    print(f'  id={row[0]}, name={row[1]}, value={row[2]}')

print('\n=== Users ===')
cur.execute('SELECT id, student_no, name, avatar FROM user')
for row in cur.fetchall():
    print(f'  id={row[0]}, student_no={row[1]}, name={row[2]}, avatar={row[3]}')

conn.close()
