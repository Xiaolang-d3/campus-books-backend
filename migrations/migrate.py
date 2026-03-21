"""
Database bootstrap - creates all normalized tables.
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


def get_connection(database=None):
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=database,
        charset='utf8mb4',
    )


def create_database():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        print(f"[OK] 数据库 `{DB_NAME}` 已就绪")
    finally:
        conn.close()


def create_tables():
    conn = get_connection(database=DB_NAME)
    tables = [
        """
        CREATE TABLE IF NOT EXISTS `admin` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `username` VARCHAR(50) NOT NULL UNIQUE,
          `password` VARCHAR(100) NOT NULL,
          `role` VARCHAR(50) DEFAULT '管理员',
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员'
        """,
        """
        CREATE TABLE IF NOT EXISTS `college` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `name` VARCHAR(100) NOT NULL UNIQUE,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学院'
        """,
        """
        CREATE TABLE IF NOT EXISTS `major` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `name` VARCHAR(100) NOT NULL,
          `college_id` BIGINT,
          `year` INT,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (college_id) REFERENCES `college`(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业'
        """,
        """
        CREATE TABLE IF NOT EXISTS `course` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `name` VARCHAR(100) NOT NULL,
          `code` VARCHAR(50) UNIQUE,
          `major_id` BIGINT,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (major_id) REFERENCES `major`(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程'
        """,
        """
        CREATE TABLE IF NOT EXISTS `book_category` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `name` VARCHAR(100) NOT NULL UNIQUE,
          `icon` VARCHAR(50),
          `sort` INT DEFAULT 0,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='书籍分类'
        """,
        """
        CREATE TABLE IF NOT EXISTS `condition_level` (
          `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `name` VARCHAR(50) NOT NULL UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='新旧程度'
        """,
        """
        CREATE TABLE IF NOT EXISTS `user` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `student_no` VARCHAR(50) NOT NULL UNIQUE,
          `name` VARCHAR(50) NOT NULL,
          `password` VARCHAR(100) NOT NULL,
          `gender` VARCHAR(10),
          `avatar` VARCHAR(255),
          `phone` VARCHAR(20),
          `college_id` BIGINT,
          `major_id` BIGINT,
          `grade` VARCHAR(20),
          `balance` DECIMAL(10,2) DEFAULT 0,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (college_id) REFERENCES `college`(id) ON DELETE SET NULL,
          FOREIGN KEY (major_id) REFERENCES `major`(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='校园用户'
        """,
        """
        CREATE TABLE IF NOT EXISTS `book` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `isbn` VARCHAR(50) UNIQUE,
          `title` VARCHAR(200) NOT NULL,
          `author` VARCHAR(200),
          `cover` VARCHAR(255),
          `publisher` VARCHAR(200),
          `description` TEXT,
          `category_id` BIGINT,
          `condition_id` INT,
          `seller_id` BIGINT NOT NULL,
          `price` DECIMAL(10,2) NOT NULL,
          `original_price` DECIMAL(10,2),
          `stock` INT DEFAULT 1,
          `status` TINYINT DEFAULT 1,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          `updatetime` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          FOREIGN KEY (category_id) REFERENCES `book_category`(id) ON DELETE SET NULL,
          FOREIGN KEY (condition_id) REFERENCES `condition_level`(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='二手书籍'
        """,
        """
        CREATE TABLE IF NOT EXISTS `address` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` BIGINT NOT NULL,
          `contact_name` VARCHAR(50) NOT NULL,
          `phone` VARCHAR(20) NOT NULL,
          `province` VARCHAR(50),
          `city` VARCHAR(50),
          `district` VARCHAR(50),
          `detail` VARCHAR(255) NOT NULL,
          `is_default` TINYINT DEFAULT 0,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES `user`(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收货地址'
        """,
        """
        CREATE TABLE IF NOT EXISTS `order` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `order_no` VARCHAR(50) NOT NULL UNIQUE,
          `user_id` BIGINT NOT NULL,
          `book_id` BIGINT NOT NULL,
          `seller_id` BIGINT NOT NULL,
          `book_title` VARCHAR(200),
          `book_cover` VARCHAR(255),
          `book_isbn` VARCHAR(50),
          `condition_name` VARCHAR(50),
          `price` DECIMAL(10,2) NOT NULL,
          `quantity` INT NOT NULL DEFAULT 1,
          `total_amount` DECIMAL(10,2) NOT NULL,
          `status` VARCHAR(50),
          `pay_type` INT,
          `address_id` BIGINT,
          `receiver_name` VARCHAR(50),
          `receiver_phone` VARCHAR(20),
          `receiver_address` VARCHAR(255),
          `remark` VARCHAR(255),
          `logistics` TEXT,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          `updatetime` DATETIME,
          FOREIGN KEY (user_id) REFERENCES `user`(id) ON DELETE CASCADE,
          FOREIGN KEY (book_id) REFERENCES `book`(id) ON DELETE RESTRICT,
          FOREIGN KEY (seller_id) REFERENCES `user`(id) ON DELETE RESTRICT,
          FOREIGN KEY (address_id) REFERENCES address(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单'
        """,
        """
        CREATE TABLE IF NOT EXISTS `cart` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` BIGINT NOT NULL,
          `book_id` BIGINT NOT NULL,
          `quantity` INT DEFAULT 1,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          UNIQUE KEY `uk_user_book` (`user_id`, `book_id`),
          FOREIGN KEY (user_id) REFERENCES `user`(id) ON DELETE CASCADE,
          FOREIGN KEY (book_id) REFERENCES `book`(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='购物车'
        """,
        """
        CREATE TABLE IF NOT EXISTS `book_view` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` BIGINT NOT NULL,
          `book_id` BIGINT NOT NULL,
          `view_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES `user`(id) ON DELETE CASCADE,
          FOREIGN KEY (book_id) REFERENCES `book`(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='浏览历史'
        """,
        """
        CREATE TABLE IF NOT EXISTS `favorite` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` BIGINT NOT NULL,
          `book_id` BIGINT NOT NULL,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          UNIQUE KEY `uk_user_book` (`user_id`, `book_id`),
          FOREIGN KEY (user_id) REFERENCES `user`(id) ON DELETE CASCADE,
          FOREIGN KEY (book_id) REFERENCES `book`(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏'
        """,
        """
        CREATE TABLE IF NOT EXISTS `review` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` BIGINT NOT NULL,
          `book_id` BIGINT NOT NULL,
          `order_id` BIGINT,
          `rating` TINYINT NOT NULL,
          `content` TEXT,
          `reply` TEXT,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES `user`(id) ON DELETE CASCADE,
          FOREIGN KEY (book_id) REFERENCES `book`(id) ON DELETE CASCADE,
          FOREIGN KEY (order_id) REFERENCES `order`(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='书籍评分评价'
        """,
        """
        CREATE TABLE IF NOT EXISTS `news` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          `title` VARCHAR(200) NOT NULL,
          `introduction` TEXT,
          `picture` TEXT NOT NULL,
          `content` TEXT NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公告信息'
        """,
        """
        CREATE TABLE IF NOT EXISTS `aboutus` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          `title` VARCHAR(200) NOT NULL,
          `subtitle` VARCHAR(200),
          `content` TEXT NOT NULL,
          `picture1` TEXT,
          `picture2` TEXT,
          `picture3` TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='关于我们'
        """,
        """
        CREATE TABLE IF NOT EXISTS `systemintro` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP,
          `title` VARCHAR(200) NOT NULL,
          `subtitle` VARCHAR(200),
          `content` TEXT NOT NULL,
          `picture1` TEXT,
          `picture2` TEXT,
          `picture3` TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统简介'
        """,
        """
        CREATE TABLE IF NOT EXISTS `config` (
          `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `name` VARCHAR(100) NOT NULL,
          `value` VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配置'
        """,
    ]

    try:
        with conn.cursor() as cur:
            for ddl in tables:
                cur.execute(ddl)
        conn.commit()
        print('[OK] 所有表已创建')
    finally:
        conn.close()


def seed_data():
    conn = get_connection(database=DB_NAME)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM `admin`")
            if cur.fetchone()[0] > 0:
                print('[SKIP] 基础数据已存在，跳过')
            else:
                cur.execute(
                    "INSERT INTO `admin` (`username`, `password`, `role`) VALUES ('admin', 'admin', '管理员')"
                )
                print('[OK] 管理员数据已插入')

            cur.execute("SELECT COUNT(*) FROM `college`")
            if cur.fetchone()[0] > 0:
                print('[SKIP] 学院数据已存在，跳过')
            else:
                for college in ['计算机学院', '文学院', '经济管理学院', '理学院']:
                    cur.execute("INSERT INTO `college` (`name`) VALUES (%s)", (college,))

                majors = [
                    ('软件工程', 1), ('计算机科学与技术', 1),
                    ('汉语言文学', 2), ('新闻学', 2),
                    ('会计学', 3), ('国际经济与贸易', 3),
                    ('数学与应用数学', 4), ('物理学', 4),
                ]
                for name, college_id in majors:
                    cur.execute("INSERT INTO `major` (`name`, `college_id`) VALUES (%s, %s)", (name, college_id))

                courses = [
                    ('软件工程导论', 'CS101', 1), ('数据结构', 'CS102', 1), ('操作系统', 'CS103', 1),
                    ('计算机组成原理', 'CS201', 2), ('数据库系统', 'CS202', 2), ('计算机网络', 'CS203', 2),
                    ('中国现代文学', 'CL101', 3), ('古代汉语', 'CL102', 3),
                    ('新闻采访与写作', 'JM101', 4), ('传播学概论', 'JM102', 4),
                    ('基础会计', 'EM101', 5), ('财务管理', 'EM102', 5),
                    ('国际贸易实务', 'EM201', 6), ('西方经济学', 'EM202', 6),
                    ('高等数学', 'SC101', 7), ('线性代数', 'SC102', 7),
                    ('大学物理', 'SC201', 8), ('理论力学', 'SC202', 8),
                ]
                for name, code, major_id in courses:
                    cur.execute("INSERT INTO `course` (`name`, `code`, `major_id`) VALUES (%s, %s, %s)", (name, code, major_id))

                categories = ['文学', '计算机', '历史', '哲学', '经济', '教育', '艺术', '科学']
                for i, cat in enumerate(categories, 1):
                    cur.execute("INSERT INTO `book_category` (`name`, `sort`) VALUES (%s, %s)", (cat, i))

                conditions = ['全新', '九成新', '八成新', '七成新', '六成及以下']
                for cond in conditions:
                    cur.execute("INSERT INTO `condition_level` (`name`) VALUES (%s)", (cond,))

                for name, value in [
                    ('picture1', 'picture1.jpg'),
                    ('picture2', 'picture2.jpg'),
                    ('picture3', 'picture3.jpg'),
                ]:
                    cur.execute("INSERT INTO `config` (`name`, `value`) VALUES (%s, %s)", (name, value))

                cur.execute(
                    "INSERT INTO `aboutus` (`title`, `subtitle`, `content`) VALUES (%s, %s, %s)",
                    ('关于我们', 'ABOUT US', '校园二手专业书平台，服务校内教材流转与供需匹配。'),
                )
                cur.execute(
                    "INSERT INTO `systemintro` (`title`, `subtitle`, `content`) VALUES (%s, %s, %s)",
                    ('系统简介', 'SYSTEM INTRODUCTION', '系统支持校园用户发布、浏览、购买和管理二手专业书籍。'),
                )
                cur.execute(
                    "INSERT INTO `news` (`title`, `introduction`, `picture`, `content`) VALUES (%s, %s, %s, %s)",
                    (
                        '欢迎使用校园二手专业书平台',
                        '平台已完成基础功能初始化，可直接用于演示与开发。',
                        'news_picture1.jpg',
                        '<p>欢迎使用校园二手专业书平台，当前版本已支持校园用户同时进行买书和卖书。</p>',
                    ),
                )
                print('[OK] 基础数据已插入')

            cur.execute("SELECT COUNT(*) FROM `user`")
            if cur.fetchone()[0] > 0:
                print('[SKIP] 用户数据已存在，跳过')
            else:
                users = [
                    ('20220011', '王同学', '123456', '男', '13800138111', 1, 1, '2022级', 300.00),
                    ('20220012', '陈同学', '123456', '女', '13800138112', 3, 5, '2021级', 600.00),
                    ('20220013', '赵同学', '123456', '男', '13800138113', 2, 3, '2023级', 120.00),
                ]
                for user in users:
                    cur.execute(
                        "INSERT INTO `user` (`student_no`, `name`, `password`, `gender`, `phone`, `college_id`, `major_id`, `grade`, `balance`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        user,
                    )
                print(f'[OK] 导入 {len(users)} 条用户数据')

            cur.execute("SELECT COUNT(*) FROM `book`")
            if cur.fetchone()[0] > 0:
                print('[SKIP] 书籍数据已存在，跳过')
            else:
                books = [
                    ('9787302147514', '数据结构', '严蔚敏', 'datastructure.jpg', '清华大学出版社', '软件工程专业核心课程教材，内容涵盖线性表、栈、队列、树、图等数据结构。', 2, 2, 1, 35.00, 59.00, 2, 1),
                    ('9787300283399', '金融学', '黄达', 'algorithm.jpg', '中国人民大学出版社', '金融学专业核心教材，系统介绍货币银行学与国际金融知识。', 5, 3, 2, 42.00, 68.00, 1, 1),
                    ('9787040548505', '中国现代文学史', '朱栋霖', 'literature.jpg', '高等教育出版社', '文学院专业核心课程教材，梳理中国现代文学发展脉络。', 1, 2, 3, 30.00, 48.00, 3, 1),
                    ('9787302492850', '操作系统原理', '汤小丹', 'csapp.jpg', '西安电子科技大学出版社', '计算机专业核心课程教材，详细讲解操作系统基本概念与实现技术。', 2, 2, 1, 38.00, 65.00, 2, 1),
                    ('9787302348950', '数据库系统概论', '王珊', 'mysql.jpg', '高等教育出版社', '数据库系统经典教材，涵盖关系数据库、SQL、事务处理等内容。', 2, 2, 1, 32.00, 55.00, 4, 1),
                    ('9787302607599', 'Python程序设计', '董付国', 'python.jpg', '清华大学出版社', 'Python入门教材，适合程序设计基础课程学习。', 2, 1, 1, 28.00, 45.00, 3, 1),
                    ('9787300317650', '基础会计学', '王华', 'capital.jpg', '中国人民大学出版社', '会计学核心教材，适合大一专业基础课。', 5, 3, 2, 28.00, 42.00, 2, 1),
                    ('9787302428019', '微观经济学', '高鸿业', 'economics.jpg', '中国人民大学出版社', '经济学专业基础教材，系统介绍供需理论、消费者行为等。', 5, 6, 2, 25.00, 38.00, 3, 1),
                ]
                for book in books:
                    cur.execute(
                        "INSERT INTO `book` (`isbn`, `title`, `author`, `cover`, `publisher`, `description`, `category_id`, `condition_id`, `seller_id`, `price`, `original_price`, `stock`, `status`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        book,
                    )
                print(f'[OK] 导入 {len(books)} 条书籍数据')

        conn.commit()
        print('[OK] 示例数据导入完成')
    finally:
        conn.close()


def migrate():
    print('========== 开始数据库迁移 ==========')
    create_database()
    create_tables()
    seed_data()
    print('========== 迁移完成 ==========')


if __name__ == '__main__':
    migrate()
