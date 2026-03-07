import json

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from models import Users, Yonghu


class AuthService:
    @staticmethod
    def _verify_password(saved_password, input_password):
        if saved_password.startswith('pbkdf2:sha256:'):
            return check_password_hash(saved_password, input_password)
        return saved_password == input_password

    @staticmethod
    def login(username, password, role):
        if role == 'admin':
            user = Users.query.filter_by(username=username).first()
            if not user or not AuthService._verify_password(user.password, password):
                return None, '账号或密码不正确'
            identity_data = {'id': user.id, 'username': username, 'tableName': 'users', 'role': '管理员'}
        elif role == 'yonghu':
            user = Yonghu.query.filter_by(yonghuzhanghao=username).first()
            if not user or not AuthService._verify_password(user.mima, password):
                return None, '账号或密码不正确'
            identity_data = {'id': user.id, 'username': username, 'tableName': 'yonghu', 'role': '用户'}
        else:
            return None, '角色类型错误'

        token = create_access_token(identity=json.dumps(identity_data))
        return {'token': token, 'role': role, 'userid': user.id, 'username': username}, None
