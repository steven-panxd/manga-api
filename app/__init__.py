from flask import Flask
from flask.cli import ScriptInfo

from flask_redis import FlaskRedis
from flask_migrate import Migrate
from captcha.image import ImageCaptcha
from itsdangerous import TimedJSONWebSignatureSerializer

from app.db import db, ma
from app.db.model import Identity
from app.libs.mail import Mail
from app.utils.enum import Config
from app.utils.response import PageNotFound, ServerError

mail = Mail()
image_captcha = None
jwt_serializer = None
redis_client = FlaskRedis()


def page_not_found(e):
    return PageNotFound()


def server_error(e):
    return ServerError()


def create_app(config_type=None):
    app = Flask(__name__)

    load_config(app, config_type)

    db.init_app(app)
    db.create_all(app=app)
    ma.init_app(app)
    mail.init_app(app)
    Migrate(app, db)
    init_database(app)

    global redis_client
    redis_client.init_app(app)

    global image_captcha
    image_captcha = ImageCaptcha()

    global jwt_serializer
    jwt_serializer = TimedJSONWebSignatureSerializer(
        secret_key=app.config.get('SECRET_KEY'),
        expires_in=app.config.get('TOKEN_EXPIRE_TIME')
    )

    app.register_error_handler(404, page_not_found)
    register_blueprint(app)
    return app


def init_database(app):
    with app.app_context():
        Identity.init_identities()


def load_config(app, config_type=None):
    if (config_type is not None) and (not isinstance(config_type, ScriptInfo)):
        app.config.from_object(Config.get(config_type))
    else:
        if app.config['ENV'] == 'development':
            app.config.from_object(Config.get('development'))
        elif app.config['ENV'] == 'testing':
            app.config.from_object(Config.get('testing'))
        else:
            app.config.from_object(Config.get('production'))


def register_blueprint(app):
    from .api.v1 import api_v1
    app.register_blueprint(api_v1)
    from .api.mask import api_mask
    app.register_blueprint(api_mask)
