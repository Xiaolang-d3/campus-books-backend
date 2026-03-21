from models import Major, db
from utils import model_to_dict, paginate_query, apply_filters


class MajorService:
    @staticmethod
    def page(params):
        query = Major.query
        query = apply_filters(Major, query, params, like_fields=['name'], eq_fields=['college_id'])
        return paginate_query(Major, query, params)

    @staticmethod
    def list_all(params):
        query = Major.query
        query = apply_filters(Major, query, params, like_fields=['name'], eq_fields=['college_id'])
        return paginate_query(Major, query, params)

    @staticmethod
    def get_by_id(obj_id):
        obj = Major.query.get(obj_id)
        if not obj:
            return None
        d = model_to_dict(obj)
        if obj.college:
            d['college_name'] = obj.college.name
        return d

    @staticmethod
    def save(data):
        from utils import generate_id
        data['id'] = generate_id()
        obj = Major(**data)
        db.session.add(obj)
        db.session.commit()

    @staticmethod
    def update(data):
        obj = Major.query.get(data.get('id'))
        if not obj:
            return False, '专业不存在'
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Major.query.filter(Major.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
