from models import Admin, db
from utils import model_to_dict, paginate_query, apply_filters


class UsersService:
    @staticmethod
    def get_by_id(user_id):
        return model_to_dict(Admin.query.get(user_id))

    @staticmethod
    def page(params):
        query = Admin.query
        query = apply_filters(Admin, query, params, like_fields=['username'])
        return paginate_query(Admin, query, params)

    @staticmethod
    def save(data):
        if Admin.query.filter_by(username=data.get('username')).first():
            return False, '用户已存在'
        user = Admin(**data)
        db.session.add(user)
        db.session.commit()
        return True, None

    @staticmethod
    def update(data):
        user = Admin.query.get(data.get('id'))
        if not user:
            return False, '管理员不存在'
        for k, v in data.items():
            if hasattr(user, k):
                setattr(user, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Admin.query.filter(Admin.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
