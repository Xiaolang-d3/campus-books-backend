from models import Order, User, db


class WalletService:
    PAID_STATUSES = {'已支付', '已发货', '已完成'}

    @staticmethod
    def get_balance(identity):
        user = WalletService._get_user(identity)
        return {'balance': float(user.balance or 0)}

    @staticmethod
    def get_logs(identity, params):
        user = WalletService._get_user(identity)
        page = max(int(params.get('page', 1)), 1)
        limit = max(int(params.get('limit', 20)), 1)

        orders = Order.query.filter(
            (Order.user_id == user.id) | (Order.seller_id == user.id)
        ).order_by(Order.addtime.desc(), Order.id.desc()).all()

        logs = []
        for order in orders:
            if order.user_id == user.id:
                buyer_log = WalletService._build_buyer_log(order)
                if buyer_log:
                    logs.append(buyer_log)
            if order.seller_id == user.id:
                seller_log = WalletService._build_seller_log(order)
                if seller_log:
                    logs.append(seller_log)

        logs.sort(key=lambda item: (item['addtime'], str(item['id'])), reverse=True)
        total = len(logs)
        start = (page - 1) * limit
        end = start + limit
        return {
            'list': logs[start:end],
            'total': total,
            'pageSize': limit,
            'currPage': page,
        }

    @staticmethod
    def pay(identity, orderid):
        user = WalletService._get_user(identity)
        order = Order.query.filter_by(order_no=orderid, user_id=user.id).first()
        if not order:
            return False, '订单不存在'
        if order.status != '未支付':
            return False, '订单状态不支持支付'

        total = float(order.total_amount or 0)
        if float(user.balance or 0) < total:
            return False, '余额不足，无法支付'

        seller = User.query.get(order.seller_id) if order.seller_id else None
        user.balance = float(user.balance or 0) - total
        if seller:
            seller.balance = float(seller.balance or 0) + total
        order.status = '已支付'
        db.session.commit()
        return True, None

    @staticmethod
    def recharge(identity, amount):
        user = WalletService._get_user(identity)
        amount = float(amount)
        if amount <= 0:
            return False, '充值金额必须大于0'
        if amount > 10000:
            return False, '单次充值金额不能超过10000元'
        user.balance = float(user.balance or 0) + amount
        db.session.commit()
        return True, None

    @staticmethod
    def _get_user(identity):
        if not identity or identity.get('tableName') != 'user':
            raise ValueError('仅校园用户支持钱包功能')
        user = User.query.get(identity['id'])
        if not user:
            raise ValueError('用户不存在')
        return user

    @staticmethod
    def _build_buyer_log(order):
        total = float(order.total_amount or 0)
        if order.status in WalletService.PAID_STATUSES:
            return {
                'id': f'buy-{order.id}',
                'type': '消费',
                'amount': -total,
                'remark': f'购买《{order.book_title or "书籍"}》',
                'orderid': order.order_no,
                'addtime': order.addtime.isoformat(sep=' ', timespec='seconds') if order.addtime else '',
            }
        if order.status == '已退款':
            return {
                'id': f'refund-{order.id}',
                'type': '退款',
                'amount': total,
                'remark': f'订单退款《{order.book_title or "书籍"}》',
                'orderid': order.order_no,
                'addtime': order.addtime.isoformat(sep=' ', timespec='seconds') if order.addtime else '',
            }
        return None

    @staticmethod
    def _build_seller_log(order):
        total = float(order.total_amount or 0)
        if order.status in WalletService.PAID_STATUSES:
            return {
                'id': f'sell-{order.id}',
                'type': '收入',
                'amount': total,
                'remark': f'出售《{order.book_title or "书籍"}》',
                'orderid': order.order_no,
                'addtime': order.addtime.isoformat(sep=' ', timespec='seconds') if order.addtime else '',
            }
        if order.status == '已退款':
            return {
                'id': f'sell-refund-{order.id}',
                'type': '消费',
                'amount': -total,
                'remark': f'退款支出《{order.book_title or "书籍"}》',
                'orderid': order.order_no,
                'addtime': order.addtime.isoformat(sep=' ', timespec='seconds') if order.addtime else '',
            }
        return None
