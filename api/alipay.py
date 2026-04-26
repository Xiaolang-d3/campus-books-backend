from flask import Blueprint, request

from common import R_error, R_ok
from core import get_jwt_identity, login_required_custom
from services.alipay_service import AlipayService

alipay_bp = Blueprint('alipay', __name__)


@alipay_bp.route('/pagePay', methods=['POST'])
@login_required_custom
def page_pay():
    identity = get_jwt_identity()
    data = request.json or {}
    try:
        return R_ok(data=AlipayService.create_page_pay(data.get('orderId'), identity))
    except ValueError as e:
        return R_error(str(e))


@alipay_bp.route('/precreate', methods=['POST'])
@login_required_custom
def precreate():
    identity = get_jwt_identity()
    data = request.json or {}
    try:
        return R_ok(data=AlipayService.create_qr_pay(data.get('orderId'), identity))
    except ValueError as e:
        return R_error(str(e))


@alipay_bp.route('/query', methods=['GET'])
@login_required_custom
def query():
    identity = get_jwt_identity()
    try:
        return R_ok(data=AlipayService.query_payment(request.args.get('orderId'), identity))
    except ValueError as e:
        return R_error(str(e))


@alipay_bp.route('/recharge/precreate', methods=['POST'])
@login_required_custom
def recharge_precreate():
    identity = get_jwt_identity()
    data = request.json or {}
    try:
        return R_ok(data=AlipayService.create_recharge_qr(data.get('amount'), identity))
    except ValueError as e:
        return R_error(str(e))


@alipay_bp.route('/recharge/query', methods=['GET'])
@login_required_custom
def recharge_query():
    identity = get_jwt_identity()
    try:
        return R_ok(data=AlipayService.query_recharge(request.args.get('rechargeId'), identity))
    except ValueError as e:
        return R_error(str(e))


@alipay_bp.route('/recharge/mockPay', methods=['POST'])
@login_required_custom
def recharge_mock_pay():
    identity = get_jwt_identity()
    data = request.json or {}
    try:
        return R_ok(data=AlipayService.mock_recharge_payment(data.get('rechargeId'), identity))
    except ValueError as e:
        return R_error(str(e))


@alipay_bp.route('/notify', methods=['POST'])
def notify():
    data = request.form.to_dict()
    ok, err = AlipayService.handle_notify(data)
    if not ok:
        print(f'[ALIPAY NOTIFY ERROR] {err}')
    return 'success' if ok else 'failure'
