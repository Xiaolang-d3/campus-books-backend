from models import db, Yonghu
from utils import model_to_dict, paginate_query, apply_filters, generate_id


class YonghuService:
    @staticmethod
    def register(data):
        if Yonghu.query.filter_by(yonghuzhanghao=data.get('yonghuzhanghao')).first():
            return False, '注册用户已存在'
        data['id'] = int(__import__('time').time() * 1000)
        user = Yonghu(**data)
        db.session.add(user)
        db.session.commit()
        return True, None

    @staticmethod
    def get_by_id(user_id):
        return model_to_dict(Yonghu.query.get(user_id))

    @staticmethod
    def reset_pass(username):
        user = Yonghu.query.filter_by(yonghuzhanghao=username).first()
        if not user:
            return False, '账号不存在'
        user.mima = '123456'
        db.session.commit()
        return True, None

    @staticmethod
    def page(params):
        query = Yonghu.query
        query = apply_filters(Yonghu, query, params,
                              like_fields=['yonghuzhanghao', 'yonghuxingming'],
                              eq_fields=['xingbie'])
        return paginate_query(Yonghu, query, params)

    @staticmethod
    def list_all(params):
        query = Yonghu.query
        query = apply_filters(Yonghu, query, params,
                              like_fields=['yonghuzhanghao', 'yonghuxingming'])
        return paginate_query(Yonghu, query, params)

    @staticmethod
    def save(data):
        if Yonghu.query.filter_by(yonghuzhanghao=data.get('yonghuzhanghao')).first():
            return False, '用户已存在'
        data['id'] = generate_id()
        user = Yonghu(**data)
        db.session.add(user)
        db.session.commit()
        return True, None

    @staticmethod
    def update(data):
        user = Yonghu.query.get(data.get('id'))
        if not user:
            return False, '用户不存在'
        for k, v in data.items():
            if hasattr(user, k):
                setattr(user, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Yonghu.query.filter(Yonghu.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
