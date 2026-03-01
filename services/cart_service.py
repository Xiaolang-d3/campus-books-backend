from models import db, Cart
from utils import model_to_dict, paginate_query, apply_filters, generate_id
from services.ershoushuji_service import ErshoushujiService


class CartService:
    @staticmethod
    def page(params, identity=None):
        query = Cart.query
        if identity and identity.get('role') != '管理员':
            query = query.filter_by(userid=identity['id'])
        query = apply_filters(Cart, query, params, like_fields=['goodname'])
        return paginate_query(Cart, query, params)

    @staticmethod
    def list_all(params):
        query = Cart.query
        query = apply_filters(Cart, query, params, like_fields=['goodname'])
        return paginate_query(Cart, query, params)

    @staticmethod
    def get_by_id(cart_id):
        return model_to_dict(Cart.query.get(cart_id))

    @staticmethod
    def save(data, identity=None):
        # 检查库存
        goodid = data.get('goodid')
        buynumber = data.get('buynumber', 1)
        if goodid:
            ok, err = ErshoushujiService.check_stock(goodid, buynumber)
            if not ok:
                raise ValueError(err)

        data['id'] = generate_id()
        if identity:
            data['userid'] = identity['id']
        cart = Cart(**data)
        db.session.add(cart)
        db.session.commit()

    @staticmethod
    def update(data):
        cart = Cart.query.get(data.get('id'))
        if not cart:
            return False, '购物车项不存在'

        # 如果修改了购买数量，需要检查库存
        new_buynumber = data.get('buynumber')
        if new_buynumber and cart.goodid:
            ok, err = ErshoushujiService.check_stock(cart.goodid, new_buynumber)
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
