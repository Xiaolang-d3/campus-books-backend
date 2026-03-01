from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom, get_jwt_identity
from services.yonghu_service import YonghuService

yonghu_bp = Blueprint('yonghu', __name__)


@yonghu_bp.route('/register', methods=['POST'])
def register():
    ok, err = YonghuService.register(request.json)
    return R_ok() if ok else R_error(err)


@yonghu_bp.route('/session', methods=['GET'])
@login_required_custom
def session_info():
    identity = get_jwt_identity()
    return R_ok(data=YonghuService.get_by_id(identity['id']))


@yonghu_bp.route('/resetPass', methods=['POST'])
def reset_pass():
    username = request.args.get('username') or request.json.get('username')
    ok, err = YonghuService.reset_pass(username)
    return R_ok('密码已重置为：123456') if ok else R_error(err)


@yonghu_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    return R_ok(data=YonghuService.page(request.args.to_dict()))


@yonghu_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=YonghuService.list_all(request.args.to_dict()))


@yonghu_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=YonghuService.get_by_id(id))


@yonghu_bp.route('/detail/<int:id>', methods=['GET'])
def detail(id):
    return R_ok(data=YonghuService.get_by_id(id))


@yonghu_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    ok, err = YonghuService.save(request.json)
    return R_ok() if ok else R_error(err)


@yonghu_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    ok, err = YonghuService.update(request.json)
    return R_ok() if ok else R_error(err)


@yonghu_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    YonghuService.delete(request.json)
    return R_ok()
