from models import db, Storeup
from utils import model_to_dict, paginate_query, apply_filters, generate_id


class StoreupService:
    @staticmethod
    def page(params, identity=None):
        query = Storeup.query
        if identity and identity.get('role') != '管理员':
            query = query.filter_by(userid=identity['id'])
        query = apply_filters(Storeup, query, params, like_fields=['name'], eq_fields=['type', 'tablename'])
        return paginate_query(Storeup, query, params)

    @staticmethod
    def list_all(params):
        query = Storeup.query
        query = apply_filters(Storeup, query, params, like_fields=['name'], eq_fields=['type', 'userid', 'tablename', 'refid'])
        return paginate_query(Storeup, query, params)

    @staticmethod
    def get_by_id(obj_id):
        return model_to_dict(Storeup.query.get(obj_id))

    @staticmethod
    def save(data):
        data['id'] = generate_id()
        obj = Storeup(**data)
        db.session.add(obj)
        db.session.commit()

    @staticmethod
    def update(data):
        obj = Storeup.query.get(data.get('id'))
        if not obj:
            return False, '收藏不存在'
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Storeup.query.filter(Storeup.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
