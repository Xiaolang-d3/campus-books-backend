from models import db, Shangjia
from utils import model_to_dict, paginate_query, apply_filters, generate_id


class ShangjiaService:
    @staticmethod
    def register(data):
        if Shangjia.query.filter_by(shangjiazhanghao=data.get('shangjiazhanghao')).first():
            return False, '注册用户已存在'
        data['id'] = int(__import__('time').time() * 1000)
        merchant = Shangjia(**data)
        db.session.add(merchant)
        db.session.commit()
        return True, None

    @staticmethod
    def get_by_id(user_id):
        return model_to_dict(Shangjia.query.get(user_id))

    @staticmethod
    def reset_pass(username):
        user = Shangjia.query.filter_by(shangjiazhanghao=username).first()
        if not user:
            return False, '账号不存在'
        user.mima = '123456'
        db.session.commit()
        return True, None

    @staticmethod
    def page(params):
        query = Shangjia.query
        query = apply_filters(Shangjia, query, params,
                              like_fields=['shangjiazhanghao', 'shangjiaxingming'],
                              eq_fields=['xingbie'])
        return paginate_query(Shangjia, query, params)

    @staticmethod
    def list_all(params):
        query = Shangjia.query
        query = apply_filters(Shangjia, query, params,
                              like_fields=['shangjiazhanghao', 'shangjiaxingming'])
        return paginate_query(Shangjia, query, params)

    @staticmethod
    def save(data):
        if Shangjia.query.filter_by(shangjiazhanghao=data.get('shangjiazhanghao')).first():
            return False, '用户已存在'
        data['id'] = generate_id()
        merchant = Shangjia(**data)
        db.session.add(merchant)
        db.session.commit()
        return True, None

    @staticmethod
    def update(data):
        merchant = Shangjia.query.get(data.get('id'))
        if not merchant:
            return False, '商家不存在'
        for k, v in data.items():
            if hasattr(merchant, k):
                setattr(merchant, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Shangjia.query.filter(Shangjia.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
