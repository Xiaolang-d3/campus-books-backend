from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom
from models import College, db
from utils import model_to_dict


college_bp = Blueprint('college', __name__)


@college_bp.route('/list', methods=['GET'])
def list_all():
    colleges = College.query.order_by(College.id.desc()).all()
    return R_ok(data=[model_to_dict(c) for c in colleges])


@college_bp.route('/info/<int:id>', methods=['GET'])
def info(id):
    college = College.query.get(id)
    return R_ok(data=model_to_dict(college))


@college_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    data = request.json
    if not data.get('name'):
        return R_error('学院名称不能为空')
    if College.query.filter_by(name=data['name']).first():
        return R_error('学院已存在')
    college = College(**data)
    db.session.add(college)
    db.session.commit()
    return R_ok()


@college_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    data = request.json
    college = College.query.get(data.get('id'))
    if not college:
        return R_error('学院不存在')
    for k, v in data.items():
        if hasattr(college, k):
            setattr(college, k, v)
    db.session.commit()
    return R_ok()


@college_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    ids = request.json if isinstance(request.json, list) else [request.json]
    College.query.filter(College.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return R_ok()
