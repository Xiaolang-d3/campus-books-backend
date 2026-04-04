from models import Review, User, Book, db
from utils import model_to_dict, paginate_query, apply_filters, generate_id


def review_to_dict(review):
    """将评论对象转换为字典，包含用户名和书籍信息"""
    if review is None:
        return None
    d = model_to_dict(review)
    
    # 添加用户信息
    user = User.query.get(review.user_id) if review.user_id else None
    if user:
        d['user_name'] = user.name
        d['user_student_no'] = user.student_no
    else:
        d['user_name'] = ''
        d['user_student_no'] = ''
    
    # 添加书籍信息
    book = Book.query.get(review.book_id) if review.book_id else None
    if book:
        d['book_title'] = book.title
        d['book_cover'] = book.cover
    else:
        d['book_title'] = ''
        d['book_cover'] = ''
    
    return d


class ReviewService:
    @staticmethod
    def page(params):
        query = Review.query
        query = apply_filters(Review, query, params, like_fields=['content'])
        
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        sort = params.get('sort', 'id')
        order = params.get('order', 'desc')
        
        if hasattr(Review, sort):
            col = getattr(Review, sort)
            query = query.order_by(col.desc() if order == 'desc' else col.asc())
        
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        return {
            'list': [review_to_dict(item) for item in pagination.items],
            'total': pagination.total,
            'pageSize': limit,
            'currPage': page,
        }

    @staticmethod
    def list_all(params):
        refid = params.get('book_id') or params.get('refid')
        query = Review.query
        if refid:
            query = query.filter_by(book_id=int(refid))
        query = apply_filters(Review, query, params, like_fields=['content'])
        
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        sort = params.get('sort', 'id')
        order = params.get('order', 'desc')
        
        if hasattr(Review, sort):
            col = getattr(Review, sort)
            query = query.order_by(col.desc() if order == 'desc' else col.asc())
        
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        return {
            'list': [review_to_dict(item) for item in pagination.items],
            'total': pagination.total,
            'pageSize': limit,
            'currPage': page,
        }

    @staticmethod
    def get_by_id(obj_id):
        return review_to_dict(Review.query.get(obj_id))

    @staticmethod
    def save(data):
        data['id'] = generate_id()
        obj = Review(**data)
        db.session.add(obj)
        db.session.commit()

    @staticmethod
    def update(data):
        obj = Review.query.get(data.get('id'))
        if not obj:
            return False, '评价不存在'
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.session.commit()
        return True, None

    @staticmethod
    def delete(ids):
        Review.query.filter(Review.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()

    @staticmethod
    def reply(review_id, reply_content):
        """卖家回复评论"""
        review = Review.query.get(review_id)
        if not review:
            return False, '评论不存在'
        
        review.reply = reply_content
        db.session.commit()
        return True, None
