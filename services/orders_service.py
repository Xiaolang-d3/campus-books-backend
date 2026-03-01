from models import db, Orders
from utils import model_to_dict, paginate_query, apply_filters, generate_id, generate_order_id
from sqlalchemy import text
from services.ershoushuji_service import ErshoushujiService


class OrdersService:
    @staticmethod
    def page(params, identity=None):
        query = Orders.query
        if identity and identity.get('role') != '管理员':
            query = query.filter_by(userid=identity['id'])
        status = params.get('status')
        if status:
            query = query.filter_by(status=status)
        query = apply_filters(Orders, query, params, like_fields=['orderid', 'goodname'])
        return paginate_query(Orders, query, params)

    @staticmethod
    def list_all(params):
        query = Orders.query
        query = apply_filters(Orders, query, params, like_fields=['orderid', 'goodname'])
        return paginate_query(Orders, query, params)

    @staticmethod
    def get_by_id(order_id):
        return model_to_dict(Orders.query.get(order_id))

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
        if not data.get('orderid'):
            data['orderid'] = generate_order_id()
        if identity:
            data['userid'] = identity['id']

        # 创建订单
        order = Orders(**data)
        db.session.add(order)

        # 扣减库存（仅在创建订单时扣减）
        if goodid and data.get('status') != '已退款':
            ok, err = ErshoushujiService.reduce_stock(goodid, buynumber)
            if not ok:
                db.session.rollback()
                raise ValueError(err)

        db.session.commit()

    @staticmethod
    def update(data):
        order = Orders.query.get(data.get('id'))
        if not order:
            return False, '订单不存在'

        old_status = order.status
        new_status = data.get('status')

        # 如果订单状态变更为"已退款"，需要恢复库存
        if new_status == '已退款' and old_status != '已退款':
            if order.goodid and order.buynumber:
                ok, err = ErshoushujiService.increase_stock(order.goodid, order.buynumber)
                if not ok:
                    return False, err

        for k, v in data.items():
            if hasattr(order, k):
                setattr(order, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        # 删除订单前，如果订单未完成，需要恢复库存
        orders = Orders.query.filter(Orders.id.in_(ids)).all()
        for order in orders:
            if order.status not in ['已完成', '已退款'] and order.goodid and order.buynumber:
                ErshoushujiService.increase_stock(order.goodid, order.buynumber)

        Orders.query.filter(Orders.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()

    @staticmethod
    def value_stat(x_col, y_col):
        sql = text(f"SELECT `{x_col}` as name, SUM(`{y_col}`) as value FROM orders WHERE status IN ('已支付','已发货','已完成') GROUP BY `{x_col}`")
        result = db.session.execute(sql)
        return [{'name': str(r[0]) if r[0] else '', 'value': float(r[1] or 0)} for r in result]

    @staticmethod
    def value_time_stat(x_col, y_col, time_stat_type):
        time_format = {'日': '%Y-%m-%d', '月': '%Y-%m', '年': '%Y'}.get(time_stat_type, '%Y-%m-%d')
        sql = text(f"SELECT DATE_FORMAT(`{x_col}`, :fmt) as name, SUM(`{y_col}`) as value FROM orders WHERE status IN ('已支付','已发货','已完成') GROUP BY name ORDER BY name")
        result = db.session.execute(sql, {'fmt': time_format})
        return [{'name': str(r[0]) if r[0] else '', 'value': float(r[1] or 0)} for r in result]

    @staticmethod
    def group_stat(column_name):
        sql = text(f"SELECT `{column_name}` as name, COUNT(*) as value FROM orders WHERE status IN ('已支付','已发货','已完成') GROUP BY `{column_name}`")
        result = db.session.execute(sql)
        return [{'name': str(r[0]) if r[0] else '', 'value': int(r[1] or 0)} for r in result]
