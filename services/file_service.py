import os
import time


class FileService:
    @staticmethod
    def upload(file, upload_dir):
        if not file or file.filename == '':
            return None, '没有文件' if not file else '文件名为空'
        ext = os.path.splitext(file.filename)[1]
        filename = str(int(time.time() * 1000)) + ext
        file.save(os.path.join(upload_dir, filename))
        return {'file': filename}, None
