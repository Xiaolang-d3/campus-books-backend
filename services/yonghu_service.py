from models import Yonghu, db
from utils import apply_filters, generate_id, model_to_dict, paginate_query


class YonghuService:
    REQUIRED_FIELDS = ('yonghuzhanghao', 'yonghuxingming', 'mima', 'xueyuan', 'zhuanye', 'nianji')

    @staticmethod
    def _validate_payload(data, is_update=False):
        data = data or {}

        for field in YonghuService.REQUIRED_FIELDS:
            if field == 'mima' and is_update and field not in data:
                continue
            value = data.get(field)
            if value is None or str(value).strip() == '':
                field_name = {
                    'yonghuzhanghao': '学号',
                    'yonghuxingming': '姓名',
                    'mima': '密码',
                    'xueyuan': '学院',
                    'zhuanye': '专业',
                    'nianji': '年级',
                }[field]
                return False, f'{field_name}不能为空'

        student_id = str(data.get('yonghuzhanghao', '')).strip()
        if student_id and not (6 <= len(student_id) <= 20):
            return False, '学号长度需在6到20位之间'
        return True, None

    @staticmethod
    def register(data):
        ok, err = YonghuService._validate_payload(data)
        if not ok:
            return False, err
        if Yonghu.query.filter_by(yonghuzhanghao=data.get('yonghuzhanghao')).first():
            return False, '学号已存在'

        payload = dict(data)
        payload['id'] = generate_id()
        user = Yonghu(**payload)
        db.session.add(user)
        db.session.commit()
        return True, None

    @staticmethod
    def get_by_id(user_id):
        return model_to_dict(Yonghu.query.get(user_id))

    @staticmethod
    def reset_pass(username):
        user = Yonghu.query.filter_by(yonghuzhanghao=username).first()
        if not user:
            return False, '用户不存在'
        user.mima = '123456'
        db.session.commit()
        return True, None

    @staticmethod
    def page(params):
        query = Yonghu.query
        query = apply_filters(
            Yonghu,
            query,
            params,
            like_fields=['yonghuzhanghao', 'yonghuxingming', 'xueyuan', 'zhuanye', 'nianji'],
            eq_fields=['xingbie'],
        )
        return paginate_query(Yonghu, query, params)

    @staticmethod
    def list_all(params):
        query = Yonghu.query
        query = apply_filters(
            Yonghu,
            query,
            params,
            like_fields=['yonghuzhanghao', 'yonghuxingming', 'xueyuan', 'zhuanye', 'nianji'],
        )
        return paginate_query(Yonghu, query, params)

    @staticmethod
    def save(data):
        ok, err = YonghuService._validate_payload(data)
        if not ok:
            return False, err
        if Yonghu.query.filter_by(yonghuzhanghao=data.get('yonghuzhanghao')).first():
            return False, '学号已存在'

        payload = dict(data)
        payload['id'] = generate_id()
        user = Yonghu(**payload)
        db.session.add(user)
        db.session.commit()
        return True, None

    @staticmethod
    def update(data):
        user = Yonghu.query.get(data.get('id'))
        if not user:
            return False, '用户不存在'

        ok, err = YonghuService._validate_payload(data, is_update=True)
        if not ok:
            return False, err

        student_id = data.get('yonghuzhanghao')
        if student_id:
            exists = Yonghu.query.filter(
                Yonghu.yonghuzhanghao == student_id,
                Yonghu.id != user.id,
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
        Yonghu.query.filter(Yonghu.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
