from models import db, Ershoushuji
from utils import model_to_dict, paginate_query, apply_filters, generate_id


class ErshoushujiService:
    @staticmethod
    def _apply_price_filter(query, params):
        pricestart = params.get('pricestart')
        priceend = params.get('priceend')
        if pricestart:
            query = query.filter(Ershoushuji.price >= float(pricestart))
        if priceend:
            query = query.filter(Ershoushuji.price <= float(priceend))
        return query

    @staticmethod
    def page(params, identity=None):
        query = Ershoushuji.query
        if identity and identity.get('tableName') == 'shangjia':
            query = query.filter_by(shangjiazhanghao=identity['username'])
        query = apply_filters(Ershoushuji, query, params,
                              like_fields=['shujibianhao', 'shujimingcheng', 'shujizuozhe'],
                              eq_fields=['shujifenlei', 'xinjiuchengdu', 'shangjiazhanghao'])
        query = ErshoushujiService._apply_price_filter(query, params)
        return paginate_query(Ershoushuji, query, params)

    @staticmethod
    def list_all(params):
        query = Ershoushuji.query
        query = apply_filters(Ershoushuji, query, params,
                              like_fields=['shujibianhao', 'shujimingcheng', 'shujizuozhe'],
                              eq_fields=['shujifenlei', 'xinjiuchengdu'])
        query = ErshoushujiService._apply_price_filter(query, params)
        return paginate_query(Ershoushuji, query, params)

    @staticmethod
    def get_by_id(book_id):
        return model_to_dict(Ershoushuji.query.get(book_id))

    @staticmethod
    def save(data):
        data['id'] = generate_id()
        # 如果没有设置库存，默认为1
        if 'kucun' not in data or data['kucun'] is None:
            data['kucun'] = 1
        book = Ershoushuji(**data)
        db.session.add(book)
        db.session.commit()

    @staticmethod
    def update(data):
        book = Ershoushuji.query.get(data.get('id'))
        if not book:
            return False, '书籍不存在'
        for k, v in data.items():
            if hasattr(book, k):
                setattr(book, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Ershoushuji.query.filter(Ershoushuji.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()

    @staticmethod
    def check_stock(book_id, quantity):
        """检查库存是否充足"""
        book = Ershoushuji.query.get(book_id)
        if not book:
            return False, '书籍不存在'
        if book.kucun < quantity:
            return False, f'库存不足，当前库存：{book.kucun}'
        return True, None

    @staticmethod
    def reduce_stock(book_id, quantity):
        """减少库存"""
        book = Ershoushuji.query.get(book_id)
        if not book:
            return False, '书籍不存在'
        if book.kucun < quantity:
            return False, f'库存不足，当前库存：{book.kucun}'
        book.kucun -= quantity
        db.session.commit()
        return True, None

    @staticmethod
    def increase_stock(book_id, quantity):
        """增加库存（退款时使用）"""
        book = Ershoushuji.query.get(book_id)
        if not book:
            return False, '书籍不存在'
        book.kucun += quantity
        db.session.commit()
        return True, None
