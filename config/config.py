import os
from datetime import timedelta
import yaml

_base_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_base_dir)
_config_file = os.path.join(_base_dir, 'config.yaml')

with open(_config_file, 'r', encoding='utf-8') as f:
    _yaml_cfg = yaml.safe_load(f)


class Config:
    SECRET_KEY = _yaml_cfg.get('secret_key', 'dev')
    SQLALCHEMY_DATABASE_URI = _yaml_cfg['database']['uri']
    SQLALCHEMY_TRACK_MODIFICATIONS = _yaml_cfg['database'].get('track_modifications', False)
    JWT_SECRET_KEY = _yaml_cfg['jwt']['secret_key']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=_yaml_cfg['jwt'].get('access_token_expires', 86400))
    UPLOAD_FOLDER = os.path.join(_backend_dir, 'static', 'upload')
    MAX_CONTENT_LENGTH = _yaml_cfg['upload'].get('max_content_length', 300 * 1024 * 1024)
    DEBUG = _yaml_cfg['server'].get('debug', False)
    SERVER_HOST = _yaml_cfg['server'].get('host', '0.0.0.0')
    SERVER_PORT = _yaml_cfg['server'].get('port', 5000)

    # AI 推荐配置
    DASHSCOPE_API_KEY = _yaml_cfg.get('ai', {}).get('dashscope', {}).get('api_key', '')
    DASHSCOPE_MODEL = _yaml_cfg.get('ai', {}).get('dashscope', {}).get('model', 'qwen-turbo')
    DASHSCOPE_BASE_URL = _yaml_cfg.get('ai', {}).get('dashscope', {}).get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    DASHSCOPE_MAX_TOKENS = _yaml_cfg.get('ai', {}).get('dashscope', {}).get('max_tokens', 200)
    DASHSCOPE_TEMPERATURE = _yaml_cfg.get('ai', {}).get('dashscope', {}).get('temperature', 0.8)
    CACHE_TTL = _yaml_cfg.get('ai', {}).get('dashscope', {}).get('cache_ttl', 600)

    _alipay_cfg = _yaml_cfg.get('alipay', {})
    ALIPAY_ENABLED = str(os.getenv('ALIPAY_ENABLED', _alipay_cfg.get('enabled', False))).lower() in ('1', 'true', 'yes')
    ALIPAY_GATEWAY = os.getenv('ALIPAY_GATEWAY', _alipay_cfg.get('gateway', 'https://openapi.alipay.com/gateway.do'))
    ALIPAY_APP_ID = os.getenv('ALIPAY_APP_ID', _alipay_cfg.get('app_id', ''))
    ALIPAY_APP_PRIVATE_KEY = os.getenv('ALIPAY_APP_PRIVATE_KEY', _alipay_cfg.get('app_private_key', ''))
    ALIPAY_APP_PRIVATE_KEY_PATH = os.getenv('ALIPAY_APP_PRIVATE_KEY_PATH', _alipay_cfg.get('app_private_key_path', ''))
    ALIPAY_PUBLIC_KEY = os.getenv('ALIPAY_PUBLIC_KEY', _alipay_cfg.get('alipay_public_key', ''))
    ALIPAY_PUBLIC_KEY_PATH = os.getenv('ALIPAY_PUBLIC_KEY_PATH', _alipay_cfg.get('alipay_public_key_path', ''))
    ALIPAY_NOTIFY_URL = os.getenv('ALIPAY_NOTIFY_URL', _alipay_cfg.get('notify_url', ''))
    ALIPAY_RETURN_URL = os.getenv('ALIPAY_RETURN_URL', _alipay_cfg.get('return_url', ''))
    ALIPAY_TIMEOUT_EXPRESS = os.getenv('ALIPAY_TIMEOUT_EXPRESS', _alipay_cfg.get('timeout_express', '30m'))
    ALIPAY_MOCK_PAY = str(os.getenv('ALIPAY_MOCK_PAY', _alipay_cfg.get('mock_pay', False))).lower() in ('1', 'true', 'yes')
