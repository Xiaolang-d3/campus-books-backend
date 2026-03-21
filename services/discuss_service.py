from models import Review, db
from utils import model_to_dict, paginate_query, apply_filters, generate_id


class ReviewService:
    @staticmethod
    def page(params):
        query = Review.query
        query = apply_filters(Review, query, params, like_fields=['content'])
        return paginate_query(Review, query, params)

    @staticmethod
    def list_all(params):
        refid = params.get('book_id') or params.get('refid')
        query = Review.query
        if refid:
            query = query.filter_by(book_id=int(refid))
        query = apply_filters(Review, query, params, like_fields=['content'])
        return paginate_query(Review, query, params)

    @staticmethod
    def get_by_id(obj_id):
        return model_to_dict(Review.query.get(obj_id))

    @staticmethod
    def save(data):
        data['id'] = generate_id()
        obj = Review(**data)
        db.session.add(obj)
        db.session.commit()

    @staticmethod
    def update(data):
        obj = Review.query.get(data.get('id'))
        if not obj:
            return False, '评价不存在'
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Review.query.filter(Review.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
