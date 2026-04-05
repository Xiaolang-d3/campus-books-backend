from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom, get_jwt_identity
from services.orders_service import OrderService

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    identity = get_jwt_identity()
    return R_ok(data=OrderService.page(request.args.to_dict(), identity))


@orders_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=OrderService.list_all(request.args.to_dict()))


@orders_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=OrderService.get_by_id(id))


@orders_bp.route('/detail/<int:id>', methods=['GET'])
def detail(id):
    return R_ok(data=OrderService.get_by_id(id))


@orders_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    identity = get_jwt_identity()
    try:
        order = OrderService.save(request.json, identity)
        return R_ok(data=order)
    except ValueError as e:
        return R_error(str(e))


@orders_bp.route('/add', methods=['POST'])
def add():
    try:
        order = OrderService.save(request.json)
        return R_ok(data=order)
    except ValueError as e:
        return R_error(str(e))


@orders_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    identity = get_jwt_identity()
    ok, err = OrderService.update(request.json, identity)
    return R_ok() if ok else R_error(err)


@orders_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    identity = get_jwt_identity()
    OrderService.delete(request.json, identity)
    return R_ok()


@orders_bp.route('/value/<x_col>/<y_col>', methods=['GET'])
def value_stat(x_col, y_col):
    try:
        return R_ok(data=OrderService.value_stat(x_col, y_col))
    except ValueError as e:
        return R_error(str(e))


@orders_bp.route('/value/<x_col>/<y_col>/<time_stat_type>', methods=['GET'])
def value_time_stat(x_col, y_col, time_stat_type):
    try:
        return R_ok(data=OrderService.value_time_stat(x_col, y_col, time_stat_type))
    except ValueError as e:
        return R_error(str(e))


@orders_bp.route('/group/<column_name>', methods=['GET'])
def group_stat(column_name):
    try:
        return R_ok(data=OrderService.group_stat(column_name))
    except ValueError as e:
        return R_error(str(e))
