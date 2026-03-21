import logging
import re

import requests
from flask import current_app

logger = logging.getLogger(__name__)

# 系统提示词：限定 AI 为书籍推荐助手
SYSTEM_PROMPT = """你是一个校园二手书籍平台的 AI 助手，名为"小书"。

你的职责是：
1. 帮用户找书：根据书名、作者、ISBN、分类等推荐相关书籍
2. 购书咨询：回答关于书籍成色、价格、出版社等问题
3. 专业建议：根据用户专业或课程推荐合适的教材或参考书
4. 平台使用指南：解答关于买卖流程、支付、发货等问题

回答要求：
- 语言亲切自然，像朋友聊天
- 回答简洁有力，一般不超过150字
- 如果涉及具体书籍推荐，可以提到"平台上可能有相关书籍，你可以去书籍市场搜索看看"
- 不知道的问题请诚实说不知道
- 不要编造具体的书籍价格或库存信息"""


class ChatService:
    """AI 聊天服务"""

    @staticmethod
    def chat(message, history=None):
        """
        处理用户对话请求

        Args:
            message: 用户发送的消息
            history: 历史对话列表 [{role: 'user'|'assistant', content: '...'}, ...]

        Returns:
            str: AI 的回复文本
        """
        api_key = current_app.config.get('DASHSCOPE_API_KEY', '')
        base_url = (current_app.config.get('DASHSCOPE_BASE_URL') or '').rstrip('/')

        # 未配置在线 AI 时，直接走本地兜底回答，避免页面看起来“坏掉”
        if not api_key or not base_url:
            logger.warning("DashScope 配置不完整，使用本地兜底回复")
            return ChatService._fallback_reply(message)

        # 构建消息列表
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # 追加历史对话（最多保留最近10轮，避免超出token限制）
        if history and isinstance(history, list):
            for item in history[-10:]:
                if isinstance(item, dict) and 'role' in item and 'content' in item:
                    role = item.get('role')
                    content = str(item.get('content', '')).strip()
                    if role in ('user', 'assistant') and content:
                        messages.append({
                            "role": role,
                            "content": content
                        })

        # 追加当前用户消息
        messages.append({"role": "user", "content": message})

        # 调用 DashScope API
        reply = ChatService._call_dashscope(messages, api_key, base_url)

        if reply:
            return reply

        logger.warning("DashScope 调用失败，回退到本地兜底回复")
        return ChatService._fallback_reply(message)

    @staticmethod
    def _call_dashscope(messages, api_key, base_url):
        """
        调用通义千问 API

        Args:
            messages: 消息列表（含 system/user/assistant 角色）
            api_key: DashScope API Key
            base_url: DashScope 基础地址

        Returns:
            str: AI 回复，失败返回 None
        """
        try:
            url = f'{base_url}/chat/completions'
            model = current_app.config.get('DASHSCOPE_MODEL', 'qwen-turbo')
            max_tokens = current_app.config.get('DASHSCOPE_MAX_TOKENS', 300)
            temperature = current_app.config.get('DASHSCOPE_TEMPERATURE', 0.8)

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }

            payload = {
                'model': model,
                'messages': messages,
                'max_tokens': max_tokens,
                'temperature': temperature,
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            choices = result.get('choices', [])

            if choices and len(choices) > 0:
                content = choices[0].get('message', {}).get('content', '')
                return content.strip() if content else None

            logger.warning("DashScope 返回格式异常: %s", result)
            return None

        except requests.exceptions.Timeout:
            logger.error("DashScope API 调用超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error("DashScope API 请求失败: %s", e)
            return None
        except Exception as e:
            logger.error("DashScope API 调用异常: %s", e)
            return None

    @staticmethod
    def _fallback_reply(message):
        """
        本地兜底回复逻辑：
        - 当在线 AI 未配置或调用失败时，仍能回答常见平台问题
        - 保证 AI 助手页面可用
        """
        text = re.sub(r'\s+', ' ', str(message or '')).strip().lower()

        if not text:
            return '你好，我是小书，可以帮你找教材、了解购书流程，或指导你发布二手书。'

        if any(keyword in text for keyword in ['算法', '数据结构', '408', '计算机']):
            return (
                '如果你想找计算机类教材，可以优先看看算法、数据结构、计算机组成原理这几类。'
                '平台上可能有相关书籍，建议去书籍市场按书名或关键词搜索。'
            )

        if any(keyword in text for keyword in ['python', 'java', 'c语言', '程序设计', '编程']):
            return (
                '编程入门可先按语言方向搜索，比如 Python、Java、C语言。'
                '如果你告诉我年级、课程名或预算，我可以继续帮你细化推荐。'
            )

        if any(keyword in text for keyword in ['推荐', '书单', '教材', '找书', '买什么书']):
            return (
                '你可以告诉我专业、年级、课程名或想学的方向，我会按教材/参考书思路给你推荐。'
                '也可以直接去书籍市场搜索课程关键词看看。'
            )

        if any(keyword in text for keyword in ['发布', '卖书', '上架', '出售']):
            return (
                '发布二手书一般是：登录账号 → 进入发布页面 → 填写书名、作者、成色、价格和库存 → 上传封面 → 提交。'
                '建议把成色和是否有笔记写清楚，更容易成交。'
            )

        if any(keyword in text for keyword in ['购买流程', '怎么买', '下单', '支付', '发货']):
            return (
                '购书流程通常是：浏览书籍 → 查看详情 → 加入购物车或直接下单 → 填写收货地址 → 支付 → 等待卖家发货。'
                '下单前建议重点看成色、版本和卖家描述。'
            )

        if any(keyword in text for keyword in ['联系卖家', '咨询卖家', '卖家']):
            return (
                '如果页面提供卖家信息或订单沟通入口，你可以先确认版本、成色、是否有划线笔记，再决定是否购买。'
                '沟通时尽量一次性问清关键信息。'
            )

        if any(keyword in text for keyword in ['成色', '版本', 'isbn', '出版社']):
            return (
                '购买教材时，建议重点确认 ISBN、出版社、版本和成色。'
                '同名教材可能有不同版本，最好和课程要求对照后再下单。'
            )

        return (
            '我可以帮你推荐教材、说明购买流程、指导发布二手书。'
            '如果你愿意，可以直接告诉我你的专业、课程名或想买/想卖的书。'
        )
