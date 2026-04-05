import os
import re

from flask import Blueprint, request, send_from_directory, send_file, current_app, redirect
from common import R_ok, R_error
from services.file_service import FileService
from services.image_proxy_service import ImageProxyService

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


@file_bp.route('/image-proxy', methods=['GET'])
def image_proxy():
    """
    图片代理接口：将外部图片缓存到本地后返回
    GET /api/file/image-proxy?url=https://xxx.jpg
    """
    url = request.args.get('url', '').strip()
    if not url or not re.match(r'^https?://', url, re.IGNORECASE):
        return R_error('无效的图片 URL')

    # 先查缓存
    cached = ImageProxyService.get_cached_path(url)
    if cached:
        return send_file(cached)

    # 缓存不存在，下载
    cached = ImageProxyService.download_and_cache(url)
    if cached:
        return send_file(cached)

    # 下载失败，302 跳转到原始 URL 让浏览器自行尝试
    return redirect(url)
