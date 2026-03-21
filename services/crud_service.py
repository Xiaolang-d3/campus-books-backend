from models import db
from utils import model_to_dict, paginate_query, apply_filters, generate_id


class CrudService:
    def __init__(self, model, like_fields=None, eq_fields=None, not_found_msg='不存在'):
        self.model = model
        self.like_fields = like_fields or []
        self.eq_fields = eq_fields or []
        self.not_found_msg = not_found_msg

    def page(self, params):
        query = self.model.query
        query = apply_filters(self.model, query, params,
                              like_fields=self.like_fields, eq_fields=self.eq_fields)
        return paginate_query(self.model, query, params)

    def list_all(self, params):
        query = self.model.query
        query = apply_filters(self.model, query, params,
                              like_fields=self.like_fields, eq_fields=self.eq_fields)
        return paginate_query(self.model, query, params)

    def option(self):
        objs = self.model.query.all()
        return [model_to_dict(obj) for obj in objs]

    def get_by_id(self, obj_id):
        return model_to_dict(self.model.query.get(obj_id))

    def save(self, data):
        data['id'] = generate_id()
        obj = self.model(**data)
        db.session.add(obj)
        db.session.commit()

    def update(self, data):
        obj = self.model.query.get(data.get('id'))
        if not obj:
            return False, self.not_found_msg
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.session.commit()
        return True, None

    def delete(self, ids):
        self.model.query.filter(self.model.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
