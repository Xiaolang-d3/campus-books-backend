from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom, get_jwt_identity
from services.ershoushuji_service import BookService

ershoushuji_bp = Blueprint('ershoushuji', __name__)


@ershoushuji_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    identity = get_jwt_identity()
    return R_ok(data=BookService.page(request.args.to_dict(), identity))


@ershoushuji_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=BookService.list_all(request.args.to_dict()))


@ershoushuji_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=BookService.get_by_id(id))


@ershoushuji_bp.route('/detail/<int:id>', methods=['GET'])
def detail(id):
    return R_ok(data=BookService.get_by_id(id))


@ershoushuji_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    identity = get_jwt_identity()
    try:
        book = BookService.save(request.json, identity)
        return R_ok(data=book)
    except ValueError as e:
        return R_error(str(e))


@ershoushuji_bp.route('/add', methods=['POST'])
def add():
    try:
        book = BookService.save(request.json)
        return R_ok(data=book)
    except ValueError as e:
        return R_error(str(e))


@ershoushuji_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    identity = get_jwt_identity()
    ok, err = BookService.update(request.json, identity)
    return R_ok() if ok else R_error(err)


@ershoushuji_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    identity = get_jwt_identity()
    deleted, err = BookService.delete(request.json, identity)
    if err:
        return R_error(err)
    if deleted > 0:
        return R_ok()
    return R_error('删除失败，书籍不存在或无权限')
