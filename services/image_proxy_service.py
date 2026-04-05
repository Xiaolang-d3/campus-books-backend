"""
图片代理与缓存服务
外部图片首次访问时下载到本地缓存，后续直接返回本地文件
"""
import hashlib
import os
import time
import threading

import requests


class ImageProxyService:
    CACHE_DIR = None
    _lock = threading.Lock()
    # 请求超时（秒）
    TIMEOUT = 8
    # 缓存有效期（秒），7 天
    CACHE_TTL = 7 * 24 * 3600

    @classmethod
    def init(cls, upload_folder):
        cls.CACHE_DIR = os.path.join(upload_folder, '_cover_cache')
        os.makedirs(cls.CACHE_DIR, exist_ok=True)

    @classmethod
    def _url_to_filename(cls, url):
        """将 URL 哈希为本地文件名，保留原始扩展名"""
        ext = ''
        path_part = url.split('?')[0]
        if '.' in path_part.split('/')[-1]:
            ext = '.' + path_part.split('/')[-1].rsplit('.', 1)[-1]
            # 只保留合法图片扩展名
            if ext.lower() not in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'):
                ext = '.jpg'
        else:
            ext = '.jpg'
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return url_hash + ext

    @classmethod
    def get_cached_path(cls, url):
        """
        获取图片的本地缓存路径。
        如果缓存不存在或已过期，返回 None。
        """
        if not cls.CACHE_DIR:
            return None
        filename = cls._url_to_filename(url)
        filepath = os.path.join(cls.CACHE_DIR, filename)
        if os.path.exists(filepath):
            # 检查缓存是否过期
            age = time.time() - os.path.getmtime(filepath)
            if age < cls.CACHE_TTL:
                return filepath
        return None

    @classmethod
    def download_and_cache(cls, url):
        """
        下载外部图片并缓存到本地，返回本地文件路径。
        失败时返回 None。
        """
        if not cls.CACHE_DIR:
            return None
        filename = cls._url_to_filename(url)
        filepath = os.path.join(cls.CACHE_DIR, filename)

        with cls._lock:
            # 双重检查，可能在等锁的过程中其他线程已完成下载
            if os.path.exists(filepath):
                age = time.time() - os.path.getmtime(filepath)
                if age < cls.CACHE_TTL:
                    return filepath

            try:
                resp = requests.get(
                    url,
                    timeout=cls.TIMEOUT,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; CampusBooks/1.0)',
                        'Accept': 'image/*',
                    },
                    stream=True,
                )
                if resp.status_code != 200:
                    return None

                content_type = resp.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    return None

                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                return filepath
            except Exception as e:
                print(f'[ImageProxy] 下载失败: {url} -> {e}')
                # 清理可能写了一半的文件
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass
                return None
