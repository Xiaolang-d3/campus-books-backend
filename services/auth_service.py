import json
from flask_jwt_extended import create_access_token
from models import Users, Yonghu, Shangjia


class AuthService:
    @staticmethod
    def login(username, password, role):
        if role == 'admin':
            user = Users.query.filter_by(username=username).first()
            if not user or user.password != password:
                return None, '账号或密码不正确'
            identity_data = {'id': user.id, 'username': username, 'tableName': 'users', 'role': '管理员'}
        elif role == 'yonghu':
            user = Yonghu.query.filter_by(yonghuzhanghao=username).first()
            if not user or user.mima != password:
                return None, '账号或密码不正确'
            identity_data = {'id': user.id, 'username': username, 'tableName': 'yonghu', 'role': '用户'}
        elif role == 'shangjia':
            user = Shangjia.query.filter_by(shangjiazhanghao=username).first()
            if not user or user.mima != password:
                return None, '账号或密码不正确'
            identity_data = {'id': user.id, 'username': username, 'tableName': 'shangjia', 'role': '商家'}
        else:
            return None, '角色类型错误'

        token = create_access_token(identity=json.dumps(identity_data))
        return {'token': token, 'role': role, 'userid': user.id, 'username': username}, None
