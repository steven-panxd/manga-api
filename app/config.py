class BaseConfig:
    SECRET_KEY = '\x02\xe6et\xe8\xfc\x0e\xdcXG|W\xa5\x1a\x82\xa6\x03\x95{\x9f`\xfc\xf5\xd9'
    TOKEN_EXPIRE_TIME = 7200  # login token will expire in 2 hours
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CAPTCHA_SAVE_FORMAT = 'CAPTCHA_{flag}'
    REGISTER_EMAIL_CODE_SAVE_FORMAT = 'REGISTER_EMAIL_CODE_{email}'
    FORGET_PASSWORD_EMAIL_CODE_SAVE_FORMAT = 'FORGET_PASSWORD_EMAIL_CODE_{email}'
    USER_LIKE_POST_IDS_SAVE_FORMAT = 'USER_{user_id}_LIKE_POST_IDS'
    CAPTCHA_EXPIRE_TIME = 600
    EMAIL_CODE_EXPIRE_TIME = 600
    MAIL_SERVER = 'smtp.test.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'admin@admin.com'
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = 'Manga<admin@admin.com>'
    POSTS_NUMBER_PER_PAGE = 10
    COMMENTS_NUMBER_PER_PAGE = 10


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/manga?charset=utf8mb4"
    REDIS_URL = "redis://localhost:6379/0"


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    REDIS_URL = "redis://localhost:6379/1"


class ProductionConfig(BaseConfig):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/manga?charset=utf8mb4"
    REDIS_URL = "redis://localhost:6379/0"
