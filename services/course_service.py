from models import Course, db
from utils import model_to_dict, paginate_query, apply_filters


class CourseService:
    @staticmethod
    def page(params):
        query = Course.query
        query = apply_filters(Course, query, params, like_fields=['name', 'code'], eq_fields=['major_id'])
        return paginate_query(Course, query, params)

    @staticmethod
    def list_all(params):
        query = Course.query
        query = apply_filters(Course, query, params, like_fields=['name', 'code'], eq_fields=['major_id'])
        return paginate_query(Course, query, params)

    @staticmethod
    def get_by_id(obj_id):
        obj = Course.query.get(obj_id)
        if not obj:
            return None
        d = model_to_dict(obj)
        if obj.major:
            d['major_name'] = obj.major.name
            if obj.major.college:
                d['college_name'] = obj.major.college.name
        return d

    @staticmethod
    def save(data):
        from utils import generate_id
        data['id'] = generate_id()
        obj = Course(**data)
        db.session.add(obj)
        db.session.commit()

    @staticmethod
    def update(data):
        obj = Course.query.get(data.get('id'))
        if not obj:
            return False, '课程不存在'
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Course.query.filter(Course.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
