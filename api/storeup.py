from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom, get_jwt_identity
from services.storeup_service import StoreupService

storeup_bp = Blueprint('storeup', __name__)


@storeup_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    identity = get_jwt_identity()
    return R_ok(data=StoreupService.page(request.args.to_dict(), identity))


@storeup_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=StoreupService.list_all(request.args.to_dict()))


@storeup_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=StoreupService.get_by_id(id))


@storeup_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    StoreupService.save(request.json)
    return R_ok()


@storeup_bp.route('/add', methods=['POST'])
def add():
    StoreupService.save(request.json)
    return R_ok()


@storeup_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    ok, err = StoreupService.update(request.json)
    return R_ok() if ok else R_error(err)


@storeup_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    StoreupService.delete(request.json)
    return R_ok()
