from models import User, db
from utils import apply_filters, generate_id, model_to_dict, paginate_query


class UserService:
    REQUIRED_FIELDS = ('student_no', 'name', 'password')

    @staticmethod
    def _validate_payload(data, is_update=False):
        data = data or {}
        for field in UserService.REQUIRED_FIELDS:
            if field == 'password' and is_update and field not in data:
                continue
            value = data.get(field)
            if value is None or str(value).strip() == '':
                field_name = {
                    'student_no': '学号',
                    'name': '姓名',
                    'password': '密码',
                }[field]
                return False, f'{field_name}不能为空'

        student_no = str(data.get('student_no', '')).strip()
        if student_no and not (6 <= len(student_no) <= 20):
            return False, '学号长度需在6到20位之间'
        return True, None

    @staticmethod
    def register(data):
        ok, err = UserService._validate_payload(data)
        if not ok:
            return False, err
        if User.query.filter_by(student_no=data.get('student_no')).first():
            return False, '学号已存在'

        payload = dict(data)
        payload['id'] = generate_id()
        user = User(**payload)
        db.session.add(user)
        db.session.commit()
        return True, None

    @staticmethod
    def get_by_id(user_id):
        return model_to_dict(User.query.get(user_id))

    @staticmethod
    def reset_pass(username):
        user = User.query.filter_by(student_no=username).first()
        if not user:
            return False, '用户不存在'
        user.password = '123456'
        db.session.commit()
        return True, None

    @staticmethod
    def page(params):
        query = User.query
        query = apply_filters(
            User,
            query,
            params,
            like_fields=['student_no', 'name', 'phone'],
            eq_fields=['gender'],
        )
        return paginate_query(User, query, params)

    @staticmethod
    def list_all(params):
        query = User.query
        query = apply_filters(
            User,
            query,
            params,
            like_fields=['student_no', 'name'],
        )
        return paginate_query(User, query, params)

    @staticmethod
    def save(data):
        ok, err = UserService._validate_payload(data)
        if not ok:
            return False, err
        if User.query.filter_by(student_no=data.get('student_no')).first():
            return False, '学号已存在'

        payload = dict(data)
        payload['id'] = generate_id()
        user = User(**payload)
        db.session.add(user)
        db.session.commit()
        return True, None

    @staticmethod
    def update(data):
        user = User.query.get(data.get('id'))
        if not user:
            return False, '用户不存在'

        ok, err = UserService._validate_payload(data, is_update=True)
        if not ok:
            return False, err

        student_no = data.get('student_no')
        if student_no:
            exists = User.query.filter(
                User.student_no == student_no,
                User.id != user.id,
            ).first()
            if exists:
                return False, '学号已存在'

        for k, v in data.items():
            if hasattr(user, k):
                setattr(user, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        User.query.filter(User.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
