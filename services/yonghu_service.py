from models import User, db
from models import College, Major
from utils import apply_filters, generate_id, model_to_dict, paginate_query


def user_to_dict(user):
    if user is None:
        return None
    data = model_to_dict(user)
    if user.college:
        data['college_name'] = user.college.name
    else:
        data['college_name'] = ''
    if user.major:
        data['major_name'] = user.major.name
    else:
        data['major_name'] = ''
    return data


class UserService:
    REQUIRED_FIELDS = ('student_no', 'name', 'password')

    @staticmethod
    def _validate_payload(data, is_update=False):
        data = data or {}
        for field in UserService.REQUIRED_FIELDS:
            if is_update and field in ('password', 'student_no') and field not in data:
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
        return user_to_dict(User.query.get(user_id))

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
            eq_fields=['gender', 'college_id', 'major_id'],
        )
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        return {
            'list': [user_to_dict(item) for item in pagination.items],
            'total': pagination.total,
            'pageSize': limit,
            'currPage': page,
        }

    @staticmethod
    def list_all(params):
        query = User.query
        query = apply_filters(
            User,
            query,
            params,
            like_fields=['student_no', 'name'],
        )
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        return {
            'list': [user_to_dict(item) for item in pagination.items],
            'total': pagination.total,
            'pageSize': limit,
            'currPage': page,
        }

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
