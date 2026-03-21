import os

from flask import Blueprint, request, send_from_directory, current_app
from common import R_ok, R_error
from services.file_service import FileService

file_bp = Blueprint('file', __name__)


@file_bp.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    result, err = FileService.upload(f, current_app.config['UPLOAD_FOLDER'])
    if err:
        return R_error(err)
    return R_ok(data=result)


@file_bp.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    normalized = filename.replace('\\', '/').lstrip('/')

    # 兼容数据库中存储的 "upload/xxx.jpg"、"/upload/xxx.jpg"、"static/upload/xxx.jpg" 格式
    if normalized.startswith('static/'):
        normalized = normalized[len('static/'):]
    if normalized.startswith('upload/'):
        normalized = normalized[len('upload/'):]

    primary_dir = current_app.config['UPLOAD_FOLDER']
    fallback_dir = os.path.abspath(
        os.path.join(current_app.root_path, '..', 'static', 'upload')
    )

    if os.path.exists(os.path.join(primary_dir, normalized)):
        return send_from_directory(primary_dir, normalized)

    if os.path.exists(os.path.join(fallback_dir, normalized)):
        return send_from_directory(fallback_dir, normalized)

    return R_error('文件不存在')
