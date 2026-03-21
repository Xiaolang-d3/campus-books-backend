from flask import Blueprint, request

from common import R_error, R_ok
from core import get_jwt_identity, login_required_custom
from services.wallet_service import WalletService

wallet_bp = Blueprint('wallet', __name__)


@wallet_bp.route('/balance', methods=['GET'])
@login_required_custom
def balance():
    identity = get_jwt_identity()
    try:
        return R_ok(data=WalletService.get_balance(identity))
    except ValueError as e:
        return R_error(str(e))


@wallet_bp.route('/logs', methods=['GET'])
@login_required_custom
def logs():
    identity = get_jwt_identity()
    try:
        return R_ok(data=WalletService.get_logs(identity, request.args.to_dict()))
    except ValueError as e:
        return R_error(str(e))


@wallet_bp.route('/pay', methods=['POST'])
@login_required_custom
def pay():
    identity = get_jwt_identity()
    data = request.json or {}
    ok, err = WalletService.pay(identity, data.get('orderid'))
    return R_ok() if ok else R_error(err)


@wallet_bp.route('/recharge', methods=['POST'])
@login_required_custom
def recharge():
    identity = get_jwt_identity()
    data = request.json or {}
    ok, err = WalletService.recharge(identity, data.get('amount'))
    return R_ok() if ok else R_error(err)
