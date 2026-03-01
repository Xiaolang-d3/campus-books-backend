from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom, get_jwt_identity
from services.address_service import AddressService

address_bp = Blueprint('address', __name__)


@address_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    identity = get_jwt_identity()
    return R_ok(data=AddressService.page(request.args.to_dict(), identity))


@address_bp.route('/list', methods=['GET'])
@login_required_custom
def list_all():
    identity = get_jwt_identity()
    return R_ok(data=AddressService.list_all(request.args.to_dict(), identity))


@address_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=AddressService.get_by_id(id))


@address_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    identity = get_jwt_identity()
    AddressService.save(request.json, identity)
    return R_ok()


@address_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    identity = get_jwt_identity()
    ok, err = AddressService.update(request.json, identity)
    return R_ok() if ok else R_error(err)


@address_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    AddressService.delete(request.json)
    return R_ok()


@address_bp.route('/default', methods=['GET'])
@login_required_custom
def get_default():
    identity = get_jwt_identity()
    return R_ok(data=AddressService.get_default(identity))
