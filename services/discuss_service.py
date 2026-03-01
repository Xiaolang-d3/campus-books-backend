from models import db, Discussershoushuji
from utils import model_to_dict, paginate_query, apply_filters, generate_id


class DiscussService:
    @staticmethod
    def page(params):
        query = Discussershoushuji.query
        query = apply_filters(Discussershoushuji, query, params, like_fields=['nickname', 'content'])
        return paginate_query(Discussershoushuji, query, params)

    @staticmethod
    def list_all(params):
        query = Discussershoushuji.query
        refid = params.get('refid')
        if refid:
            query = query.filter_by(refid=int(refid))
        query = apply_filters(Discussershoushuji, query, params, like_fields=['nickname'])
        return paginate_query(Discussershoushuji, query, params)

    @staticmethod
    def get_by_id(obj_id):
        return model_to_dict(Discussershoushuji.query.get(obj_id))

    @staticmethod
    def save(data):
        data['id'] = generate_id()
        obj = Discussershoushuji(**data)
        db.session.add(obj)
        db.session.commit()

    @staticmethod
    def update(data):
        obj = Discussershoushuji.query.get(data.get('id'))
        if not obj:
            return False, '评论不存在'
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Discussershoushuji.query.filter(Discussershoushuji.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
