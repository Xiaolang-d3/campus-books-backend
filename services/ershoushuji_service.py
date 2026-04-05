from models import Book, User, BookCategory, ConditionLevel, Order, db
from utils import apply_filters, generate_id, model_to_dict, paginate_query


def book_to_dict(book):
    """将书籍对象转换为字典，包含关联表数据"""
    if book is None:
        return None
    d = model_to_dict(book)
    # 附加关联表名称
    if book.category:
        d['category_name'] = book.category.name
    else:
        d['category_name'] = ''
    if book.condition:
        d['condition_name'] = book.condition.name
    else:
        d['condition_name'] = ''
    if book.seller:
        d['seller_name'] = book.seller.name
        d['seller_student_no'] = book.seller.student_no
    else:
        d['seller_name'] = ''
        d['seller_student_no'] = ''
    # 是否有关联订单
    d['has_orders'] = Order.query.filter_by(book_id=book.id).first() is not None
    return d


class BookService:
    REQUIRED_FIELDS = ('title', 'isbn', 'price')

    @staticmethod
    def _apply_price_filter(query, params):
        pricestart = params.get('pricestart')
        priceend = params.get('priceend')
        if pricestart:
            query = query.filter(Book.price >= float(pricestart))
        if priceend:
            query = query.filter(Book.price <= float(priceend))
        return query

    @staticmethod
    def _validate_payload(data):
        field_names = {
            'title': '书籍名称',
            'isbn': 'ISBN',
            'price': '价格',
        }
        for field in BookService.REQUIRED_FIELDS:
            value = data.get(field)
            if value is None or str(value).strip() == '':
                return False, f'{field_names[field]}不能为空'
        return True, None

    @staticmethod
    def _apply_visibility_scope(query, params, identity):
        if not identity or identity.get('tableName') == 'admin':
            return query
        # 支持字符串'1'和数字1
        my_published = params.get('myPublished')
        if my_published == '1' or my_published == 1:
            return query.filter_by(seller_id=identity['id'])
        return query

    @staticmethod
    def page(params, identity=None):
        query = Book.query
        query = BookService._apply_visibility_scope(query, params, identity)
        
        # 如果有卖家姓名搜索，需要 JOIN user 表
        seller_name = params.get('seller_name')
        if seller_name:
            query = query.join(User, Book.seller_id == User.id).filter(
                User.name.like(f'%{seller_name}%')
            )
        
        query = apply_filters(
            Book,
            query,
            params,
            like_fields=['title', 'author', 'isbn', 'publisher'],
            eq_fields=['category_id', 'condition_id', 'status', 'seller_id'],
        )
        query = BookService._apply_price_filter(query, params)
        
        # 使用自定义分页逻辑以包含关联数据
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        sort = params.get('sort', 'id')
        order = params.get('order', 'desc')
        
        if hasattr(Book, sort):
            col = getattr(Book, sort)
            query = query.order_by(col.desc() if order == 'desc' else col.asc())
        
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        return {
            'list': [book_to_dict(item) for item in pagination.items],
            'total': pagination.total,
            'pageSize': limit,
            'currPage': page,
        }

    @staticmethod
    def list_all(params):
        query = Book.query
        query = apply_filters(
            Book,
            query,
            params,
            like_fields=['title', 'author', 'isbn', 'publisher'],
            eq_fields=['category_id', 'condition_id', 'status', 'seller_id'],
        )
        query = BookService._apply_price_filter(query, params)
        
        # 使用自定义分页逻辑以包含关联数据
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        sort = params.get('sort', 'id')
        order = params.get('order', 'desc')
        
        if hasattr(Book, sort):
            col = getattr(Book, sort)
            query = query.order_by(col.desc() if order == 'desc' else col.asc())
        
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        return {
            'list': [book_to_dict(item) for item in pagination.items],
            'total': pagination.total,
            'pageSize': limit,
            'currPage': page,
        }

    @staticmethod
    def get_by_id(book_id):
        book = Book.query.get(book_id)
        return book_to_dict(book)

    @staticmethod
    def _resolve_names_to_ids(payload):
        """将 category_name / condition_name 转换为对应的 category_id / condition_id"""
        cat_name = payload.pop('category_name', None)
        if cat_name and not payload.get('category_id'):
            cat = BookCategory.query.filter_by(name=cat_name).first()
            if cat:
                payload['category_id'] = cat.id

        cond_name = payload.pop('condition_name', None)
        if cond_name and not payload.get('condition_id'):
            cond = ConditionLevel.query.filter_by(name=cond_name).first()
            if cond:
                payload['condition_id'] = cond.id

    @staticmethod
    def save(data, identity=None):
        ok, err = BookService._validate_payload(data)
        if not ok:
            raise ValueError(err)

        payload = dict(data)
        payload['id'] = generate_id()
        if payload.get('stock') is None:
            payload['stock'] = 1

        if identity and identity.get('tableName') == 'user':
            payload['seller_id'] = identity['id']

        # 兼容前端传 category_name / condition_name 的情况
        BookService._resolve_names_to_ids(payload)

        # 过滤掉非 Book 模型的字段，避免 SQLAlchemy 报错
        valid_columns = {c.key for c in Book.__table__.columns}
        payload = {k: v for k, v in payload.items() if k in valid_columns}

        book = Book(**payload)
        db.session.add(book)
        db.session.commit()
        return model_to_dict(book)

    @staticmethod
    def update(data, identity=None):
        book = Book.query.get(data.get('id'))
        if not book:
            return False, '书籍不存在'

        if identity and identity.get('tableName') == 'user' and int(book.seller_id) != int(identity['id']):
            return False, '只能修改自己发布的书籍'

        # update 时只校验传了的必填字段，允许部分更新
        for field in BookService.REQUIRED_FIELDS:
            if field in data:
                value = data.get(field)
                if value is None or str(value).strip() == '':
                    field_name = {'title': '书籍名称', 'isbn': 'ISBN', 'price': '价格'}[field]
                    return False, f'{field_name}不能为空'

        payload = dict(data)
        # 兼容前端传 category_name / condition_name 的情况
        BookService._resolve_names_to_ids(payload)

        valid_columns = {c.key for c in Book.__table__.columns}
        for k, v in payload.items():
            if k in valid_columns:
                setattr(book, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids, identity=None):
        query = Book.query.filter(Book.id.in_(ids))
        if identity and identity.get('tableName') == 'user':
            query = query.filter(Book.seller_id == int(identity['id']))
        try:
            deleted = query.delete(synchronize_session=False)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return 0, '该书籍存在关联订单，无法删除，请先下架'
        return deleted, None

    @staticmethod
    def check_stock(book_id, quantity):
        book = Book.query.get(book_id)
        if not book:
            return False, '书籍不存在'
        if book.stock < quantity:
            return False, f'库存不足，当前库存：{book.stock}'
        return True, None

    @staticmethod
    def reduce_stock(book_id, quantity):
        book = Book.query.get(book_id)
        if not book:
            return False, '书籍不存在'
        if book.stock < quantity:
            return False, f'库存不足，当前库存：{book.stock}'
        book.stock -= quantity
        db.session.commit()
        return True, None

    @staticmethod
    def increase_stock(book_id, quantity):
        book = Book.query.get(book_id)
        if not book:
            return False, '书籍不存在'
        book.stock += quantity
        db.session.commit()
        return True, None
