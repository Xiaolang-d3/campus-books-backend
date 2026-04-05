import time
import random


def model_to_dict(obj):
    if obj is None:
        return None
    d = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if hasattr(val, 'isoformat'):
            val = val.isoformat()
        d[col.name] = val
    return d


def paginate_query(model, query, params):
    page = int(params.get('page', 1))
    limit = int(params.get('limit', 10))
    sort = params.get('sort', 'id')
    order = params.get('order', 'desc')
    if hasattr(model, sort):
        col = getattr(model, sort)
        query = query.order_by(col.desc() if order == 'desc' else col.asc())
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    return {
        'list': [model_to_dict(item) for item in pagination.items],
        'total': pagination.total,
        'pageSize': limit,
        'currPage': page,
    }


def apply_filters(model, query, params, like_fields=None, eq_fields=None):
    like_fields = like_fields or []
    eq_fields = eq_fields or []
    for field in like_fields:
        val = params.get(field)
        if val and hasattr(model, field):
            query = query.filter(getattr(model, field).like(f'%{val}%'))
    for field in eq_fields:
        val = params.get(field)
        if val and hasattr(model, field):
            col = getattr(model, field)
            # 如果是整数类型字段，尝试转换值为整数
            if hasattr(col.type, 'python_type') and col.type.python_type == int:
                try:
                    val = int(val)
                except (ValueError, TypeError):
                    pass
            query = query.filter(col == val)
    return query


def generate_id():
    return int(time.time() * 1000) + random.randint(0, 999)


def generate_order_id():
    return str(int(time.time() * 1000)) + str(random.randint(100, 999))
