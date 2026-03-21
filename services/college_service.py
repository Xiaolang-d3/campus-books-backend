from models import College, db
from utils import model_to_dict, paginate_query, apply_filters


class CollegeService:
    @staticmethod
    def page(params):
        query = College.query
        query = apply_filters(College, query, params, like_fields=['name'])
        return paginate_query(College, query, params)

    @staticmethod
    def list_all(params):
        query = College.query
        query = apply_filters(College, query, params, like_fields=['name'])
        return paginate_query(College, query, params)

    @staticmethod
    def get_by_id(obj_id):
        return model_to_dict(College.query.get(obj_id))

    @staticmethod
    def save(data):
        from utils import generate_id
        data['id'] = generate_id()
        obj = College(**data)
        db.session.add(obj)
        db.session.commit()

    @staticmethod
    def update(data):
        from utils import generate_id
        obj = College.query.get(data.get('id'))
        if not obj:
            return False, '学院不存在'
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        College.query.filter(College.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
