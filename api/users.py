from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom, get_jwt_identity
from services.users_service import UsersService

users_bp = Blueprint('users', __name__)


@users_bp.route('/session', methods=['GET'])
@login_required_custom
def session_info():
    identity = get_jwt_identity()
    return R_ok(data=UsersService.get_by_id(identity['id']))


@users_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    return R_ok(data=UsersService.page(request.args.to_dict()))


@users_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=UsersService.get_by_id(id))


@users_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    ok, err = UsersService.save(request.json)
    return R_ok() if ok else R_error(err)


@users_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    ok, err = UsersService.update(request.json)
    return R_ok() if ok else R_error(err)


@users_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    UsersService.delete(request.json)
    return R_ok()
