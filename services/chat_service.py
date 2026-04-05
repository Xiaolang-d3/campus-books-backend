import json
from datetime import datetime
from models import ChatSession, ChatMessage, Book, db
from utils import model_to_dict, generate_id


class ChatService:
    @staticmethod
    def get_or_create_session(user_id):
        """获取或创建用户的当前会话"""
        # 获取用户最近的会话
        session = ChatSession.query.filter_by(user_id=user_id).order_by(
            ChatSession.last_message_time.desc()
        ).first()
        
        # 如果没有会话或最近的会话消息数超过50条，创建新会话
        if not session or session.message_count >= 50:
            session = ChatSession(
                id=generate_id(),
                user_id=user_id,
                title='新对话',
                message_count=0,
                last_message_time=datetime.now()
            )
            db.session.add(session)
            db.session.commit()
        
        return session

    @staticmethod
    def get_session_list(user_id, limit=10):
        """获取用户的会话列表"""
        sessions = ChatSession.query.filter_by(user_id=user_id).order_by(
            ChatSession.last_message_time.desc()
        ).limit(limit).all()
        
        result = []
        for session in sessions:
            data = model_to_dict(session)
            # 获取第一条消息作为预览
            first_msg = ChatMessage.query.filter_by(
                session_id=session.id, role='user'
            ).first()
            data['preview'] = first_msg.content[:50] if first_msg else '新对话'
            result.append(data)
        
        return result

    @staticmethod
    def get_session_messages(session_id, user_id):
        """获取会话的所有消息"""
        # 验证会话属于该用户
        session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            return None
        
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(
            ChatMessage.addtime.asc()
        ).all()
        
        result = []
        for msg in messages:
            data = model_to_dict(msg)
            # 解析extra_data
            if msg.extra_data:
                try:
                    data['metadata'] = json.loads(msg.extra_data)
                except:
                    data['metadata'] = {}
            result.append(data)
        
        return result

    @staticmethod
    def save_message(session_id, role, content, content_type='text', metadata=None):
        """保存消息"""
        message = ChatMessage(
            id=generate_id(),
            session_id=session_id,
            role=role,
            content=content,
            content_type=content_type,
            extra_data=json.dumps(metadata) if metadata else None
        )
        db.session.add(message)
        
        # 更新会话信息
        session = ChatSession.query.get(session_id)
        if session:
            session.message_count = session.message_count + 1
            session.last_message_time = datetime.now()
            
            # 如果是第一条用户消息，用它作为会话标题
            if session.message_count == 1 and role == 'user':
                session.title = content[:30] + ('...' if len(content) > 30 else '')
        
        db.session.commit()
        return model_to_dict(message)

    @staticmethod
    def create_session(user_id, title='新对话'):
        """创建新会话"""
        session = ChatSession(
            id=generate_id(),
            user_id=user_id,
            title=title,
            message_count=0,
            last_message_time=datetime.now()
        )
        db.session.add(session)
        db.session.commit()
        return model_to_dict(session)

    @staticmethod
    def delete_session(session_id, user_id):
        """删除会话"""
        session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            return False
        
        # 删除会话会级联删除所有消息
        db.session.delete(session)
        db.session.commit()
        return True

    @staticmethod
    def search_books_for_ai(query, limit=5):
        """为AI搜索书籍（用于推荐）"""
        books = Book.query.filter(
            db.or_(
                Book.title.like(f'%{query}%'),
                Book.author.like(f'%{query}%'),
                Book.description.like(f'%{query}%')
            )
        ).filter_by(status=1).limit(limit).all()
        
        result = []
        for book in books:
            data = {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'cover': book.cover,
                'price': float(book.price) if book.price else 0,
                'original_price': float(book.original_price) if book.original_price else 0,
                'stock': book.stock,
                'condition': book.condition.name if book.condition else '',
                'category': book.category.name if book.category else ''
            }
            result.append(data)
        
        return result

    @staticmethod
    def format_book_recommendation(books):
        """格式化书籍推荐为富文本"""
        if not books:
            return None
        
        return {
            'type': 'book_list',
            'books': books
        }
