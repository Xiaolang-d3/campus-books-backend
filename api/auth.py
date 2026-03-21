import json

from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from models import Admin, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or request.form
    username = data.get('username', '')
    password = data.get('password', '')
    role = data.get('role', 'admin')
    result, err = AuthService.login(username, password, role)
    if err:
        return R_error(err)
    return R_ok('登录成功', result)
