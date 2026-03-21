import logging
from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom
from services.chat_service import ChatService

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)


@chat_bp.route('/send', methods=['POST'])
@login_required_custom
def send():
    """
    AI 对话接口

    请求体：
    {
        "message": "我想买一本算法书",
        "history": [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"}
        ]
    }

    返回：
    {
        "code": 0,
        "msg": "success",
        "data": {
            "reply": "算法书的话..."
        }
    }
    """
    try:
        data = request.json
        if not data:
            return R_error('请求数据不能为空')

        message = data.get('message', '').strip()
        if not message:
            return R_error('消息内容不能为空')

        history = data.get('history', [])

        reply = ChatService.chat(message, history)
        return R_ok(data={'reply': reply})
    except Exception as e:
        logger.exception('AI 对话接口异常: %s', e)
        return R_error('AI 服务暂时不可用，请稍后重试')
