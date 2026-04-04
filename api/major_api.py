from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom
from models import Major, db
from utils import model_to_dict


major_bp = Blueprint('major', __name__)


@major_bp.route('/list', methods=['GET'])
def list_all():
    college_id = request.args.get('college_id')
    query = Major.query
    if college_id:
        query = query.filter_by(college_id=college_id)
    majors = query.order_by(Major.id.desc()).all()
    return R_ok(data=[model_to_dict(m) for m in majors])


@major_bp.route('/info/<int:id>', methods=['GET'])
def info(id):
    major = Major.query.get(id)
    return R_ok(data=model_to_dict(major))


@major_bp.route('/save', methods=['POST'])
@login_required_custom
def save():
    data = request.json
    if not data.get('name'):
        return R_error('专业名称不能为空')
    major = Major(**data)
    db.session.add(major)
    db.session.commit()
    return R_ok()


@major_bp.route('/update', methods=['POST'])
@login_required_custom
def update():
    data = request.json
    major = Major.query.get(data.get('id'))
    if not major:
        return R_error('专业不存在')
    for k, v in data.items():
        if hasattr(major, k):
            setattr(major, k, v)
    db.session.commit()
    return R_ok()


@major_bp.route('/delete', methods=['POST'])
@login_required_custom
def delete():
    ids = request.json if isinstance(request.json, list) else [request.json]
    Major.query.filter(Major.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return R_ok()
