from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom, get_jwt_identity
from services.shangjia_service import ShangjiaService

shangjia_bp = Blueprint('shangjia', __name__)


@shangjia_bp.route('/register', methods=['POST'])
def register():
    ok, err = ShangjiaService.register(request.json)
    return R_ok() if ok else R_error(err)


@shangjia_bp.route('/session', methods=['GET'])
@login_required_custom
def session_info():
    identity = get_jwt_identity()
    return R_ok(data=ShangjiaService.get_by_id(identity['id']))


@shangjia_bp.route('/resetPass', methods=['POST'])
def reset_pass():
    username = request.args.get('username') or request.json.get('username')
    ok, err = ShangjiaService.reset_pass(username)
    return R_ok('密码已重置为：123456') if ok else R_error(err)


@shangjia_bp.route('/page', methods=['GET'])
@login_required_custom
def page():
    return R_ok(data=ShangjiaService.page(request.args.to_dict()))


@shangjia_bp.route('/list', methods=['GET'])
def list_all():
    return R_ok(data=ShangjiaService.list_all(request.args.to_dict()))


@shangjia_bp.route('/info/<int:id>', methods=['GET'])
@login_required_custom
def info(id):
    return R_ok(data=ShangjiaService.get_by_id(id))


@shangjia_bp.route('/detail/<int:id>', methods=['GET'])
def detail(id):
    return R_ok(data=ShangjiaService.get_by_id(id))


@shangjia_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    ok, err = ShangjiaService.save(request.json)
    return R_ok() if ok else R_error(err)


@shangjia_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    ok, err = ShangjiaService.update(request.json)
    return R_ok() if ok else R_error(err)


@shangjia_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    ShangjiaService.delete(request.json)
    return R_ok()
