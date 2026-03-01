from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom, get_jwt_identity
from services.ershoushuji_service import ErshoushujiService

ershoushuji_bp = Blueprint('ershoushuji', __name__)


@ershoushuji_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    identity = get_jwt_identity()
    return R_ok(data=ErshoushujiService.page(request.args.to_dict(), identity))


@ershoushuji_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=ErshoushujiService.list_all(request.args.to_dict()))


@ershoushuji_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=ErshoushujiService.get_by_id(id))


@ershoushuji_bp.route('/detail/<int:id>', methods=['GET'])
def detail(id):
    return R_ok(data=ErshoushujiService.get_by_id(id))


@ershoushuji_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    ErshoushujiService.save(request.json)
    return R_ok()


@ershoushuji_bp.route('/add', methods=['POST'])
def add():
    ErshoushujiService.save(request.json)
    return R_ok()


@ershoushuji_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    ok, err = ErshoushujiService.update(request.json)
    return R_ok() if ok else R_error(err)


@ershoushuji_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    ErshoushujiService.delete(request.json)
    return R_ok()
