from datetime import datetime

from sqlalchemy import text

from models import Book, Order, User, db
from utils import apply_filters, generate_id, generate_order_id, model_to_dict


class OrderService:
    @staticmethod
    def _order_to_dict(order):
        """订单字典 + 卖家姓名/学号（前端展示用）"""
        if order is None:
            return None
        data = model_to_dict(order)
        seller = User.query.get(order.seller_id) if order.seller_id else None
        if seller:
            data['seller_name'] = seller.name
            data['seller_student_no'] = seller.student_no
        else:
            data['seller_name'] = ''
            data['seller_student_no'] = ''
        return data

    @staticmethod
    def _orders_to_dict_list(orders):
        if not orders:
            return []
        seller_ids = {o.seller_id for o in orders if o.seller_id}
        sellers = {}
        if seller_ids:
            for u in User.query.filter(User.id.in_(seller_ids)).all():
                sellers[u.id] = u
        out = []
        for o in orders:
            d = model_to_dict(o)
            s = sellers.get(o.seller_id)
            if s:
                d['seller_name'] = s.name
                d['seller_student_no'] = s.student_no
            else:
                d['seller_name'] = ''
                d['seller_student_no'] = ''
            out.append(d)
        return out

    PAID_STATUSES = {'已支付', '已发货', '已完成'}

    @staticmethod
    def page(params, identity=None):
        query = Order.query
        if identity and identity.get('tableName') != 'admin':
            if params.get('viewType') == 'sell':
                query = query.filter_by(seller_id=identity['id'])
            else:
                query = query.filter_by(user_id=identity['id'])

        status = params.get('status')
        if status:
            query = query.filter_by(status=status)

        query = apply_filters(
            Order,
            query,
            params,
            like_fields=['order_no', 'book_title'],
        )
        page_num = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        sort = params.get('sort', 'id')
        order_dir = params.get('order', 'desc')
        if hasattr(Order, sort):
            col = getattr(Order, sort)
            query = query.order_by(col.desc() if order_dir == 'desc' else col.asc())
        pagination = query.paginate(page=page_num, per_page=limit, error_out=False)
        return {
            'list': OrderService._orders_to_dict_list(pagination.items),
            'total': pagination.total,
            'pageSize': limit,
            'currPage': page_num,
        }

    @staticmethod
    def list_all(params):
        query = Order.query
        query = apply_filters(
            Order,
            query,
            params,
            like_fields=['order_no', 'book_title'],
        )
        page_num = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        sort = params.get('sort', 'id')
        order_dir = params.get('order', 'desc')
        if hasattr(Order, sort):
            col = getattr(Order, sort)
            query = query.order_by(col.desc() if order_dir == 'desc' else col.asc())
        pagination = query.paginate(page=page_num, per_page=limit, error_out=False)
        return {
            'list': OrderService._orders_to_dict_list(pagination.items),
            'total': pagination.total,
            'pageSize': limit,
            'currPage': page_num,
        }

    @staticmethod
    def get_by_id(order_id):
        return OrderService._order_to_dict(Order.query.get(order_id))

    @staticmethod
    def save(data, identity=None):
        book_id = data.get('book_id')
        quantity = int(data.get('quantity', 1) or 1)
        book = Book.query.get(book_id) if book_id else None
        if not book:
            raise ValueError('书籍不存在')

        ok, err = OrderService._check_book_available(book, quantity, identity)
        if not ok:
            raise ValueError(err)

        payload = dict(data)
        payload['id'] = generate_id()
        payload['order_no'] = payload.get('order_no') or generate_order_id()
        payload['user_id'] = identity['id'] if identity else payload.get('user_id')
        payload['seller_id'] = book.seller_id
        # 快照字段
        payload['book_title'] = book.title
        payload['book_cover'] = book.cover
        payload['book_isbn'] = book.isbn
        if book.condition:
            payload['condition_name'] = book.condition.name
        payload['status'] = payload.get('status') or '未支付'
        payload['updatetime'] = datetime.now()

        allowed_fields = {column.name for column in Order.__table__.columns}
        payload = {key: value for key, value in payload.items() if key in allowed_fields}

        order = Order(**payload)
        db.session.add(order)

        ok, err = OrderService._lock_stock(book, quantity, payload['status'])
        if not ok:
            db.session.rollback()
            raise ValueError(err)

        db.session.commit()
        return OrderService._order_to_dict(order)

    @staticmethod
    def _check_book_available(book, quantity, identity):
        if identity and book.seller_id == identity['id']:
            return False, '不能购买自己发布的书籍'
        if int(book.stock or 0) < quantity:
            return False, f'库存不足，当前库存：{book.stock or 0}'
        return True, None

    @staticmethod
    def _lock_stock(book, quantity, status):
        if status == '已退款':
            return True, None
        if int(book.stock or 0) < quantity:
            return False, f'库存不足，当前库存：{book.stock or 0}'
        book.stock = int(book.stock or 0) - quantity
        return True, None

    @staticmethod
    def update(data, identity=None):
        order = Order.query.get(data.get('id'))
        if not order:
            return False, '订单不存在'

        new_status = data.get('status')
        old_status = order.status
        if not OrderService._can_update_order(order, identity, new_status):
            return False, '无权修改该订单'

        if new_status and new_status != old_status:
            ok, err = OrderService._apply_status_transition(order, old_status, new_status)
            if not ok:
                db.session.rollback()
                return False, err

        for key, value in data.items():
            if hasattr(order, key):
                setattr(order, key, value)
        db.session.commit()
        return True, None

    @staticmethod
    def _apply_status_transition(order, old_status, new_status):
        if old_status == '未支付' and new_status == '已支付':
            return OrderService._apply_payment(order)

        if new_status == '已退款' and old_status != '已退款':
            ok, err = OrderService._apply_refund(order, old_status)
            if not ok:
                return False, err
            return True, None

        return True, None

    @staticmethod
    def _apply_payment(order):
        buyer = User.query.get(order.user_id)
        if not buyer:
            return False, '买家不存在'

        total = float(order.total_amount or 0)
        if float(buyer.balance or 0) < total:
            return False, '余额不足，无法支付'

        seller = User.query.get(order.seller_id) if order.seller_id else None
        buyer.balance = float(buyer.balance or 0) - total
        if seller:
            seller.balance = float(seller.balance or 0) + total
        return True, None

    @staticmethod
    def _apply_refund(order, old_status):
        book = Book.query.get(order.book_id) if order.book_id else None
        if book:
            book.stock = int(book.stock or 0) + int(order.quantity or 0)

        if old_status in OrderService.PAID_STATUSES:
            total = float(order.total_amount or 0)
            buyer = User.query.get(order.user_id)
            seller = User.query.get(order.seller_id) if order.seller_id else None
            if buyer:
                buyer.balance = float(buyer.balance or 0) + total
            if seller:
                seller.balance = float(seller.balance or 0) - total
        return True, None

    @staticmethod
    def _can_update_order(order, identity, new_status):
        if not identity:
            return True
        if identity.get('tableName') == 'admin':
            return True
        if new_status == '已发货':
            return order.seller_id == identity['id']
        return order.user_id == identity['id']

    @staticmethod
    def delete(ids, identity=None):
        query = Order.query.filter(Order.id.in_(ids))
        if identity and identity.get('tableName') != 'admin':
            query = query.filter(Order.user_id == identity['id'])

        orders = query.all()
        for order in orders:
            if order.status not in ['已完成', '已退款'] and order.book_id and order.quantity:
                book = Book.query.get(order.book_id)
                if book:
                    book.stock = int(book.stock or 0) + int(order.quantity or 0)
            if order.status in OrderService.PAID_STATUSES:
                buyer = User.query.get(order.user_id)
                seller = User.query.get(order.seller_id) if order.seller_id else None
                total = float(order.total_amount or 0)
                if buyer:
                    buyer.balance = float(buyer.balance or 0) + total
                if seller:
                    seller.balance = float(seller.balance or 0) - total

        query.delete(synchronize_session=False)
        db.session.commit()

    @staticmethod
    def value_stat(x_col, y_col):
        sql = text(
            f"SELECT `{x_col}` as name, SUM(`{y_col}`) as value "
            f"FROM `order` WHERE status IN ({OrderService._paid_status_sql()}) GROUP BY `{x_col}`"
        )
        result = db.session.execute(sql)
        return [{'name': str(row[0]) if row[0] else '', 'value': float(row[1] or 0)} for row in result]

    @staticmethod
    def value_time_stat(x_col, y_col, time_stat_type):
        time_format = {'日': '%Y-%m-%d', '月': '%Y-%m', '年': '%Y'}.get(time_stat_type, '%Y-%m-%d')
        sql = text(
            f"SELECT DATE_FORMAT(`{x_col}`, :fmt) as name, SUM(`{y_col}`) as value "
            f"FROM `order` WHERE status IN ({OrderService._paid_status_sql()}) GROUP BY name ORDER BY name"
        )
        result = db.session.execute(sql, {'fmt': time_format})
        return [{'name': str(row[0]) if row[0] else '', 'value': float(row[1] or 0)} for row in result]

    @staticmethod
    def group_stat(column_name):
        sql = text(
            f"SELECT `{column_name}` as name, COUNT(*) as value "
            f"FROM `order` WHERE status IN ({OrderService._paid_status_sql()}) GROUP BY `{column_name}`"
        )
        result = db.session.execute(sql)
        return [{'name': str(row[0]) if row[0] else '', 'value': int(row[1] or 0)} for row in result]

    @staticmethod
    def _paid_status_sql():
        return "', '".join(OrderService.PAID_STATUSES).join(["'", "'"])
