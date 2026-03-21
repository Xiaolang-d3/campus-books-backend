from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom
from services.discuss_service import ReviewService

discuss_bp = Blueprint('discuss', __name__)


@discuss_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    return R_ok(data=ReviewService.page(request.args.to_dict()))


@discuss_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=ReviewService.list_all(request.args.to_dict()))


@discuss_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=ReviewService.get_by_id(id))


@discuss_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    ReviewService.save(request.json)
    return R_ok()


@discuss_bp.route('/add', methods=['POST'])
def add():
    ReviewService.save(request.json)
    return R_ok()


@discuss_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    ok, err = ReviewService.update(request.json)
    return R_ok() if ok else R_error(err)


@discuss_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    ReviewService.delete(request.json)
    return R_ok()
