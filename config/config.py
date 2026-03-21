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
