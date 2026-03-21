from models import Cart, Book, db
from utils import model_to_dict, paginate_query, apply_filters, generate_id


class CartService:
    @staticmethod
    def _check_stock(book_id, quantity):
        book = Book.query.get(book_id)
        if not book:
            return False, '书籍不存在'
        if book.stock < quantity:
            return False, f'库存不足，当前库存：{book.stock}'
        return True, None

    @staticmethod
    def page(params, identity=None):
        query = Cart.query
        if identity and identity.get('role') != '管理员':
            query = query.filter_by(user_id=identity['id'])
        query = apply_filters(Cart, query, params)
        return paginate_query(Cart, query, params)

    @staticmethod
    def list_all(params, identity=None):
        query = Cart.query
        if identity and identity.get('role') != '管理员':
            query = query.filter_by(user_id=identity['id'])
        query = apply_filters(Cart, query, params)
        return paginate_query(Cart, query, params)

    @staticmethod
    def get_by_id(cart_id):
        cart = Cart.query.get(cart_id)
        if not cart:
            return None
        d = model_to_dict(cart)
        if cart.book_id:
            book = Book.query.get(cart.book_id)
            if book:
                d['book_title'] = book.title
                d['book_cover'] = book.cover
                d['book_price'] = book.price
                d['book_stock'] = book.stock
        return d

    @staticmethod
    def save(data, identity=None):
        book_id = data.get('book_id')
        quantity = data.get('quantity', 1)
        if book_id:
            ok, err = CartService._check_stock(book_id, quantity)
            if not ok:
                raise ValueError(err)

        data['id'] = generate_id()
        if identity:
            data['user_id'] = identity['id']
        cart = Cart(**data)
        db.session.add(cart)
        db.session.commit()

    @staticmethod
    def update(data):
        cart = Cart.query.get(data.get('id'))
        if not cart:
            return False, '购物车项不存在'

        new_quantity = data.get('quantity')
        if new_quantity and cart.book_id:
            ok, err = CartService._check_stock(cart.book_id, new_quantity)
            if not ok:
                return False, err

        for k, v in data.items():
            if hasattr(cart, k):
                setattr(cart, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Cart.query.filter(Cart.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
