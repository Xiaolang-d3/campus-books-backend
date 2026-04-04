from flask import Blueprint
from common import R_ok
from services.statistics_service import StatisticsService

statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """首页统计数据"""
    return R_ok(data=StatisticsService.get_dashboard_stats())


@statistics_bp.route('/order/trend', methods=['GET'])
def order_trend():
    """订单趋势统计（最近7天）"""
    return R_ok(data=StatisticsService.get_order_trend())


@statistics_bp.route('/order/status', methods=['GET'])
def order_status():
    """订单状态分布"""
    return R_ok(data=StatisticsService.get_order_status_distribution())


@statistics_bp.route('/sales/category', methods=['GET'])
def sales_category():
    """各分类销售额统计"""
    return R_ok(data=StatisticsService.get_sales_by_category())


@statistics_bp.route('/sales/trend', methods=['GET'])
def sales_trend():
    """销售额趋势（最近30天）"""
    return R_ok(data=StatisticsService.get_sales_trend())
