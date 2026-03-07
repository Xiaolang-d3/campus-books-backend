"""
Seed example data for local development.

Usage:
    python -m migrations.seed_data
"""

import os
import sys
from urllib.parse import urlparse

import pymysql
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'config',
    'config.yaml',
)
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    CONFIG = yaml.safe_load(f)

db_uri = CONFIG['database']['uri']
parsed = urlparse(db_uri.replace('mysql+pymysql://', 'mysql://'))
DB_HOST = parsed.hostname or '127.0.0.1'
DB_PORT = parsed.port or 3306
DB_USER = parsed.username or 'root'
DB_PASS = parsed.password or ''
DB_NAME = parsed.path.lstrip('/').split('?')[0]


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset='utf8mb4',
    )


def seed():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM yonghu")
            if cur.fetchone()[0] == 0:
                users = [
                    ('20220011', '王同学', '123456', '男', '13800138111', '计算机学院', '计算机科学与技术', '2022级', 300),
                    ('20220012', '陈同学', '123456', '女', '13800138112', '经济管理学院', '金融学', '2021级', 600),
                    ('20220013', '赵同学', '123456', '男', '13800138113', '外国语学院', '英语', '2023级', 120),
                ]
                for user in users:
                    cur.execute(
                        """
                        INSERT INTO yonghu
                        (yonghuzhanghao, yonghuxingming, mima, xingbie, dianhuahaoma, xueyuan, zhuanye, nianji, money)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        user,
                    )
                print(f"[OK] 导入 {len(users)} 条校园用户数据")
            else:
                print('[SKIP] 校园用户数据已存在')

            cur.execute("SELECT COUNT(*) FROM ershoushuji")
            if cur.fetchone()[0] == 0:
                books = [
                    (
                        'CS101-01',
                        'Python程序设计',
                        'upload/python.jpg',
                        '董付国',
                        '9787302602594',
                        'CS101',
                        '第3版',
                        '计算机科学与技术,软件工程',
                        'Python程序设计',
                        '计算机',
                        '计算机学院',
                        '计算机科学与技术',
                        'Python程序设计',
                        '第3版',
                        'Python 入门教材，适合程序设计基础课程。',
                        '九成新',
                        '清华大学出版社',
                        '2026-03-01',
                        20220011,
                        '20220011',
                        '王同学',
                        38,
                        2,
                    ),
                    (
                        'ACC201-01',
                        '基础会计学',
                        'upload/accounting.jpg',
                        '王华',
                        '9787300317650',
                        'ACC201',
                        '第2版',
                        '会计学,财务管理',
                        '基础会计学',
                        '经济',
                        '经济管理学院',
                        '会计学',
                        '基础会计学',
                        '第2版',
                        '会计学核心教材，适合大一专业基础课。',
                        '八成新',
                        '中国人民大学出版社',
                        '2026-03-03',
                        20220012,
                        '20220012',
                        '陈同学',
                        28,
                        1,
                    ),
                ]
                for book in books:
                    cur.execute(
                        """
                        INSERT INTO ershoushuji
                        (
                          shujibianhao, shujimingcheng, shujifengmian, shujizuozhe, isbn, kechengbianhao,
                          jiaocaibanben, shiyongzhuanye, shiyongkecheng, shujifenlei, xueyuan, zhuanye,
                          kecheng, banben, shujijianjie, xinjiuchengdu, chubanshe, shangjiariqi,
                          faburenid, faburenzhanghao, faburenxingming, price, kucun
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        book,
                    )
                print(f"[OK] 导入 {len(books)} 条书籍数据")
            else:
                print('[SKIP] 书籍数据已存在')

        conn.commit()
        print('========== 示例数据导入完成 ==========')
    finally:
        conn.close()


if __name__ == '__main__':
    seed()
