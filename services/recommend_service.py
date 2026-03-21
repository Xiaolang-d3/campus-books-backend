import time
import logging
import requests
from models import Book, db
from utils import model_to_dict
from flask import current_app

logger = logging.getLogger(__name__)

# 缓存：{cache_key: (timestamp, data)}
_cache = {}
DEFAULT_REASONS = [
    "这本书在校园里非常受欢迎，赶紧来看看！",
    "经典教材，考研考公必备，好评如潮！",
    "学长学姐强烈推荐，知识点全面，覆盖考试重点！",
    "二手好书低价出，保存完好，物超所值！",
    "这学期刚好需要？来看看这本书的成色吧！",
]


class RecommendService:
    """AI 书籍推荐服务"""

    @staticmethod
    def _get_cache(key):
        """获取缓存数据"""
        if key not in _cache:
            return None
        timestamp, data = _cache[key]
        ttl = current_app.config.get('CACHE_TTL', 600)
        if time.time() - timestamp < ttl:
            return data
        del _cache[key]
        return None

    @staticmethod
    def _set_cache(key, data):
        """设置缓存数据"""
        _cache[key] = (time.time(), data)

    @staticmethod
    def get_home_recommendations(limit=6):
        """
        获取首页推荐书籍及 AI 推荐理由

        Args:
            limit: 推荐书籍数量，默认 6 本

        Returns:
            list: 推荐书籍列表，每本书包含基础信息 + AI 推荐理由
        """
        cache_key = f'home_recommendations_{limit}'
        cached = RecommendService._get_cache(cache_key)
        if cached is not None:
            return cached

        # 获取热门书籍（按上架时间倒序，取有库存的上架书籍）
        books = (
            Book.query
            .filter(Book.status == 1)
            .filter(Book.stock > 0)
            .order_by(Book.addtime.desc())
            .limit(limit)
            .all()
        )

        if not books:
            return []

        recommendations = []
        for book in books:
            book_dict = model_to_dict(book)

            # 附加关联信息
            if book.category:
                book_dict['category_name'] = book.category.name
            if book.condition:
                book_dict['condition_name'] = book.condition.name
            if book.seller:
                book_dict['seller_name'] = book.seller.name

            # 生成推荐理由
            book_dict['reason'] = RecommendService._generate_reason(book_dict)

            # 排除冗余字段，减小返回数据量
            for field in ['description', 'addtime', 'updatetime']:
                book_dict.pop(field, None)

            recommendations.append(book_dict)

        # 缓存结果
        RecommendService._set_cache(cache_key, recommendations)

        return recommendations

    @staticmethod
    def _generate_reason(book_info):
        """
        为单本书籍生成推荐理由

        优先尝试调用通义千问 API，失败时返回默认推荐语
        """
        api_key = current_app.config.get('DASHSCOPE_API_KEY', '')
        if not api_key:
            logger.warning("DashScope API Key 未配置，使用默认推荐语")
            return DEFAULT_REASONS[hash(book_info.get('id', '')) % len(DEFAULT_REASONS)]

        prompt = RecommendService._build_prompt(book_info)
        reason = RecommendService._call_dashscope(prompt, api_key)

        if reason:
            return reason
        return DEFAULT_REASONS[hash(book_info.get('id', '')) % len(DEFAULT_REASONS)]

    @staticmethod
    def _build_prompt(book_info):
        """构建发送给 AI 的 Prompt"""
        title = book_info.get('title', '')
        author = book_info.get('author', '未知')
        publisher = book_info.get('publisher', '未知')
        category = book_info.get('category_name', '')
        condition = book_info.get('condition_name', '')
        price = book_info.get('price', 0)

        prompt = f"""请为以下书籍生成一段简短、有吸引力的推荐语（30-50字以内），适合在二手书交易平台展示给大学生。

书籍信息：
- 书名：《{title}》
- 作者：{author}
- 出版社：{publisher}
{f'- 分类：{category}' if category else ''}
{f'- 成色：{condition}' if condition else ''}
- 价格：¥{price}

要求：
1. 语言亲切自然，像朋友推荐
2. 突出书籍价值或实用性
3. 不要提及"二手"字眼，可以用"好书"、"闲置"等中性词
4. 直接返回推荐语，不要加引号或前缀

推荐语："""

        return prompt

    @staticmethod
    def _call_dashscope(prompt, api_key):
        """
        调用通义千问 API 生成推荐语

        Args:
            prompt: 发送给 AI 的提示词
            api_key: DashScope API Key

        Returns:
            str: AI 生成的推荐语，失败返回 None
        """
        try:
            url = current_app.config.get('DASHSCOPE_BASE_URL') + '/chat/completions'
            model = current_app.config.get('DASHSCOPE_MODEL', 'qwen-turbo')
            max_tokens = current_app.config.get('DASHSCOPE_MAX_TOKENS', 200)
            temperature = current_app.config.get('DASHSCOPE_TEMPERATURE', 0.8)

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }

            payload = {
                'model': model,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': max_tokens,
                'temperature': temperature,
            }

            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()

            result = response.json()
            choices = result.get('choices', [])

            if choices and len(choices) > 0:
                content = choices[0].get('message', {}).get('content', '')
                # 清理返回内容（去除首尾空白）
                content = content.strip()
                # 去除可能的引号包裹
                if content.startswith('"') and content.endswith('"'):
                    content = content[1:-1]
                if content.startswith("'") and content.endswith("'"):
                    content = content[1:-1]
                return content

            logger.warning(f"DashScope 返回格式异常: {result}")
            return None

        except requests.exceptions.Timeout:
            logger.error("DashScope API 调用超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"DashScope API 请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"DashScope API 调用异常: {e}")
            return None
