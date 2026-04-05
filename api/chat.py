import logging
import re
from flask import Blueprint, request
from common import R_ok, R_error
from core import login_required_custom, get_jwt_identity
from services.chat_service import ChatService

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)


@chat_bp.route('/send', methods=['POST'])
@login_required_custom
def send():
    """
    AI 对话接口（带历史记录保存）

    请求体：
    {
        "message": "我想买一本算法书",
        "session_id": 123456789  // 可选，不传则使用当前会话
    }

    返回：
    {
        "code": 0,
        "msg": "success",
        "data": {
            "reply": "算法书的话...",
            "content_type": "text",  // 或 "book_list"
            "metadata": {...},  // 如果是书籍推荐，包含书籍信息
            "session_id": 123456789
        }
    }
    """
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        data = request.json
        if not data:
            return R_error('请求数据不能为空')

        message = data.get('message', '').strip()
        if not message:
            return R_error('消息内容不能为空')

        # 获取或创建会话
        session_id = data.get('session_id')
        if session_id:
            session = ChatService.get_session_messages(session_id, user_id)
            if not session:
                return R_error('会话不存在')
        else:
            session = ChatService.get_or_create_session(user_id)
            session_id = session.id

        # 保存用户消息
        ChatService.save_message(session_id, 'user', message)

        # 获取历史消息（最近10轮）
        messages = ChatService.get_session_messages(session_id, user_id)
        history = [{'role': m['role'], 'content': m['content']} for m in messages[-20:]]

        # 检查是否需要推荐书籍
        book_keywords = ['推荐', '找书', '买书', '教材', '书籍', '有什么', '哪些书']
        should_recommend = any(keyword in message for keyword in book_keywords)

        reply_content = None
        content_type = 'text'
        metadata = None

        if should_recommend:
            # 提取关键词进行书籍搜索
            search_query = extract_book_keywords(message)
            if search_query:
                books = ChatService.search_books_for_ai(search_query, limit=5)
                if books:
                    content_type = 'book_list'
                    metadata = {'books': books}
                    reply_content = generate_book_recommendation_text(books, message)

        # 如果没有找到书籍或不需要推荐，使用通用回复
        if not reply_content:
            reply_content = generate_ai_reply(message, history)

        # 保存AI回复
        ChatService.save_message(session_id, 'assistant', reply_content, content_type, metadata)

        return R_ok(data={
            'reply': reply_content,
            'content_type': content_type,
            'metadata': metadata,
            'session_id': session_id
        })
    except Exception as e:
        logger.exception('AI 对话接口异常: %s', e)
        return R_error('AI 服务暂时不可用，请稍后重试')


@chat_bp.route('/sessions', methods=['GET'])
@login_required_custom
def get_sessions():
    """获取用户的会话列表"""
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        sessions = ChatService.get_session_list(user_id, limit=20)
        return R_ok(data={'sessions': sessions})
    except Exception as e:
        logger.exception('获取会话列表异常: %s', e)
        return R_error('获取会话列表失败')


@chat_bp.route('/session/<int:session_id>', methods=['GET'])
@login_required_custom
def get_session(session_id):
    """获取会话的所有消息"""
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        messages = ChatService.get_session_messages(session_id, user_id)
        if messages is None:
            return R_error('会话不存在')
        
        return R_ok(data={'messages': messages})
    except Exception as e:
        logger.exception('获取会话消息异常: %s', e)
        return R_error('获取会话消息失败')


@chat_bp.route('/session/new', methods=['POST'])
@login_required_custom
def create_session():
    """创建新会话"""
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        data = request.json or {}
        title = data.get('title', '新对话')
        
        session = ChatService.create_session(user_id, title)
        return R_ok(data={'session': session})
    except Exception as e:
        logger.exception('创建会话异常: %s', e)
        return R_error('创建会话失败')


@chat_bp.route('/session/<int:session_id>', methods=['DELETE'])
@login_required_custom
def delete_session(session_id):
    """删除会话"""
    try:
        identity = get_jwt_identity()
        user_id = identity['id']
        
        success = ChatService.delete_session(session_id, user_id)
        if not success:
            return R_error('会话不存在')
        
        return R_ok(msg='会话已删除')
    except Exception as e:
        logger.exception('删除会话异常: %s', e)
        return R_error('删除会话失败')


def extract_book_keywords(message):
    """从用户消息中提取书籍关键词"""
    # 移除常见的问句词
    message = re.sub(r'(推荐|有什么|哪些|买|找|需要|想要|帮我|给我)', '', message)
    message = re.sub(r'(书|教材|书籍)', '', message)
    message = message.strip()
    
    # 如果剩余内容太短，返回None
    if len(message) < 2:
        return None
    
    return message


def generate_book_recommendation_text(books, user_message):
    """生成书籍推荐的文本回复"""
    if not books:
        return "抱歉，暂时没有找到相关的书籍。你可以换个关键词试试，或者直接去书籍列表浏览。"
    
    intro = "根据你的需求，我为你找到了以下几本书：\n\n"
    
    book_list = []
    for i, book in enumerate(books, 1):
        price_info = f"¥{book['price']:.2f}"
        if book.get('original_price') and book['original_price'] > book['price']:
            price_info += f" (原价 ¥{book['original_price']:.2f})"
        
        book_info = f"{i}. **{book['title']}**\n"
        if book.get('author'):
            book_info += f"   作者：{book['author']}\n"
        book_info += f"   价格：{price_info}\n"
        if book.get('condition'):
            book_info += f"   成色：{book['condition']}\n"
        if book.get('stock', 0) > 0:
            book_info += f"   库存：{book['stock']} 件\n"
        else:
            book_info += "   库存：已售罄\n"
        
        book_list.append(book_info)
    
    return intro + "\n".join(book_list) + "\n\n你可以点击下方的书籍卡片查看详情或直接购买。"


def generate_ai_reply(message, history):
    """生成AI回复（简单规则版本）"""
    message_lower = message.lower()
    
    # 问候语
    if any(word in message_lower for word in ['你好', 'hello', 'hi', '您好']):
        return "你好！我是小书，你的校园二手书助手。我可以帮你推荐教材、解答购买问题、指导发布二手书。有什么我可以帮你的吗？"
    
    # 购买流程
    if any(word in message for word in ['购买', '买书', '下单', '支付']):
        return """购买二手书的流程很简单：

1. **浏览书籍**：在首页或书籍列表中找到你想要的书
2. **查看详情**：点击书籍查看详细信息、成色、价格等
3. **加入购物车**：点击"加入购物车"或"立即购买"
4. **确认订单**：选择收货地址，确认订单信息
5. **支付订单**：使用账户余额支付（需要先充值）
6. **等待发货**：卖家会尽快发货，你可以在"我的订单"中查看物流

如果有任何问题，随时可以联系卖家或平台客服。"""
    
    # 发布流程
    if any(word in message for word in ['发布', '上架', '卖书', '出售']):
        return """发布二手书很简单，按照以下步骤操作：

1. **进入发布页面**：点击"发布闲置"或"我要卖书"
2. **填写书籍信息**：
   - 书名、作者、出版社
   - 上传清晰的书籍照片（封面、内页）
   - 选择书籍分类和成色
3. **设置价格**：参考原价和成色，设置合理的价格
4. **填写描述**：详细描述书籍状态、使用痕迹等
5. **提交审核**：提交后等待审核通过即可上架

**小贴士**：
- 照片要清晰，展示书籍真实状态
- 价格合理更容易卖出
- 详细的描述能增加买家信任"""
    
    # 找书/推荐
    if any(word in message for word in ['推荐', '找书', '有什么书', '哪些书']):
        return "我可以帮你推荐书籍！请告诉我：\n\n1. 你的专业或感兴趣的领域（如：计算机、数学、英语）\n2. 你的年级或学习阶段（如：大一、考研）\n3. 具体的课程或主题（如：数据结构、算法、Python）\n\n例如：\"推荐几本计算机专业大一的教材\" 或 \"有什么Python入门书籍推荐吗？\""
    
    # 默认回复
    return """我是小书，你的校园二手书助手。我可以帮你：

📚 **推荐书籍**：根据专业、课程推荐合适的教材
🛒 **购买指导**：解答购买流程、支付、物流等问题
📤 **发布指导**：教你如何快速发布二手书
💡 **使用建议**：解答平台使用中的各种问题

你可以直接问我问题，比如：
- "推荐几本Python书籍"
- "如何购买二手书？"
- "怎么发布闲置教材？"

有什么我可以帮你的吗？"""
