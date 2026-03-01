"""
导入 Spring Boot 项目的示例数据
用法: python -m migrations.seed_data
"""
import sys
import os
import yaml
import pymysql
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
with open(_config_file, 'r', encoding='utf-8') as f:
    _cfg = yaml.safe_load(f)

_db_uri = _cfg['database']['uri']
_parsed = urlparse(_db_uri.replace('mysql+pymysql://', 'mysql://'))
DB_HOST = _parsed.hostname or '127.0.0.1'
DB_PORT = _parsed.port or 3306
DB_USER = _parsed.username or 'root'
DB_PASS = _parsed.password or ''
DB_NAME = _parsed.path.lstrip('/').split('?')[0]


def get_connection():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS,
        database=DB_NAME, charset='utf8mb4',
    )


def seed():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 检查是否已导入
            cur.execute("SELECT COUNT(*) FROM shangjia")
            if cur.fetchone()[0] > 0:
                print("[SKIP] 商家数据已存在")
            else:
                shangjia = [
                    (21, '商家姓名1', '商家账号1', '123456', '男', 'upload/shangjia_touxiang1.jpg', '13823888881', 200),
                    (22, '商家姓名2', '商家账号2', '123456', '男', 'upload/shangjia_touxiang2.jpg', '13823888882', 200),
                    (23, '商家姓名3', '商家账号3', '123456', '男', 'upload/shangjia_touxiang3.jpg', '13823888883', 200),
                    (24, '商家姓名4', '商家账号4', '123456', '男', 'upload/shangjia_touxiang4.jpg', '13823888884', 200),
                    (25, '商家姓名5', '商家账号5', '123456', '男', 'upload/shangjia_touxiang5.jpg', '13823888885', 200),
                    (26, '商家姓名6', '商家账号6', '123456', '男', 'upload/shangjia_touxiang6.jpg', '13823888886', 200),
                    (27, '商家姓名7', '商家账号7', '123456', '男', 'upload/shangjia_touxiang7.jpg', '13823888887', 200),
                    (28, '商家姓名8', '商家账号8', '123456', '男', 'upload/shangjia_touxiang8.jpg', '13823888888', 200),
                ]
                for s in shangjia:
                    cur.execute(
                        "INSERT INTO shangjia (id, shangjiaxingming, shangjiazhanghao, mima, xingbie, touxiang, dianhuahaoma, money) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", s
                    )
                print(f"[OK] 导入 {len(shangjia)} 条商家数据")

            cur.execute("SELECT COUNT(*) FROM yonghu")
            if cur.fetchone()[0] > 0:
                print("[SKIP] 用户数据已存在")
            else:
                yonghu = [
                    (11, '用户账号1', '用户姓名1', '123456', '男', 'upload/yonghu_touxiang1.jpg', '13823888881', 200),
                    (12, '用户账号2', '用户姓名2', '123456', '男', 'upload/yonghu_touxiang2.jpg', '13823888882', 200),
                    (13, '用户账号3', '用户姓名3', '123456', '男', 'upload/yonghu_touxiang3.jpg', '13823888883', 200),
                    (14, '用户账号4', '用户姓名4', '123456', '男', 'upload/yonghu_touxiang4.jpg', '13823888884', 200),
                    (15, '用户账号5', '用户姓名5', '123456', '男', 'upload/yonghu_touxiang5.jpg', '13823888885', 200),
                    (16, '用户账号6', '用户姓名6', '123456', '男', 'upload/yonghu_touxiang6.jpg', '13823888886', 200),
                    (17, '用户账号7', '用户姓名7', '123456', '男', 'upload/yonghu_touxiang7.jpg', '13823888887', 200),
                    (18, '用户账号8', '用户姓名8', '123456', '男', 'upload/yonghu_touxiang8.jpg', '13823888888', 200),
                ]
                for u in yonghu:
                    cur.execute(
                        "INSERT INTO yonghu (id, yonghuzhanghao, yonghuxingming, mima, xingbie, touxiang, dianhuahaoma, money) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", u
                    )
                print(f"[OK] 导入 {len(yonghu)} 条用户数据")

            cur.execute("SELECT COUNT(*) FROM ershoushuji")
            if cur.fetchone()[0] > 0:
                print("[SKIP] 书籍数据已存在")
            else:
                books = [
                    (41, '1111111111', '书籍名称1', 'upload/ershoushuji_shujifengmian1.jpg', '书籍作者1', '文学', '经典文学作品，值得一读', '全新', '人民文学出版社', '2026-02-10', '商家账号1', '商家姓名1', 29.9),
                    (42, '2222222222', '书籍名称2', 'upload/ershoushuji_shujifengmian2.jpg', '书籍作者2', '计算机', 'Python编程入门经典教材', '全新', '清华大学出版社', '2026-02-10', '商家账号2', '商家姓名2', 45.0),
                    (43, '3333333333', '书籍名称3', 'upload/ershoushuji_shujifengmian3.jpg', '书籍作者3', '历史', '中国历史通俗读物', '九成新', '中华书局', '2026-02-10', '商家账号3', '商家姓名3', 35.5),
                    (44, '4444444444', '书籍名称4', 'upload/ershoushuji_shujifengmian4.jpg', '书籍作者4', '哲学', '西方哲学入门', '全新', '商务印书馆', '2026-02-10', '商家账号4', '商家姓名4', 28.0),
                    (45, '5555555555', '书籍名称5', 'upload/ershoushuji_shujifengmian5.jpg', '书籍作者5', '经济', '经济学原理', '九成新', '北京大学出版社', '2026-02-10', '商家账号5', '商家姓名5', 52.0),
                    (46, '6666666666', '书籍名称6', 'upload/ershoushuji_shujifengmian6.jpg', '书籍作者6', '教育', '教育心理学', '全新', '华东师范大学出版社', '2026-02-10', '商家账号6', '商家姓名6', 38.0),
                    (47, '7777777777', '书籍名称7', 'upload/ershoushuji_shujifengmian7.jpg', '书籍作者7', '艺术', '艺术的故事', '八成新', '广西美术出版社', '2026-02-10', '商家账号7', '商家姓名7', 66.0),
                    (48, '8888888888', '书籍名称8', 'upload/ershoushuji_shujifengmian8.jpg', '书籍作者8', '科学', '时间简史', '全新', '湖南科学技术出版社', '2026-02-10', '商家账号8', '商家姓名8', 42.0),
                ]
                for b in books:
                    cur.execute(
                        "INSERT INTO ershoushuji (id, shujibianhao, shujimingcheng, shujifengmian, shujizuozhe, shujifenlei, shujijianjie, xinjiuchengdu, chubanshe, shangjiariqi, shangjiazhanghao, shangjiaxingming, price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", b
                    )
                print(f"[OK] 导入 {len(books)} 条书籍数据")

        conn.commit()
        print("========== 数据导入完成 ==========")
    finally:
        conn.close()


if __name__ == '__main__':
    seed()
