from models import Favorite, BookView, Book, db
from utils import model_to_dict, paginate_query, apply_filters, generate_id


class FavoriteService:
    @staticmethod
    def page(params, identity=None):
        query = Favorite.query
        if identity and identity.get('role') != '管理员':
            query = query.filter_by(user_id=identity['id'])
        query = apply_filters(Favorite, query, params, eq_fields=['user_id', 'book_id'])
        return paginate_query(Favorite, query, params)

    @staticmethod
    def list_all(params):
        query = Favorite.query
        query = apply_filters(Favorite, query, params, eq_fields=['user_id', 'book_id'])
        return paginate_query(Favorite, query, params)

    @staticmethod
    def get_by_id(obj_id):
        fav = Favorite.query.get(obj_id)
        if not fav:
            return None
        d = model_to_dict(fav)
        if fav.book_id:
            book = Book.query.get(fav.book_id)
            if book:
                d['book_title'] = book.title
                d['book_cover'] = book.cover
                d['book_price'] = book.price
        return d

    @staticmethod
    def save(data):
        data['id'] = generate_id()
        obj = Favorite(**data)
        db.session.add(obj)
        db.session.commit()

    @staticmethod
    def delete(ids):
        Favorite.query.filter(Favorite.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
