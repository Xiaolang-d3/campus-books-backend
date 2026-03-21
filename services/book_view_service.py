from models import BookView, db
from utils import model_to_dict, paginate_query, apply_filters


class BookViewService:
    @staticmethod
    def record(user_id, book_id):
        from utils import generate_id
        bv = BookView(
            id=generate_id(),
            user_id=user_id,
            book_id=book_id,
        )
        db.session.add(bv)
        db.session.commit()

    @staticmethod
    def list_all(params):
        query = BookView.query
        query = apply_filters(BookView, query, params, eq_fields=['user_id', 'book_id'])
        query = query.order_by(BookView.view_time.desc())
        return paginate_query(BookView, query, params)

    @staticmethod
    def get_by_id(obj_id):
        return model_to_dict(BookView.query.get(obj_id))

    @staticmethod
    def delete(ids):
        BookView.query.filter(BookView.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
