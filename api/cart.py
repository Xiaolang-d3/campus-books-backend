from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom, get_jwt_identity
from services.cart_service import CartService

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    identity = get_jwt_identity()
    return R_ok(data=CartService.page(request.args.to_dict(), identity))


@cart_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=CartService.list_all(request.args.to_dict()))


@cart_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=CartService.get_by_id(id))


@cart_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    identity = get_jwt_identity()
    CartService.save(request.json, identity)
    return R_ok()


@cart_bp.route('/add', methods=['POST'])
@login_required_custom
def add():
    identity = get_jwt_identity()
    try:
        CartService.save(request.json, identity)
        return R_ok()
    except ValueError as e:
        return R_error(str(e))


@cart_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    ok, err = CartService.update(request.json)
    return R_ok() if ok else R_error(err)


@cart_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    CartService.delete(request.json)
    return R_ok()
