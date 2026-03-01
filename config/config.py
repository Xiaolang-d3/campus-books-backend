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
