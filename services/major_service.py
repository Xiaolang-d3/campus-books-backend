from models import Major, db
from utils import model_to_dict, paginate_query, apply_filters


def major_to_dict(major):
    """将专业对象转换为字典，包含学院名称"""
    if major is None:
        return None
    d = model_to_dict(major)
    if major.college:
        d['college_name'] = major.college.name
    else:
        d['college_name'] = ''
    return d


class MajorService:
    @staticmethod
    def page(params):
        query = Major.query
        query = apply_filters(Major, query, params, like_fields=['name'], eq_fields=['college_id'])
        
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        sort = params.get('sort', 'id')
        order = params.get('order', 'desc')
        
        if hasattr(Major, sort):
            col = getattr(Major, sort)
            query = query.order_by(col.desc() if order == 'desc' else col.asc())
        
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        return {
            'list': [major_to_dict(item) for item in pagination.items],
            'total': pagination.total,
            'pageSize': limit,
            'currPage': page,
        }

    @staticmethod
    def list_all(params):
        query = Major.query
        query = apply_filters(Major, query, params, like_fields=['name'], eq_fields=['college_id'])
        
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        sort = params.get('sort', 'id')
        order = params.get('order', 'desc')
        
        if hasattr(Major, sort):
            col = getattr(Major, sort)
            query = query.order_by(col.desc() if order == 'desc' else col.asc())
        
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        return {
            'list': [major_to_dict(item) for item in pagination.items],
            'total': pagination.total,
            'pageSize': limit,
            'currPage': page,
        }

    @staticmethod
    def get_by_id(obj_id):
        return major_to_dict(Major.query.get(obj_id))

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
