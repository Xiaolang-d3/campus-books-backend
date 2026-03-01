import os
import sys

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from api.auth import auth_bp
from api.users import users_bp
from api.yonghu import yonghu_bp
from api.shangjia import shangjia_bp
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


def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    CORS(app, supports_credentials=True)
    JWTManager(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(yonghu_bp, url_prefix='/api/yonghu')
    app.register_blueprint(shangjia_bp, url_prefix='/api/shangjia')
    app.register_blueprint(ershoushuji_bp, url_prefix='/api/ershoushuji')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(address_bp, url_prefix='/api/address')
    app.register_blueprint(shujifenlei_bp, url_prefix='/api/shujifenlei')
    app.register_blueprint(news_bp, url_prefix='/api/news')
    app.register_blueprint(aboutus_bp, url_prefix='/api/aboutus')
    app.register_blueprint(systemintro_bp, url_prefix='/api/systemintro')
    app.register_blueprint(discuss_bp, url_prefix='/api/discussershoushuji')
    app.register_blueprint(storeup_bp, url_prefix='/api/storeup')
    app.register_blueprint(config_bp, url_prefix='/api/config')
    app.register_blueprint(file_bp, url_prefix='/api/file')
    app.register_blueprint(common_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    from migrations.migrate import migrate
    migrate()

    app = create_app()
    app.run(
        host=app.config.get('SERVER_HOST', '0.0.0.0'),
        port=app.config.get('SERVER_PORT', 5000),
        debug=app.config.get('DEBUG', False),
    )
