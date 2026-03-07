from models import Ershoushuji, Yonghu, db
from utils import apply_filters, generate_id, model_to_dict, paginate_query


class ErshoushujiService:
    REQUIRED_FIELDS = (
        'shujimingcheng',
        'isbn',
        'kechengbianhao',
        'jiaocaibanben',
        'shiyongzhuanye',
        'shiyongkecheng',
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
        field_names = {
            'shujimingcheng': '书籍名称',
            'isbn': 'ISBN',
            'kechengbianhao': '课程编号',
            'jiaocaibanben': '教材版本',
            'shiyongzhuanye': '适用专业',
            'shiyongkecheng': '适用课程',
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
    def _apply_visibility_scope(query, params, identity):
        if not identity or identity.get('tableName') == 'users':
            return query
        if params.get('myPublished') == '1':
            return query.filter_by(faburenid=identity['id'])
        return query

    @staticmethod
    def page(params, identity=None):
        query = Ershoushuji.query
        query = ErshoushujiService._apply_visibility_scope(query, params, identity)
        query = apply_filters(
            Ershoushuji,
            query,
            params,
            like_fields=[
                'shujibianhao',
                'shujimingcheng',
                'shujizuozhe',
                'isbn',
                'kechengbianhao',
                'jiaocaibanben',
                'shiyongzhuanye',
                'shiyongkecheng',
            ],
            eq_fields=['shujifenlei', 'xinjiuchengdu', 'xueyuan', 'zhuanye', 'kecheng', 'banben', 'faburenid'],
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
            like_fields=[
                'shujibianhao',
                'shujimingcheng',
                'shujizuozhe',
                'isbn',
                'kechengbianhao',
                'jiaocaibanben',
                'shiyongzhuanye',
                'shiyongkecheng',
            ],
            eq_fields=['shujifenlei', 'xinjiuchengdu', 'xueyuan', 'zhuanye', 'kecheng', 'banben'],
        )
        query = ErshoushujiService._apply_price_filter(query, params)
        return paginate_query(Ershoushuji, query, params)

    @staticmethod
    def get_by_id(book_id):
        return model_to_dict(Ershoushuji.query.get(book_id))

    @staticmethod
    def save(data, identity=None):
        ok, err = ErshoushujiService._validate_payload(data)
        if not ok:
            raise ValueError(err)

        payload = dict(data)
        payload['id'] = generate_id()
        if payload.get('kucun') is None:
            payload['kucun'] = 1

        if identity and identity.get('tableName') == 'yonghu':
            user = Yonghu.query.get(identity['id'])
            payload['faburenid'] = user.id
            payload['faburenzhanghao'] = user.yonghuzhanghao
            payload['faburenxingming'] = user.yonghuxingming

        book = Ershoushuji(**payload)
        db.session.add(book)
        db.session.commit()
        return model_to_dict(book)

    @staticmethod
    def update(data, identity=None):
        book = Ershoushuji.query.get(data.get('id'))
        if not book:
            return False, '书籍不存在'

        if identity and identity.get('tableName') == 'yonghu' and book.faburenid != identity['id']:
            return False, '只能修改自己发布的书籍'

        ok, err = ErshoushujiService._validate_payload(data)
        if not ok:
            return False, err

        for k, v in data.items():
            if hasattr(book, k):
                setattr(book, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids, identity=None):
        query = Ershoushuji.query.filter(Ershoushuji.id.in_(ids))
        if identity and identity.get('tableName') == 'yonghu':
            query = query.filter_by(faburenid=identity['id'])
        query.delete(synchronize_session=False)
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
