from models import Address, db
from utils import model_to_dict, paginate_query, apply_filters, generate_id


class AddressService:
    @staticmethod
    def page(params, identity=None):
        query = Address.query
        if identity and identity.get('role') != '管理员':
            query = query.filter_by(user_id=identity['id'])
        query = apply_filters(Address, query, params, like_fields=['contact_name', 'detail', 'phone'])
        return paginate_query(Address, query, params)

    @staticmethod
    def list_all(params, identity=None):
        query = Address.query
        if identity and identity.get('role') != '管理员':
            query = query.filter_by(user_id=identity['id'])
        query = apply_filters(Address, query, params, like_fields=['contact_name', 'detail'])
        return paginate_query(Address, query, params)

    @staticmethod
    def get_by_id(addr_id):
        return model_to_dict(Address.query.get(addr_id))

    @staticmethod
    def save(data, identity):
        data['id'] = generate_id()
        data['user_id'] = identity['id']
        if data.get('is_default') == 1 or data.get('is_default') == '是':
            Address.query.filter_by(user_id=identity['id']).update({'is_default': 0})
        addr = Address(**data)
        db.session.add(addr)
        db.session.commit()

    @staticmethod
    def update(data, identity):
        addr = Address.query.get(data.get('id'))
        if not addr:
            return False, '地址不存在'
        if data.get('is_default') == 1 or data.get('is_default') == '是':
            Address.query.filter_by(user_id=identity['id']).update({'is_default': 0})
        for k, v in data.items():
            if hasattr(addr, k):
                setattr(addr, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Address.query.filter(Address.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()

    @staticmethod
    def get_default(identity):
        addr = Address.query.filter_by(user_id=identity['id'], is_default=1).first()
        if not addr:
            addr = Address.query.filter_by(user_id=identity['id']).first()
        return model_to_dict(addr)
