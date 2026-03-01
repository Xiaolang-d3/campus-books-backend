from flask import Blueprint
from common import R_ok
from services.common_service import CommonService

common_bp = Blueprint('common', __name__)


@common_bp.route('/option/<table_name>/<column_name>', methods=['GET'])
def get_option(table_name, column_name):
    return R_ok(data=CommonService.get_option(table_name, column_name))


@common_bp.route('/group/<table_name>/<column_name>', methods=['GET'])
def group(table_name, column_name):
    return R_ok(data=CommonService.group(table_name, column_name))


@common_bp.route('/value/<table_name>/<x_column>/<y_column>', methods=['GET'])
def value(table_name, x_column, y_column):
    return R_ok(data=CommonService.value(table_name, x_column, y_column))


@common_bp.route('/cal/<table_name>/<column_name>', methods=['GET'])
def cal(table_name, column_name):
    return R_ok(data=CommonService.cal(table_name, column_name))
