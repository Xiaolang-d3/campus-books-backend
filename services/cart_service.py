from models import Cart, Book, User, db
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
    def _enrich_book_info(cart_dict, book):
        """为购物车项补充书籍信息"""
        if book:
            cart_dict['book_title'] = book.title
            cart_dict['book_cover'] = book.cover
            cart_dict['book_price'] = book.price
            cart_dict['book_stock'] = book.stock
        return cart_dict

    @staticmethod
    def page(params, identity=None):
        query = Cart.query
        if identity and identity.get('role') != '管理员':
            query = query.filter_by(user_id=identity['id'])
        query = apply_filters(Cart, query, params)
        result = paginate_query(Cart, query, params)
        # 补充书籍信息
        for item in result.get('list', []):
            if item.get('book_id'):
                book = Book.query.get(item['book_id'])
                CartService._enrich_book_info(item, book)
        return result

    @staticmethod
    def list_all(params, identity=None):
        query = Cart.query
        if identity and identity.get('role') != '管理员':
            query = query.filter_by(user_id=identity['id'])
        query = apply_filters(Cart, query, params)
        result = paginate_query(Cart, query, params)
        # 补充书籍信息
        for item in result.get('list', []):
            if item.get('book_id'):
                book = Book.query.get(item['book_id'])
                CartService._enrich_book_info(item, book)
        return result

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
        quantity = int(data.get('quantity', 1) or 1)
        if quantity <= 0:
            raise ValueError('购买数量必须大于 0')

        if book_id:
            ok, err = CartService._check_stock(book_id, quantity)
            if not ok:
                raise ValueError(err)

        user_id = identity['id'] if identity else data.get('user_id') or data.get('userid')
        if not user_id:
            raise ValueError('用户未登录或用户信息缺失')

        user = User.query.get(user_id)
        if not user:
            raise ValueError('当前登录用户不存在，请重新登录后再试')

        # 已存在购物车项时直接累加数量
        exists = Cart.query.filter_by(user_id=user_id, book_id=book_id).first()
        if exists:
            new_quantity = exists.quantity + quantity
            ok, err = CartService._check_stock(book_id, new_quantity)
            if not ok:
                raise ValueError(err)
            exists.quantity = new_quantity
            db.session.commit()
            return

        cart_data = {
            'id': generate_id(),
            'user_id': user_id,
            'book_id': book_id,
            'quantity': quantity,
        }
        cart = Cart(**cart_data)
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
