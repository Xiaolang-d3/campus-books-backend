from flask import Blueprint, request
from common import R_ok, R_error
from services.recommend_service import RecommendService

recommend_bp = Blueprint('recommend', __name__)


@recommend_bp.route('/home', methods=['GET'])
def home():
    """
    首页推荐接口

    Query Parameters:
        limit: 推荐书籍数量，默认 6 本

    Returns:
        {
            "code": 0,
            "msg": "操作成功",
            "data": {
                "recommendations": [
                    {
                        "id": 1,
                        "title": "...",
                        "cover": "...",
                        "price": 45.00,
                        "author": "...",
                        "reason": "..."
                    }
                ]
            }
        }
    """
    try:
        limit = request.args.get('limit', 6, type=int)
        limit = max(1, min(limit, 20))  # 限制范围 1-20

        recommendations = RecommendService.get_home_recommendations(limit)
        return R_ok(data={'recommendations': recommendations})
    except Exception as e:
        return R_error(f'获取推荐失败: {str(e)}')
