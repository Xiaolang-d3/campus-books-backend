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
                    # 计算机类
                    ('9787302147514', '数据结构（C语言版）', '严蔚敏 吴伟民', 'https://img1.doubanio.com/view/subject/l/public/s30016908.jpg', '清华大学出版社', '本书是计算机科学与技术专业的核心基础课程教材，系统介绍了线性表、栈、队列、树、图等基本数据结构，以及查找和排序的各类算法。配套C语言实现代码，适合考研和课程学习。', 2, 2, 1, 28.00, 45.00, 3, 1),
                    ('9787302492850', '计算机网络（第7版）', '谢希仁', 'https://img1.doubanio.com/view/subject/l/public/s30016454.jpg', '电子工业出版社', '计算机网络经典教材，系统阐述计算机网络体系结构、物理层、数据链路层、网络层、传输层、应用层等核心内容，配套PPT和习题答案。', 2, 2, 1, 32.00, 52.00, 2, 1),
                    ('9787302348950', '数据库系统概论（第5版）', '王珊 萨师煊', 'https://img1.doubanio.com/view/subject/l/public/s27243621.jpg', '高等教育出版社', '数据库系统经典教材，全面介绍关系数据库、SQL语言、数据库设计、事务管理、并发控制、数据库恢复等核心知识。', 2, 3, 1, 25.00, 42.00, 2, 1),
                    ('9787302585874', '软件工程导论（第6版）', '张海藩 牟永敏', 'https://img1.doubanio.com/view/subject/l/public/s24514483.jpg', '清华大学出版社', '软件工程专业基础教材，涵盖软件过程模型、需求分析、系统设计、测试与维护等内容。', 2, 2, 1, 26.00, 38.00, 3, 1),
                    # 数学类
                    ('9787302185424', '高等数学（第7版）上册', '同济大学数学系', 'https://img1.doubanio.com/view/subject/l/public/s27263085.jpg', '高等教育出版社', '工科院校高等数学经典教材，内容包括函数与极限、导数与微分、微分中值定理与导数应用、不定积分、定积分及其应用等。', 8, 3, 2, 22.00, 35.00, 3, 1),
                    ('9787302185431', '高等数学（第7版）下册', '同济大学数学系', 'https://img1.doubanio.com/view/subject/l/public/s27263090.jpg', '高等教育出版社', '工科院校高等数学经典教材下册，内容包括向量与空间解析几何、多元函数微分法及其应用、重积分、曲线积分与曲面积分、无穷级数等。', 8, 2, 2, 24.00, 38.00, 2, 1),
                    ('9787302529044', '线性代数（第6版）', '同济大学数学系', 'https://img1.doubanio.com/view/subject/l/public/s29820966.jpg', '高等教育出版社', '线性代数经典教材，内容包括行列式、矩阵及其运算、向量组的线性相关性、相似矩阵及二次型、线性空间与线性变换等。', 8, 3, 1, 18.00, 28.00, 4, 1),
                    ('9787302332263', '概率论与数理统计（第4版）', '盛骤 谢式千 潘承毅', 'https://img1.doubanio.com/view/subject/l/public/s33868644.jpg', '高等教育出版社', '概率论与数理统计基础教材，内容包括概率论基本概念、随机变量及其分布、多维随机变量、大数定律与中心极限定理、样本与抽样分布、参数估计、假设检验等。', 8, 2, 1, 26.00, 42.00, 2, 1),
                    # 经济管理类
                    ('9787302428019', '西方经济学（微观部分 第7版）', '高鸿业', 'https://img1.doubanio.com/view/subject/l/public/s29653804.jpg', '中国人民大学出版社', '经济学专业基础教材，系统介绍供求理论、消费者行为理论、生产者行为理论、市场理论、要素市场理论、一般均衡与福利经济学、市场失灵与政府干预等。', 5, 3, 2, 24.00, 38.00, 3, 1),
                    ('9787300249944', '西方经济学（宏观部分 第7版）', '高鸿业', 'https://img1.doubanio.com/view/subject/l/public/s29653810.jpg', '中国人民大学出版社', '宏观经济学经典教材，内容涵盖国民收入核算、简单国民收入决定理论、产品市场和货币市场的一般均衡、宏观经济政策、失业与通货膨胀、经济增长等。', 5, 2, 2, 26.00, 40.00, 2, 1),
                    ('9787300317650', '基础会计学（第2版）', '王华', 'https://img1.doubanio.com/view/subject/l/public/s27241632.jpg', '中国人民大学出版社', '会计学入门教材，内容包括会计基本理论、会计科目与账户、复式记账原理、主要经济业务核算、会计凭证、账簿、报表等。', 5, 3, 2, 22.00, 35.00, 3, 1),
                    # 文学语言类
                    ('9787040548505', '中国现代文学史（第2版）', '朱栋霖', 'https://img1.doubanio.com/view/subject/l/public/s29813717.jpg', '高等教育出版社', '中文专业核心教材，系统梳理1917年至1949年中国现代文学的发展历程，涵盖重要作家作品、文学思潮与流派。', 1, 2, 3, 28.00, 45.00, 2, 1),
                    ('9787101007995', '古代汉语（校订重排本 第1册）', '王力 主编', 'https://img1.doubanio.com/view/subject/l/public/s10796758.jpg', '中华书局', '古代汉语经典教材，文选部分选录先秦至汉代的散文和韵文，读本部分包括语法常识和古代文化知识，附有常用词释义。', 1, 3, 3, 20.00, 32.00, 2, 1),
                    # 大学物理
                    ('9787040410322', '大学物理（第3版）', '张三慧', 'https://img1.doubanio.com/view/subject/l/public/s29949133.jpg', '清华大学出版社', '工科物理基础教材，内容包括力学、热学、电磁学、光学和量子物理基础，配有丰富的例题和习题。', 8, 2, 1, 35.00, 55.00, 2, 1),
                    # 大学英语
                    ('9787544653247', '新视野大学英语（读写教程1）', '郑树棠', 'https://img1.doubanio.com/view/subject/l/public/s28115841.jpg', '外语教学与研究出版社', '大学英语精读教材第一册，包含8个单元，涵盖校园生活、学习方法、文化交流等主题，配有音频和视频资料。', 6, 2, 2, 18.00, 28.00, 4, 1),
                    # 马克思主义基本原理
                    ('9787040441838', '马克思主义基本原理概论（2018年版）', '本书编写组', 'https://img1.doubanio.com/view/subject/l/public/s29957537.jpg', '高等教育出版社', '高校思想政治理论课教材，系统阐述马克思主义的哲学、政治经济学和科学社会主义基本原理。', 6, 3, 1, 16.00, 25.00, 3, 1),
                    # 系统解剖学
                    ('9787117244050', '系统解剖学（第9版）', '柏树令 丁文龙', 'https://img1.doubanio.com/view/subject/l/public/s33871822.jpg', '人民卫生出版社', '临床医学专业基础课程教材，系统介绍人体各系统的组成、形态结构和功能关系，配有精美插图和配套习题集。', 6, 2, 1, 38.00, 65.00, 1, 1),
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
