from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom
from models import ConfigModel
from services.crud_service import CrudService

config_bp = Blueprint('config', __name__)
_svc = CrudService(ConfigModel, not_found_msg='配置不存在')


@config_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    return R_ok(data=_svc.page(request.args.to_dict()))


@config_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=_svc.list_all(request.args.to_dict()))


@config_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=_svc.get_by_id(id))


@config_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    _svc.save(request.json)
    return R_ok()


@config_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    ok, err = _svc.update(request.json)
    return R_ok() if ok else R_error(err)


@config_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    _svc.delete(request.json)
    return R_ok()
