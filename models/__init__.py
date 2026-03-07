from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), default='管理员')
    addtime = db.Column(db.DateTime, default=datetime.now)


class Yonghu(db.Model):
    __tablename__ = 'yonghu'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    yonghuzhanghao = db.Column(db.String(200), nullable=False, unique=True, comment='学号')
    yonghuxingming = db.Column(db.String(200), nullable=False, comment='姓名')
    mima = db.Column(db.String(200), nullable=False, comment='密码')
    xingbie = db.Column(db.String(200), comment='性别')
    touxiang = db.Column(db.Text, comment='头像')
    dianhuahaoma = db.Column(db.String(200), comment='电话号码')
    xueyuan = db.Column(db.String(200), nullable=False, default='', comment='学院')
    zhuanye = db.Column(db.String(200), nullable=False, default='', comment='专业')
    nianji = db.Column(db.String(200), nullable=False, default='', comment='年级')
    money = db.Column(db.Float, default=0, comment='余额')


class Shujifenlei(db.Model):
    __tablename__ = 'shujifenlei'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    shujifenlei = db.Column(db.String(200), nullable=False, comment='书籍分类')


class Ershoushuji(db.Model):
    __tablename__ = 'ershoushuji'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    shujibianhao = db.Column(db.String(200), unique=True, comment='书籍编号')
    shujimingcheng = db.Column(db.String(200), comment='书籍名称')
    shujifengmian = db.Column(db.Text, comment='书籍封面')
    shujizuozhe = db.Column(db.String(200), comment='书籍作者')
    isbn = db.Column(db.String(50), nullable=False, default='', comment='ISBN')
    kechengbianhao = db.Column(db.String(100), nullable=False, default='', comment='课程编号')
    jiaocaibanben = db.Column(db.String(200), nullable=False, default='', comment='教材版本')
    shiyongzhuanye = db.Column(db.String(200), nullable=False, default='', comment='适用专业')
    shiyongkecheng = db.Column(db.String(200), nullable=False, default='', comment='适用课程')
    shujifenlei = db.Column(db.String(200), comment='书籍分类')
    xueyuan = db.Column(db.String(200), nullable=False, default='', comment='学院')
    zhuanye = db.Column(db.String(200), nullable=False, default='', comment='专业')
    kecheng = db.Column(db.String(200), nullable=False, default='', comment='课程')
    banben = db.Column(db.String(200), nullable=False, default='', comment='版本')
    shujijianjie = db.Column(db.Text, comment='书籍简介')
    xinjiuchengdu = db.Column(db.String(200), comment='新旧程度')
    chubanshe = db.Column(db.String(200), comment='出版社')
    shangjiariqi = db.Column(db.Date, comment='上架日期')
    faburenid = db.Column(db.BigInteger, nullable=False, default=0, comment='发布人ID')
    faburenzhanghao = db.Column(db.String(200), nullable=False, default='', comment='发布人账号')
    faburenxingming = db.Column(db.String(200), nullable=False, default='', comment='发布人姓名')
    price = db.Column(db.Float, nullable=False, comment='价格')
    kucun = db.Column(db.Integer, default=1, comment='库存数量')


class Orders(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    orderid = db.Column(db.String(200), nullable=False, unique=True, comment='订单编号')
    tablename = db.Column(db.String(200), default='ershoushuji', comment='商品表名')
    userid = db.Column(db.BigInteger, nullable=False, comment='买家ID')
    sellerid = db.Column(db.BigInteger, nullable=False, default=0, comment='卖家ID')
    sellerzhanghao = db.Column(db.String(200), nullable=False, default='', comment='卖家账号')
    sellerxingming = db.Column(db.String(200), nullable=False, default='', comment='卖家姓名')
    goodid = db.Column(db.BigInteger, nullable=False, comment='商品ID')
    goodname = db.Column(db.String(200), comment='商品名称')
    picture = db.Column(db.Text, comment='商品图片')
    buynumber = db.Column(db.Integer, nullable=False, comment='购买数量')
    price = db.Column(db.Float, nullable=False, default=0, comment='价格')
    discountprice = db.Column(db.Float, default=0, comment='折扣价格')
    total = db.Column(db.Float, nullable=False, default=0, comment='总价格')
    discounttotal = db.Column(db.Float, default=0, comment='折扣总价格')
    type = db.Column(db.Integer, default=1, comment='支付类型')
    status = db.Column(db.String(200), comment='状态')
    address = db.Column(db.String(200), comment='地址')
    tel = db.Column(db.String(200), comment='电话')
    consignee = db.Column(db.String(200), comment='收货人')
    remark = db.Column(db.String(200), comment='备注')
    logistics = db.Column(db.Text, comment='物流')


class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    tablename = db.Column(db.String(200), default='ershoushuji', comment='商品表名')
    userid = db.Column(db.BigInteger, nullable=False, comment='用户ID')
    goodid = db.Column(db.BigInteger, nullable=False, comment='商品ID')
    goodname = db.Column(db.String(200), comment='商品名称')
    picture = db.Column(db.Text, comment='图片')
    buynumber = db.Column(db.Integer, nullable=False, comment='购买数量')
    price = db.Column(db.Float, comment='单价')
    discountprice = db.Column(db.Float, comment='会员价')


class Address(db.Model):
    __tablename__ = 'address'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    userid = db.Column(db.BigInteger, nullable=False, comment='用户ID')
    address = db.Column(db.String(200), nullable=False, comment='地址')
    name = db.Column(db.String(200), nullable=False, comment='收货人')
    phone = db.Column(db.String(200), nullable=False, comment='电话')
    isdefault = db.Column(db.String(200), nullable=False, comment='是否默认地址')


class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    title = db.Column(db.String(200), nullable=False, comment='标题')
    introduction = db.Column(db.Text, comment='简介')
    picture = db.Column(db.Text, nullable=False, comment='图片')
    content = db.Column(db.Text, nullable=False, comment='内容')


class Aboutus(db.Model):
    __tablename__ = 'aboutus'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    picture1 = db.Column(db.Text)
    picture2 = db.Column(db.Text)
    picture3 = db.Column(db.Text)


class Systemintro(db.Model):
    __tablename__ = 'systemintro'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    picture1 = db.Column(db.Text)
    picture2 = db.Column(db.Text)
    picture3 = db.Column(db.Text)


class Discussershoushuji(db.Model):
    __tablename__ = 'discussershoushuji'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    refid = db.Column(db.BigInteger, nullable=False, comment='关联表ID')
    userid = db.Column(db.BigInteger, nullable=False, comment='用户ID')
    avatarurl = db.Column(db.Text, comment='头像')
    nickname = db.Column(db.String(200), comment='用户昵称')
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    reply = db.Column(db.Text, comment='回复内容')


class Storeup(db.Model):
    __tablename__ = 'storeup'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    userid = db.Column(db.BigInteger, nullable=False, comment='用户ID')
    refid = db.Column(db.BigInteger, comment='商品ID')
    tablename = db.Column(db.String(200), comment='表名')
    name = db.Column(db.String(200), nullable=False, comment='名称')
    picture = db.Column(db.Text, nullable=False, comment='图片')
    type = db.Column(db.String(200), default='1', comment='类型')
    inteltype = db.Column(db.String(200), comment='推荐类型')
    remark = db.Column(db.String(200), comment='备注')


class ConfigModel(db.Model):
    __tablename__ = 'config'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='配置参数名称')
    value = db.Column(db.String(100), comment='配置参数值')
