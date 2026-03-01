from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom
from models import News
from services.crud_service import CrudService

news_bp = Blueprint('news', __name__)
_svc = CrudService(News, like_fields=['title'], not_found_msg='公告不存在')


@news_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    return R_ok(data=_svc.page(request.args.to_dict()))


@news_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=_svc.list_all(request.args.to_dict()))


@news_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=_svc.get_by_id(id))


@news_bp.route('/detail/<int:id>', methods=['GET'])
def detail(id):
    return R_ok(data=_svc.get_by_id(id))


@news_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    _svc.save(request.json)
    return R_ok()


@news_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    ok, err = _svc.update(request.json)
    return R_ok() if ok else R_error(err)


@news_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    _svc.delete(request.json)
    return R_ok()
