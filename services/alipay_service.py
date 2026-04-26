import base64
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlencode

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from flask import current_app

from models import Order, User, WalletRecharge, db
from services.orders_service import OrderService
from utils import generate_order_id


class AlipayService:
    TRADE_SUCCESS_STATUSES = {'TRADE_SUCCESS', 'TRADE_FINISHED'}
    WAITING_STATUS = 'WAIT_BUYER_PAY'
    RECHARGE_PAID_STATUS = '已支付'
    RECHARGE_PENDING_STATUS = '待支付'

    @staticmethod
    def create_page_pay(order_id, identity):
        if not identity or identity.get('tableName') != 'user':
            raise ValueError('仅校园用户支持支付宝支付')

        order = Order.query.filter_by(id=order_id, user_id=identity['id']).first()
        if not order:
            raise ValueError('订单不存在')
        if order.status != '未支付':
            raise ValueError('订单状态不支持支付')

        config = AlipayService._config()
        AlipayService._ensure_ready(config)

        biz_content = {
            'out_trade_no': order.order_no,
            'total_amount': AlipayService._format_amount(order.total_amount),
            'subject': f'校园二手书订单-{order.book_title or order.order_no}',
            'product_code': 'FAST_INSTANT_TRADE_PAY',
            'body': order.book_title or '校园二手书订单',
        }
        if config.get('timeout_express'):
            biz_content['timeout_express'] = config['timeout_express']

        params = {
            'app_id': config['app_id'],
            'method': 'alipay.trade.page.pay',
            'format': 'JSON',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'notify_url': config['notify_url'],
            'return_url': config['return_url'],
            'biz_content': json.dumps(biz_content, ensure_ascii=False, separators=(',', ':')),
        }
        params['sign'] = AlipayService._sign(params, config['app_private_key'])
        return {'payUrl': f"{config['gateway']}?{urlencode(params)}"}

    @staticmethod
    def create_qr_pay(order_id, identity):
        order = AlipayService._get_payable_order(order_id, identity)
        config = AlipayService._config()

        biz_content = {
            'out_trade_no': order.order_no,
            'total_amount': AlipayService._format_amount(order.total_amount),
            'subject': f'校园二手书订单-{order.book_title or order.order_no}',
        }
        if config.get('timeout_express'):
            biz_content['timeout_express'] = config['timeout_express']

        try:
            response = AlipayService._execute('alipay.trade.precreate', biz_content, config)
        except ValueError:
            db.session.rollback()
            raise

        data = response.get('alipay_trade_precreate_response') or {}
        if data.get('code') != '10000':
            raise ValueError(data.get('sub_msg') or data.get('msg') or '支付宝二维码创建失败')

        return {
            'orderId': order.id,
            'orderNo': order.order_no,
            'qrCode': data.get('qr_code'),
            'amount': AlipayService._format_amount(order.total_amount),
        }

    @staticmethod
    def query_payment(order_id, identity):
        if not identity or identity.get('tableName') != 'user':
            raise ValueError('仅校园用户支持支付宝支付')

        order = Order.query.filter_by(id=order_id, user_id=identity['id']).first()
        if not order:
            raise ValueError('订单不存在')
        if order.status != '未支付':
            return {'paid': order.status in OrderService.PAID_STATUSES, 'status': order.status}

        config = AlipayService._config()
        AlipayService._ensure_ready(config, require_return_url=False, require_notify_url=False)
        response = AlipayService._execute('alipay.trade.query', {'out_trade_no': order.order_no}, config)
        data = response.get('alipay_trade_query_response') or {}
        code = data.get('code')
        trade_status = data.get('trade_status')

        if code != '10000':
            sub_code = data.get('sub_code')
            if sub_code == 'ACQ.TRADE_NOT_EXIST':
                return {'paid': False, 'status': 'WAIT_BUYER_PAY', 'message': '等待扫码支付'}
            raise ValueError(data.get('sub_msg') or data.get('msg') or '支付宝交易查询失败')

        if trade_status in AlipayService.TRADE_SUCCESS_STATUSES:
            ok, err = OrderService.mark_paid(order, pay_type=2, deduct_buyer_balance=False)
            if not ok:
                db.session.rollback()
                raise ValueError(err)
            db.session.commit()
            return {'paid': True, 'status': '已支付', 'tradeStatus': trade_status}

        return {'paid': False, 'status': trade_status or AlipayService.WAITING_STATUS}

    @staticmethod
    def create_recharge_qr(amount, identity):
        user = AlipayService._get_user(identity)
        amount = AlipayService._to_decimal(amount)
        if amount <= Decimal('0'):
            raise ValueError('充值金额必须大于 0')
        if amount > Decimal('10000'):
            raise ValueError('单次充值金额不能超过 10000')

        config = AlipayService._config()
        AlipayService._ensure_ready(config, require_return_url=False, require_notify_url=False)

        recharge = WalletRecharge(
            recharge_no=AlipayService._make_recharge_no(),
            user_id=user.id,
            amount=amount,
            status=AlipayService.RECHARGE_PENDING_STATUS,
            pay_type=2,
        )
        db.session.add(recharge)
        db.session.flush()

        if config.get('mock_pay'):
            db.session.commit()
            return {
                'rechargeId': recharge.id,
                'rechargeNo': recharge.recharge_no,
                'qrCode': f'campus-books://mock-alipay/recharge?no={recharge.recharge_no}&amount={AlipayService._format_amount(amount)}',
                'amount': AlipayService._format_amount(amount),
                'mockPay': True,
            }

        AlipayService._ensure_ready(config, require_return_url=False, require_notify_url=False)

        biz_content = {
            'out_trade_no': recharge.recharge_no,
            'total_amount': AlipayService._format_amount(amount),
            'subject': f'校园二手书余额充值-{AlipayService._format_amount(amount)}',
        }
        if config.get('timeout_express'):
            biz_content['timeout_express'] = config['timeout_express']

        response = AlipayService._execute('alipay.trade.precreate', biz_content, config)
        data = response.get('alipay_trade_precreate_response') or {}
        if data.get('code') != '10000':
            db.session.rollback()
            raise ValueError(data.get('sub_msg') or data.get('msg') or '支付宝充值二维码创建失败')

        db.session.commit()
        return {
            'rechargeId': recharge.id,
            'rechargeNo': recharge.recharge_no,
            'qrCode': data.get('qr_code'),
            'amount': AlipayService._format_amount(amount),
            'mockPay': False,
        }

    @staticmethod
    def query_recharge(recharge_id, identity):
        user = AlipayService._get_user(identity)
        recharge = WalletRecharge.query.filter_by(id=recharge_id, user_id=user.id).first()
        if not recharge:
            raise ValueError('充值单不存在')
        if recharge.status == AlipayService.RECHARGE_PAID_STATUS:
            return {
                'paid': True,
                'status': recharge.status,
                'balance': float(user.balance or 0),
            }

        config = AlipayService._config()
        AlipayService._ensure_ready(config, require_return_url=False, require_notify_url=False)
        response = AlipayService._execute('alipay.trade.query', {'out_trade_no': recharge.recharge_no}, config)
        data = response.get('alipay_trade_query_response') or {}
        code = data.get('code')
        trade_status = data.get('trade_status')

        if code != '10000':
            sub_code = data.get('sub_code')
            if sub_code == 'ACQ.TRADE_NOT_EXIST':
                return {'paid': False, 'status': AlipayService.WAITING_STATUS, 'message': '等待扫码支付'}
            raise ValueError(data.get('sub_msg') or data.get('msg') or '查询支付宝充值状态失败')

        if trade_status in AlipayService.TRADE_SUCCESS_STATUSES:
            ok, err = AlipayService._mark_recharge_paid(recharge, data.get('total_amount'))
            if not ok:
                db.session.rollback()
                raise ValueError(err)
            db.session.commit()
            db.session.refresh(user)
            return {
                'paid': True,
                'status': AlipayService.RECHARGE_PAID_STATUS,
                'tradeStatus': trade_status,
                'balance': float(user.balance or 0),
            }

        return {'paid': False, 'status': trade_status or AlipayService.WAITING_STATUS}

    @staticmethod
    def mock_recharge_payment(recharge_id, identity):
        if not AlipayService._config().get('mock_pay'):
            raise ValueError('模拟支付未开启')

        user = AlipayService._get_user(identity)
        recharge = WalletRecharge.query.filter_by(id=recharge_id, user_id=user.id).first()
        if not recharge:
            raise ValueError('充值单不存在')

        ok, err = AlipayService._mark_recharge_paid(recharge, recharge.amount)
        if not ok:
            db.session.rollback()
            raise ValueError(err)

        db.session.commit()
        db.session.refresh(user)
        return {
            'paid': True,
            'status': AlipayService.RECHARGE_PAID_STATUS,
            'balance': float(user.balance or 0),
        }

    @staticmethod
    def _get_payable_order(order_id, identity):
        if not identity or identity.get('tableName') != 'user':
            raise ValueError('仅校园用户支持支付宝支付')

        order = Order.query.filter_by(id=order_id, user_id=identity['id']).first()
        if not order:
            raise ValueError('订单不存在')
        if order.status != '未支付':
            raise ValueError('订单状态不支持支付')
        return order

    @staticmethod
    def _get_user(identity):
        if not identity or identity.get('tableName') != 'user':
            raise ValueError('请先登录用户账号')
        user = User.query.get(identity['id'])
        if not user:
            raise ValueError('用户不存在')
        return user

    @staticmethod
    def handle_notify(data):
        config = AlipayService._config()
        AlipayService._ensure_ready(config, require_return_url=False)

        if data.get('app_id') != config['app_id']:
            return False, 'app_id不匹配'
        if not AlipayService._verify(data, config['alipay_public_key']):
            return False, '支付宝回调验签失败'
        if data.get('trade_status') not in AlipayService.TRADE_SUCCESS_STATUSES:
            return True, None

        order_no = data.get('out_trade_no')
        recharge = WalletRecharge.query.filter_by(recharge_no=order_no).first()
        if recharge:
            ok, err = AlipayService._mark_recharge_paid(recharge, data.get('total_amount'))
            if not ok:
                db.session.rollback()
                return False, err
            db.session.commit()
            return True, None

        order = Order.query.filter_by(order_no=order_no).first()
        if not order:
            return False, '订单不存在'

        paid_amount = AlipayService._to_decimal(data.get('total_amount'))
        order_amount = AlipayService._to_decimal(order.total_amount)
        if paid_amount != order_amount:
            return False, '支付金额与订单金额不一致'

        if order.status == '未支付':
            ok, err = OrderService.mark_paid(order, pay_type=2, deduct_buyer_balance=False)
            if not ok:
                db.session.rollback()
                return False, err
            db.session.commit()
        return True, None

    @staticmethod
    def _mark_recharge_paid(recharge, paid_amount):
        if not recharge:
            return False, '充值单不存在'
        paid_amount = AlipayService._to_decimal(paid_amount)
        recharge_amount = AlipayService._to_decimal(recharge.amount)
        if paid_amount != recharge_amount:
            return False, '支付金额与充值金额不一致'
        if recharge.status == AlipayService.RECHARGE_PAID_STATUS:
            return True, None

        user = User.query.get(recharge.user_id)
        if not user:
            return False, '用户不存在'

        user.balance = AlipayService._to_decimal(user.balance) + recharge_amount
        recharge.status = AlipayService.RECHARGE_PAID_STATUS
        recharge.pay_type = 2
        recharge.updatetime = datetime.now()
        return True, None

    @staticmethod
    def _make_recharge_no():
        for _ in range(5):
            recharge_no = f'RC{generate_order_id()}'
            exists = WalletRecharge.query.filter_by(recharge_no=recharge_no).first()
            if not exists:
                return recharge_no
        raise ValueError('充值单号生成失败，请重试')

    @staticmethod
    def _config():
        return {
            'enabled': current_app.config.get('ALIPAY_ENABLED', False),
            'gateway': current_app.config.get('ALIPAY_GATEWAY', 'https://openapi.alipay.com/gateway.do'),
            'app_id': current_app.config.get('ALIPAY_APP_ID', ''),
            'app_private_key': AlipayService._load_key(
                current_app.config.get('ALIPAY_APP_PRIVATE_KEY', ''),
                current_app.config.get('ALIPAY_APP_PRIVATE_KEY_PATH', ''),
                private=True,
            ),
            'alipay_public_key': AlipayService._load_key(
                current_app.config.get('ALIPAY_PUBLIC_KEY', ''),
                current_app.config.get('ALIPAY_PUBLIC_KEY_PATH', ''),
                private=False,
            ),
            'notify_url': current_app.config.get('ALIPAY_NOTIFY_URL', ''),
            'return_url': current_app.config.get('ALIPAY_RETURN_URL', ''),
            'timeout_express': current_app.config.get('ALIPAY_TIMEOUT_EXPRESS', '30m'),
            'mock_pay': current_app.config.get('ALIPAY_MOCK_PAY', False),
        }

    @staticmethod
    def _ensure_ready(config, require_return_url=True, require_notify_url=True):
        required = ['app_id', 'app_private_key', 'alipay_public_key']
        if require_notify_url:
            required.append('notify_url')
        if require_return_url:
            required.append('return_url')
        if not config.get('enabled'):
            raise ValueError('支付宝支付未启用，请先完善 alipay 配置')
        missing = [key for key in required if not config.get(key)]
        if missing:
            raise ValueError(f'支付宝配置缺失：{", ".join(missing)}')

    @staticmethod
    def _execute(method, biz_content, config):
        params = {
            'app_id': config['app_id'],
            'method': method,
            'format': 'JSON',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'biz_content': json.dumps(biz_content, ensure_ascii=False, separators=(',', ':')),
        }
        if config.get('notify_url'):
            params['notify_url'] = config['notify_url']
        params['sign'] = AlipayService._sign(params, config['app_private_key'])

        try:
            resp = requests.post(config['gateway'], params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise ValueError(f'支付宝接口请求失败：{e}')
        except ValueError:
            raise ValueError('支付宝响应解析失败')

    @staticmethod
    def _load_key(raw_key, key_path, private):
        key = (raw_key or '').strip()
        if not key and key_path:
            path = Path(key_path)
            if path.exists():
                key = path.read_text(encoding='utf-8').strip()
        if not key:
            return ''
        if 'BEGIN ' in key:
            return key

        line_size = 64
        body = '\n'.join(key[i:i + line_size] for i in range(0, len(key), line_size))
        if private:
            return f'-----BEGIN PRIVATE KEY-----\n{body}\n-----END PRIVATE KEY-----'
        return f'-----BEGIN PUBLIC KEY-----\n{body}\n-----END PUBLIC KEY-----'

    @staticmethod
    def _sign(params, private_key_text):
        private_key = serialization.load_pem_private_key(
            private_key_text.encode('utf-8'),
            password=None,
        )
        sign_content = AlipayService._sign_content(params)
        signature = private_key.sign(
            sign_content.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def _verify(params, public_key_text):
        signature = params.get('sign')
        if not signature:
            return False

        public_key = serialization.load_pem_public_key(public_key_text.encode('utf-8'))
        sign_content = AlipayService._sign_content(params)
        try:
            public_key.verify(
                base64.b64decode(signature),
                sign_content.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except InvalidSignature:
            return False

    @staticmethod
    def _sign_content(params):
        filtered = {
            key: value
            for key, value in params.items()
            if key != 'sign' and value not in [None, '']
        }
        return '&'.join(f'{key}={filtered[key]}' for key in sorted(filtered))

    @staticmethod
    def _format_amount(amount):
        return str(AlipayService._to_decimal(amount))

    @staticmethod
    def _to_decimal(amount):
        return Decimal(str(amount or '0')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
