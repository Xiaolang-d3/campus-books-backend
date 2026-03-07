"""
Database bootstrap and lightweight schema migration helpers.
"""

import os
import sys
from urllib.parse import urlparse

import pymysql
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
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
        print(f"[OK] 数据库 '{DB_NAME}' 已就绪")
    finally:
        conn.close()


def create_tables():
    tables = [
        """
        CREATE TABLE IF NOT EXISTS `users` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `username` varchar(100) NOT NULL UNIQUE,
          `password` varchar(100) NOT NULL,
          `role` varchar(100) DEFAULT '管理员',
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员'
        """,
        """
        CREATE TABLE IF NOT EXISTS `yonghu` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `yonghuzhanghao` varchar(200) NOT NULL UNIQUE COMMENT '学号',
          `yonghuxingming` varchar(200) NOT NULL COMMENT '姓名',
          `mima` varchar(200) NOT NULL COMMENT '密码',
          `xingbie` varchar(200) DEFAULT NULL COMMENT '性别',
          `touxiang` text COMMENT '头像',
          `dianhuahaoma` varchar(200) DEFAULT NULL COMMENT '电话号码',
          `xueyuan` varchar(200) NOT NULL DEFAULT '' COMMENT '学院',
          `zhuanye` varchar(200) NOT NULL DEFAULT '' COMMENT '专业',
          `nianji` varchar(200) NOT NULL DEFAULT '' COMMENT '年级',
          `money` float DEFAULT 0 COMMENT '余额',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户'
        """,
        """
        CREATE TABLE IF NOT EXISTS `shangjia` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `shangjiaxingming` varchar(200) NOT NULL COMMENT '商家姓名',
          `shangjiazhanghao` varchar(200) NOT NULL UNIQUE COMMENT '商家账号',
          `mima` varchar(200) NOT NULL COMMENT '密码',
          `xingbie` varchar(200) DEFAULT NULL COMMENT '性别',
          `touxiang` text COMMENT '头像',
          `dianhuahaoma` varchar(200) DEFAULT NULL COMMENT '电话号码',
          `money` float DEFAULT 0 COMMENT '余额',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商家'
        """,
        """
        CREATE TABLE IF NOT EXISTS `shujifenlei` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `shujifenlei` varchar(200) NOT NULL COMMENT '书籍分类',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='书籍分类'
        """,
        """
        CREATE TABLE IF NOT EXISTS `ershoushuji` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `shujibianhao` varchar(200) UNIQUE COMMENT '书籍编号',
          `shujimingcheng` varchar(200) COMMENT '书籍名称',
          `shujifengmian` text COMMENT '书籍封面',
          `shujizuozhe` varchar(200) COMMENT '书籍作者',
          `isbn` varchar(50) NOT NULL DEFAULT '' COMMENT 'ISBN',
          `kechengbianhao` varchar(100) NOT NULL DEFAULT '' COMMENT '课程编号',
          `jiaocaibanben` varchar(200) NOT NULL DEFAULT '' COMMENT '教材版本',
          `shiyongzhuanye` varchar(200) NOT NULL DEFAULT '' COMMENT '适用专业',
          `shiyongkecheng` varchar(200) NOT NULL DEFAULT '' COMMENT '适用课程',
          `shujifenlei` varchar(200) COMMENT '书籍分类',
          `xueyuan` varchar(200) NOT NULL DEFAULT '' COMMENT '学院',
          `zhuanye` varchar(200) NOT NULL DEFAULT '' COMMENT '专业',
          `kecheng` varchar(200) NOT NULL DEFAULT '' COMMENT '课程',
          `banben` varchar(200) NOT NULL DEFAULT '' COMMENT '版本',
          `shujijianjie` text COMMENT '书籍简介',
          `xinjiuchengdu` varchar(200) COMMENT '新旧程度',
          `chubanshe` varchar(200) COMMENT '出版社',
          `shangjiariqi` date COMMENT '上架日期',
          `shangjiazhanghao` varchar(200) COMMENT '商家账号',
          `shangjiaxingming` varchar(200) COMMENT '商家姓名',
          `price` float NOT NULL COMMENT '价格',
          `kucun` int DEFAULT 1 COMMENT '库存数量',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='二手书籍'
        """,
        """
        CREATE TABLE IF NOT EXISTS `orders` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `orderid` varchar(200) NOT NULL UNIQUE COMMENT '订单编号',
          `tablename` varchar(200) DEFAULT 'ershoushuji' COMMENT '商品表名',
          `userid` bigint NOT NULL COMMENT '用户id',
          `goodid` bigint NOT NULL COMMENT '商品id',
          `goodname` varchar(200) COMMENT '商品名称',
          `picture` text COMMENT '商品图片',
          `buynumber` int NOT NULL COMMENT '购买数量',
          `price` float NOT NULL DEFAULT 0 COMMENT '价格',
          `discountprice` float DEFAULT 0 COMMENT '折扣价格',
          `total` float NOT NULL DEFAULT 0 COMMENT '总价格',
          `discounttotal` float DEFAULT 0 COMMENT '折扣总价格',
          `type` int DEFAULT 1 COMMENT '支付类型',
          `status` varchar(200) COMMENT '状态',
          `address` varchar(200) COMMENT '地址',
          `tel` varchar(200) COMMENT '电话',
          `consignee` varchar(200) COMMENT '收货人',
          `remark` varchar(200) COMMENT '备注',
          `logistics` text COMMENT '物流',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单'
        """,
        """
        CREATE TABLE IF NOT EXISTS `cart` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `tablename` varchar(200) DEFAULT 'ershoushuji' COMMENT '商品表名',
          `userid` bigint NOT NULL COMMENT '用户id',
          `goodid` bigint NOT NULL COMMENT '商品id',
          `goodname` varchar(200) COMMENT '商品名称',
          `picture` text COMMENT '图片',
          `buynumber` int NOT NULL COMMENT '购买数量',
          `price` float COMMENT '单价',
          `discountprice` float COMMENT '会员价',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='购物车'
        """,
        """
        CREATE TABLE IF NOT EXISTS `address` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `userid` bigint NOT NULL COMMENT '用户id',
          `address` varchar(200) NOT NULL COMMENT '地址',
          `name` varchar(200) NOT NULL COMMENT '收货人',
          `phone` varchar(200) NOT NULL COMMENT '电话',
          `isdefault` varchar(200) NOT NULL COMMENT '是否默认地址',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='地址'
        """,
        """
        CREATE TABLE IF NOT EXISTS `news` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `title` varchar(200) NOT NULL COMMENT '标题',
          `introduction` text COMMENT '简介',
          `picture` text NOT NULL COMMENT '图片',
          `content` text NOT NULL COMMENT '内容',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公告信息'
        """,
        """
        CREATE TABLE IF NOT EXISTS `aboutus` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `title` varchar(200) NOT NULL,
          `subtitle` varchar(200),
          `content` text NOT NULL,
          `picture1` text,
          `picture2` text,
          `picture3` text,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='关于我们'
        """,
        """
        CREATE TABLE IF NOT EXISTS `systemintro` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `title` varchar(200) NOT NULL,
          `subtitle` varchar(200),
          `content` text NOT NULL,
          `picture1` text,
          `picture2` text,
          `picture3` text,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统简介'
        """,
        """
        CREATE TABLE IF NOT EXISTS `discussershoushuji` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `refid` bigint NOT NULL COMMENT '关联表id',
          `userid` bigint NOT NULL COMMENT '用户id',
          `avatarurl` text COMMENT '头像',
          `nickname` varchar(200) COMMENT '用户昵称',
          `content` text NOT NULL COMMENT '评论内容',
          `reply` text COMMENT '回复内容',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='二手书籍评论'
        """,
        """
        CREATE TABLE IF NOT EXISTS `storeup` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
          `userid` bigint NOT NULL COMMENT '用户id',
          `refid` bigint COMMENT '商品id',
          `tablename` varchar(200) COMMENT '表名',
          `name` varchar(200) NOT NULL COMMENT '名称',
          `picture` text NOT NULL COMMENT '图片',
          `type` varchar(200) DEFAULT '1' COMMENT '类型',
          `inteltype` varchar(200) COMMENT '推荐类型',
          `remark` varchar(200) COMMENT '备注',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏'
        """,
        """
        CREATE TABLE IF NOT EXISTS `config` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `name` varchar(100) NOT NULL COMMENT '配置参数名称',
          `value` varchar(100) COMMENT '配置参数值',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配置'
        """,
    ]

    conn = get_connection(database=DB_NAME)
    try:
        with conn.cursor() as cur:
            for ddl in tables:
                cur.execute(ddl)
        conn.commit()
        print('[OK] 所有表已创建')
    finally:
        conn.close()


def ensure_column_exists(table_name, column_name, ddl):
    conn = get_connection(database=DB_NAME)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE %s", (column_name,))
            if not cur.fetchone():
                print(f"[MIGRATE] 添加字段 {table_name}.{column_name} ...")
                cur.execute(f"ALTER TABLE `{table_name}` ADD COLUMN {ddl}")
        conn.commit()
    finally:
        conn.close()


def patch_existing_schema():
    ensure_column_exists('ershoushuji', 'kucun', "`kucun` int DEFAULT 1 COMMENT '库存数量' AFTER `price`")
    ensure_column_exists('ershoushuji', 'isbn', "`isbn` varchar(50) NOT NULL DEFAULT '' COMMENT 'ISBN' AFTER `shujizuozhe`")
    ensure_column_exists('ershoushuji', 'kechengbianhao', "`kechengbianhao` varchar(100) NOT NULL DEFAULT '' COMMENT '课程编号' AFTER `isbn`")
    ensure_column_exists('ershoushuji', 'jiaocaibanben', "`jiaocaibanben` varchar(200) NOT NULL DEFAULT '' COMMENT '教材版本' AFTER `kechengbianhao`")
    ensure_column_exists('ershoushuji', 'shiyongzhuanye', "`shiyongzhuanye` varchar(200) NOT NULL DEFAULT '' COMMENT '适用专业' AFTER `jiaocaibanben`")
    ensure_column_exists('ershoushuji', 'shiyongkecheng', "`shiyongkecheng` varchar(200) NOT NULL DEFAULT '' COMMENT '适用课程' AFTER `shiyongzhuanye`")
    ensure_column_exists('ershoushuji', 'xueyuan', "`xueyuan` varchar(200) NOT NULL DEFAULT '' COMMENT '学院' AFTER `shujifenlei`")
    ensure_column_exists('ershoushuji', 'zhuanye', "`zhuanye` varchar(200) NOT NULL DEFAULT '' COMMENT '专业' AFTER `xueyuan`")
    ensure_column_exists('ershoushuji', 'kecheng', "`kecheng` varchar(200) NOT NULL DEFAULT '' COMMENT '课程' AFTER `zhuanye`")
    ensure_column_exists('ershoushuji', 'banben', "`banben` varchar(200) NOT NULL DEFAULT '' COMMENT '版本' AFTER `kecheng`")
    ensure_column_exists('yonghu', 'xueyuan', "`xueyuan` varchar(200) NOT NULL DEFAULT '' COMMENT '学院' AFTER `dianhuahaoma`")
    ensure_column_exists('yonghu', 'zhuanye', "`zhuanye` varchar(200) NOT NULL DEFAULT '' COMMENT '专业' AFTER `xueyuan`")
    ensure_column_exists('yonghu', 'nianji', "`nianji` varchar(200) NOT NULL DEFAULT '' COMMENT '年级' AFTER `zhuanye`")


def seed_data():
    conn = get_connection(database=DB_NAME)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM `users`")
            if cur.fetchone()[0] > 0:
                print('[SKIP] 初始数据已存在，跳过')
                return

            cur.execute("INSERT INTO `users` (`username`, `password`, `role`) VALUES ('admin', 'admin', '管理员')")

            cur.execute(
                "INSERT INTO `yonghu` "
                "(`yonghuzhanghao`, `yonghuxingming`, `mima`, `xingbie`, `dianhuahaoma`, `xueyuan`, `zhuanye`, `nianji`, `money`) "
                "VALUES ('20220001', '张三', '123456', '男', '13800138001', '计算机学院', '软件工程', '2022级', 1000)"
            )
            cur.execute(
                "INSERT INTO `yonghu` "
                "(`yonghuzhanghao`, `yonghuxingming`, `mima`, `xingbie`, `dianhuahaoma`, `xueyuan`, `zhuanye`, `nianji`, `money`) "
                "VALUES ('20220002', '李四', '123456', '女', '13800138002', '文学院', '汉语言文学', '2022级', 500)"
            )

            cur.execute(
                "INSERT INTO `shangjia` (`shangjiazhanghao`, `shangjiaxingming`, `mima`, `xingbie`, `dianhuahaoma`, `money`) "
                "VALUES ('shop1', '书店老板', '123456', '男', '13900139001', 5000)"
            )
            cur.execute(
                "INSERT INTO `shangjia` (`shangjiazhanghao`, `shangjiaxingming`, `mima`, `xingbie`, `dianhuahaoma`, `money`) "
                "VALUES ('shop2', '二手书商', '123456', '女', '13900139002', 3000)"
            )

            for category in ['文学', '计算机', '历史', '哲学', '经济', '教育', '艺术', '科学']:
                cur.execute("INSERT INTO `shujifenlei` (`shujifenlei`) VALUES (%s)", (category,))

            for name, value in [('picture1', 'picture1.jpg'), ('picture2', 'picture2.jpg'), ('picture3', 'picture3.jpg')]:
                cur.execute("INSERT INTO `config` (`name`, `value`) VALUES (%s, %s)", (name, value))

            cur.execute(
                "INSERT INTO `aboutus` (`title`, `subtitle`, `content`) VALUES (%s, %s, %s)",
                ('关于我们', 'ABOUT US', '二手书籍交易平台，致力于为用户提供便捷的二手书籍买卖服务。'),
            )
            cur.execute(
                "INSERT INTO `systemintro` (`title`, `subtitle`, `content`) VALUES (%s, %s, %s)",
                ('系统简介', 'SYSTEM INTRODUCTION', '本系统是一个二手书籍在线交易平台，支持浏览、购买和管理书籍信息。'),
            )
            cur.execute(
                "INSERT INTO `news` (`title`, `introduction`, `picture`, `content`) VALUES (%s, %s, %s, %s)",
                (
                    '欢迎使用二手书籍交易平台',
                    '平台正式上线，欢迎大家使用',
                    'upload/news_picture1.jpg',
                    '<p>欢迎使用二手书籍交易平台，在这里您可以买到物美价廉的二手书籍。</p>',
                ),
            )

        conn.commit()
        print('[OK] 初始数据已插入')
    finally:
        conn.close()


def migrate():
    print('========== 开始数据库迁移 ==========')
    create_database()
    create_tables()
    patch_existing_schema()
    seed_data()
    print('========== 迁移完成 ==========')


if __name__ == '__main__':
    migrate()
