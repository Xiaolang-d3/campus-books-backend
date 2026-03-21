from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom
from models import BookCategory
from services.crud_service import CrudService

shujifenlei_bp = Blueprint('shujifenlei', __name__)
_svc = CrudService(BookCategory, like_fields=['name'], not_found_msg='分类不存在')


@shujifenlei_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    return R_ok(data=_svc.page(request.args.to_dict()))


@shujifenlei_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=_svc.list_all(request.args.to_dict()))


@shujifenlei_bp.route('/option', methods=['GET'])
def option():
    return R_ok(data=_svc.option())


@shujifenlei_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=_svc.get_by_id(id))


@shujifenlei_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    _svc.save(request.json)
    return R_ok()


@shujifenlei_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    ok, err = _svc.update(request.json)
    return R_ok() if ok else R_error(err)


@shujifenlei_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    _svc.delete(request.json)
    return R_ok()
