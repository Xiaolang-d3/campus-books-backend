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
    # 兼容数据库中存储的 "upload/xxx.jpg" 格式
    if filename.startswith('upload/'):
        filename = filename[len('upload/'):]
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
