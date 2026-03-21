from flask import Blueprint
from common import R_ok
from models import ConditionLevel
from services.crud_service import CrudService

condition_level_bp = Blueprint('condition_level', __name__)
_svc = CrudService(ConditionLevel)


@condition_level_bp.route('/option', methods=['GET'])
def option():
    return R_ok(data=_svc.option())
