from datetime import datetime, timedelta
from sqlalchemy import func, text
from models import Book, Order, User, BookCategory, db


class StatisticsService:
    """统计服务"""
    
    @staticmethod
    def get_dashboard_stats():
        """首页统计数据"""
        # 用户总数
        total_users = User.query.count()
        
        # 书籍总数
        total_books = Book.query.count()
        
        # 在售书籍数
        on_sale_books = Book.query.filter_by(status=1).filter(Book.stock > 0).count()
        
        # 订单总数
        total_orders = Order.query.count()
        
        # 已完成订单数
        completed_orders = Order.query.filter_by(status='已完成').count()
        
        # 总销售额（已支付、已发货、已完成）
        paid_statuses = ['已支付', '已发货', '已完成']
        total_sales = db.session.query(func.sum(Order.total_amount)).filter(
            Order.status.in_(paid_statuses)
        ).scalar() or 0
        
        # 今日新增订单
        today = datetime.now().date()
        today_orders = Order.query.filter(
            func.date(Order.addtime) == today
        ).count()
        
        # 今日销售额
        today_sales = db.session.query(func.sum(Order.total_amount)).filter(
            func.date(Order.addtime) == today,
            Order.status.in_(paid_statuses)
        ).scalar() or 0
        
        return {
            'total_users': total_users,
            'total_books': total_books,
            'on_sale_books': on_sale_books,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_sales': float(total_sales),
            'today_orders': today_orders,
            'today_sales': float(today_sales)
        }
    
    @staticmethod
    def get_order_trend():
        """订单趋势统计（最近7天）"""
        result = []
        paid_statuses = ['已支付', '已发货', '已完成']
        
        for i in range(6, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            count = Order.query.filter(func.date(Order.addtime) == date).count()
            paid_count = Order.query.filter(
                func.date(Order.addtime) == date,
                Order.status.in_(paid_statuses)
            ).count()
            
            result.append({
                'date': date.strftime('%m-%d'),
                'total': count,
                'paid': paid_count
            })
        
        return result
    
    @staticmethod
    def get_order_status_distribution():
        """订单状态分布"""
        sql = text(
            "SELECT status, COUNT(*) as count FROM `order` "
            "GROUP BY status ORDER BY count DESC"
        )
        result = db.session.execute(sql)
        
        return [
            {'name': row[0] or '未知', 'value': row[1]}
            for row in result
        ]
    
    @staticmethod
    def get_sales_by_category():
        """各分类销售额统计"""
        paid_statuses = ['已支付', '已发货', '已完成']
        
        # 通过书籍关联查询分类销售额
        result = db.session.query(
            BookCategory.name,
            func.sum(Order.total_amount).label('total')
        ).join(
            Book, Book.id == Order.book_id
        ).join(
            BookCategory, BookCategory.id == Book.category_id
        ).filter(
            Order.status.in_(paid_statuses)
        ).group_by(
            BookCategory.name
        ).all()
        
        return [
            {'name': row[0], 'value': float(row[1] or 0)}
            for row in result
        ]
    
    @staticmethod
    def get_sales_trend():
        """销售额趋势（最近30天）"""
        result = []
        paid_statuses = ['已支付', '已发货', '已完成']
        
        for i in range(29, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            sales = db.session.query(func.sum(Order.total_amount)).filter(
                func.date(Order.addtime) == date,
                Order.status.in_(paid_statuses)
            ).scalar() or 0
            
            result.append({
                'date': date.strftime('%m-%d'),
                'sales': float(sales)
            })
        
        return result
