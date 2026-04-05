import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from api.auth import auth_bp
from api.users import users_bp
from api.yonghu import yonghu_bp
from api.ershoushuji import ershoushuji_bp
from api.orders import orders_bp
from api.cart import cart_bp
from api.address import address_bp
from api.shujifenlei import shujifenlei_bp
from api.news import news_bp
from api.aboutus import aboutus_bp
from api.systemintro import systemintro_bp
from api.discuss import discuss_bp
from api.storeup import storeup_bp
from api.config_api import config_bp
from api.file import file_bp
from api.common import common_bp
from api.wallet import wallet_bp
from api.condition_level_api import condition_level_bp
from api.recommend import recommend_bp
from api.chat import chat_bp
from api.college_api import college_bp
from api.major_api import major_bp
from api.statistics import statistics_bp


def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 初始化图片代理缓存
    from services.image_proxy_service import ImageProxyService
    ImageProxyService.init(app.config['UPLOAD_FOLDER'])

    CORS(app, supports_credentials=True)
    JWTManager(app)
    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(yonghu_bp, url_prefix='/api/yonghu')
    app.register_blueprint(ershoushuji_bp, url_prefix='/api/book')
    app.register_blueprint(orders_bp, url_prefix='/api/order')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(address_bp, url_prefix='/api/address')
    app.register_blueprint(shujifenlei_bp, url_prefix='/api/bookCategory')
    app.register_blueprint(news_bp, url_prefix='/api/news')
    app.register_blueprint(aboutus_bp, url_prefix='/api/aboutus')
    app.register_blueprint(systemintro_bp, url_prefix='/api/systemintro')
    app.register_blueprint(discuss_bp, url_prefix='/api/review')
    app.register_blueprint(storeup_bp, url_prefix='/api/favorite')
    app.register_blueprint(config_bp, url_prefix='/api/config')
    app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
    app.register_blueprint(file_bp, url_prefix='/api/file')
    app.register_blueprint(common_bp, url_prefix='/api')
    app.register_blueprint(condition_level_bp, url_prefix='/api/conditionLevel')
    app.register_blueprint(recommend_bp, url_prefix='/api/recommend')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(college_bp, url_prefix='/api/college')
    app.register_blueprint(major_bp, url_prefix='/api/major')
    app.register_blueprint(statistics_bp, url_prefix='/api/statistics')

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    import os
    import logging
    
    # Suppress Flask development server warnings
    os.environ['WERKZEUG_RUN_MAIN'] = os.environ.get('WERKZEUG_RUN_MAIN', 'false')
    
    # Only run migration once (not on reloader)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        from migrations.migrate import migrate
        migrate()
        print('Server starting on http://127.0.0.1:8081')

    # Reduce werkzeug logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app = create_app()
    app.run(
        host=app.config.get('SERVER_HOST', '0.0.0.0'),
        port=app.config.get('SERVER_PORT', 5000),
        debug=app.config.get('DEBUG', False),
    )
