from models import Ershoushuji, db
from utils import apply_filters, generate_id, model_to_dict, paginate_query


class ErshoushujiService:
    REQUIRED_FIELDS = (
        'shujimingcheng',
        'shujifenlei',
        'xueyuan',
        'zhuanye',
        'kecheng',
        'banben',
        'price',
    )

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
    def _validate_payload(data):
        data = data or {}
        field_names = {
            'shujimingcheng': '书籍名称',
            'shujifenlei': '书籍分类',
            'xueyuan': '学院',
            'zhuanye': '专业',
            'kecheng': '课程',
            'banben': '版本',
            'price': '价格',
        }
        for field in ErshoushujiService.REQUIRED_FIELDS:
            value = data.get(field)
            if value is None or str(value).strip() == '':
                return False, f'{field_names[field]}不能为空'
        return True, None

    @staticmethod
    def page(params, identity=None):
        query = Ershoushuji.query
        if identity and identity.get('tableName') == 'shangjia':
            query = query.filter_by(shangjiazhanghao=identity['username'])
        query = apply_filters(
            Ershoushuji,
            query,
            params,
            like_fields=['shujibianhao', 'shujimingcheng', 'shujizuozhe'],
            eq_fields=['shujifenlei', 'xinjiuchengdu', 'shangjiazhanghao', 'xueyuan', 'zhuanye', 'kecheng', 'banben'],
        )
        query = ErshoushujiService._apply_price_filter(query, params)
        return paginate_query(Ershoushuji, query, params)

    @staticmethod
    def list_all(params):
        query = Ershoushuji.query
        query = apply_filters(
            Ershoushuji,
            query,
            params,
            like_fields=['shujibianhao', 'shujimingcheng', 'shujizuozhe'],
            eq_fields=['shujifenlei', 'xinjiuchengdu', 'xueyuan', 'zhuanye', 'kecheng', 'banben'],
        )
        query = ErshoushujiService._apply_price_filter(query, params)
        return paginate_query(Ershoushuji, query, params)

    @staticmethod
    def get_by_id(book_id):
        return model_to_dict(Ershoushuji.query.get(book_id))

    @staticmethod
    def save(data):
        ok, err = ErshoushujiService._validate_payload(data)
        if not ok:
            raise ValueError(err)

        payload = dict(data)
        payload['id'] = generate_id()
        if 'kucun' not in payload or payload['kucun'] is None:
            payload['kucun'] = 1
        book = Ershoushuji(**payload)
        db.session.add(book)
        db.session.commit()

    @staticmethod
    def update(data):
        book = Ershoushuji.query.get(data.get('id'))
        if not book:
            return False, '书籍不存在'

        ok, err = ErshoushujiService._validate_payload(data)
        if not ok:
            return False, err

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
        book = Ershoushuji.query.get(book_id)
        if not book:
            return False, '书籍不存在'
        if book.kucun < quantity:
            return False, f'库存不足，当前库存：{book.kucun}'
        return True, None

    @staticmethod
    def reduce_stock(book_id, quantity):
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
        book = Ershoushuji.query.get(book_id)
        if not book:
            return False, '书籍不存在'
        book.kucun += quantity
        db.session.commit()
        return True, None
