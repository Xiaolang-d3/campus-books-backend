from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# =====================================================================
# 管理员
# =====================================================================
class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='管理员')
    addtime = db.Column(db.DateTime, default=datetime.now)


# =====================================================================
# 字典表
# =====================================================================
class College(db.Model):
    __tablename__ = 'college'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    addtime = db.Column(db.DateTime, default=datetime.now)

    majors = db.relationship('Major', backref='college', lazy=True)


class Major(db.Model):
    __tablename__ = 'major'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    college_id = db.Column(db.BigInteger, db.ForeignKey('college.id', ondelete='SET NULL'))
    year = db.Column(db.Integer)
    addtime = db.Column(db.DateTime, default=datetime.now)

    courses = db.relationship('Course', backref='major', lazy=True)


class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)
    major_id = db.Column(db.BigInteger, db.ForeignKey('major.id', ondelete='SET NULL'))
    addtime = db.Column(db.DateTime, default=datetime.now)


class BookCategory(db.Model):
    __tablename__ = 'book_category'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    icon = db.Column(db.String(50))
    sort = db.Column(db.Integer, default=0)
    addtime = db.Column(db.DateTime, default=datetime.now)


class ConditionLevel(db.Model):
    __tablename__ = 'condition_level'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


# =====================================================================
# 用户表
# =====================================================================
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    student_no = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    avatar = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    college_id = db.Column(db.BigInteger, db.ForeignKey('college.id', ondelete='SET NULL'))
    major_id = db.Column(db.BigInteger, db.ForeignKey('major.id', ondelete='SET NULL'))
    grade = db.Column(db.String(20))
    balance = db.Column(db.Numeric(10, 2), default=0)
    addtime = db.Column(db.DateTime, default=datetime.now)

    college = db.relationship('College', backref='users')
    major = db.relationship('Major', backref='users')


# =====================================================================
# 书籍表
# =====================================================================
class Book(db.Model):
    __tablename__ = 'book'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200))
    cover = db.Column(db.String(255))
    publisher = db.Column(db.String(200))
    description = db.Column(db.Text)
    category_id = db.Column(db.BigInteger, db.ForeignKey('book_category.id', ondelete='SET NULL'))
    condition_id = db.Column(db.Integer, db.ForeignKey('condition_level.id', ondelete='SET NULL'))
    seller_id = db.Column(db.BigInteger, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    original_price = db.Column(db.Numeric(10, 2))
    stock = db.Column(db.Integer, default=1)
    status = db.Column(db.SmallInteger, default=1)
    addtime = db.Column(db.DateTime, default=datetime.now)
    updatetime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    category = db.relationship('BookCategory', backref='books')
    condition = db.relationship('ConditionLevel', backref='books')
    seller = db.relationship('User', foreign_keys=[seller_id])


# =====================================================================
# 收货地址表
# =====================================================================
class Address(db.Model):
    __tablename__ = 'address'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    contact_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))
    detail = db.Column(db.String(255), nullable=False)
    is_default = db.Column(db.SmallInteger, default=0)
    addtime = db.Column(db.DateTime, default=datetime.now)


# =====================================================================
# 订单表
# =====================================================================
class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(50), nullable=False, unique=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    book_id = db.Column(db.BigInteger, nullable=False)
    seller_id = db.Column(db.BigInteger, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    # 快照字段
    book_title = db.Column(db.String(200))
    book_cover = db.Column(db.String(255))
    book_isbn = db.Column(db.String(50))
    condition_name = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50))
    pay_type = db.Column(db.Integer)
    address_id = db.Column(db.BigInteger)
    receiver_name = db.Column(db.String(50))
    receiver_phone = db.Column(db.String(20))
    receiver_address = db.Column(db.String(255))
    remark = db.Column(db.String(255))
    logistics = db.Column(db.Text)
    addtime = db.Column(db.DateTime, default=datetime.now)
    updatetime = db.Column(db.DateTime)


# =====================================================================
# 购物车表
# =====================================================================
class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    book_id = db.Column(db.BigInteger, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    addtime = db.Column(db.DateTime, default=datetime.now)


# =====================================================================
# AI 推荐表
# =====================================================================
class BookView(db.Model):
    __tablename__ = 'book_view'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    book_id = db.Column(db.BigInteger, nullable=False)
    view_time = db.Column(db.DateTime, default=datetime.now)


class Favorite(db.Model):
    __tablename__ = 'favorite'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    book_id = db.Column(db.BigInteger, nullable=False)
    addtime = db.Column(db.DateTime, default=datetime.now)


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    book_id = db.Column(db.BigInteger, nullable=False)
    order_id = db.Column(db.BigInteger)
    rating = db.Column(db.SmallInteger, nullable=False)
    content = db.Column(db.Text)
    reply = db.Column(db.Text)
    addtime = db.Column(db.DateTime, default=datetime.now)


# =====================================================================
# 内容表
# =====================================================================
class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    title = db.Column(db.String(200), nullable=False)
    introduction = db.Column(db.Text)
    picture = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)


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


class ConfigModel(db.Model):
    __tablename__ = 'config'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100))
