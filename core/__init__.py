import json
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity as _get_jwt_identity


def login_required_custom(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            print(f'[AUTH ERROR] {type(e).__name__}: {e}')
            return jsonify({'code': 401, 'msg': 'token失效，请重新登录'}), 401
        return f(*args, **kwargs)
    return decorated


def get_jwt_identity():
    raw = _get_jwt_identity()
    if isinstance(raw, str):
        return json.loads(raw)
    return raw
