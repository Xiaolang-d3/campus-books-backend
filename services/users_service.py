from models import db, Users
from utils import model_to_dict, paginate_query, apply_filters


class UsersService:
    @staticmethod
    def get_by_id(user_id):
        return model_to_dict(Users.query.get(user_id))

    @staticmethod
    def page(params):
        query = Users.query
        query = apply_filters(Users, query, params, like_fields=['username'])
        return paginate_query(Users, query, params)

    @staticmethod
    def save(data):
        if Users.query.filter_by(username=data.get('username')).first():
            return False, '用户已存在'
        user = Users(**data)
        db.session.add(user)
        db.session.commit()
        return True, None

    @staticmethod
    def update(data):
        user = Users.query.get(data.get('id'))
        if not user:
            return False, '用户不存在'
        for k, v in data.items():
            if hasattr(user, k):
                setattr(user, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Users.query.filter(Users.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
