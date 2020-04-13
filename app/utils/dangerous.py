import random
import base64

from itsdangerous import SignatureExpired, BadData
from redis import RedisError
from io import BytesIO

from flask import current_app
from werkzeug.security import generate_password_hash as g_password_hash, check_password_hash as c_password_hash

from app.utils.enum import EmailType
from app.utils.response import Fail, ServerError

__all__ = (
    'generate_captcha_by_flag',
    'check_captcha_by_flag',
    'generate_and_save_email_code',
    'check_email_code',
    'generate_password_hash',
    'check_password_hash',
    'generate_login_token',
    'check_login_token'
)


def generate_login_token(user_id):
    from app import jwt_serializer
    data = jwt_serializer.dumps({
        "user_id": user_id
    })
    return data


def check_login_token(token):
    from app import jwt_serializer
    try:
        payload = jwt_serializer.loads(token)
    except (SignatureExpired, BadData, UnicodeEncodeError):
        return False
    return payload


def generate_captcha_by_flag(flag):
    data = generate_captcha()
    if not save_captcha(flag, data.get('code')):
        raise ServerError(message='Database error, please try it later')
    return data.get('image_data')


def generate_captcha():
    code = str(random.randint(1000, 9999))
    from app import image_captcha
    image = image_captcha.generate_image(code)
    bytes_io = BytesIO()  # byte buffered (缓存器)
    image.save(bytes_io, format('JPEG'))
    image_data = base64.b64encode(bytes_io.getvalue())  # byte data
    image_data = image_data.decode('utf-8')  # string data
    image_data = 'data:image/jpeg;base64,' + image_data  # add prefix
    return {
        'code': code,
        'image_data': image_data
    }


def save_captcha(flag, code):
    key_format = current_app.config.get('CAPTCHA_SAVE_FORMAT')
    key = key_format.format(flag=flag)
    expire_time = current_app.config.get('CAPTCHA_EXPIRE_TIME')
    try:
        from app import redis_client
        redis_client.set(key, code, ex=expire_time)
    except RedisError:
        raise ServerError(message='Database error, please try it later')
    return True


def check_captcha_by_flag(input_captcha, flag):
    raw_captcha = get_captcha(flag)
    if not raw_captcha:
        raise Fail(message='Captcha expired')
    if not raw_captcha == input_captcha:
        return False
    delete_captcha_by_flag(flag)
    return True


def get_captcha(flag):
    key_format = current_app.config.get('CAPTCHA_SAVE_FORMAT')
    key = key_format.format(flag=flag)
    try:
        from app import redis_client
        code = redis_client.get(key)
    except RedisError:
        raise ServerError(message='Database error, please try it later')
    if not code:
        raise Fail(message='Captcha expired')
    return code.decode('utf-8')


def delete_captcha_by_flag(flag):
    key_format = current_app.config.get('CAPTCHA_SAVE_FORMAT')
    key = key_format.format(flag=flag)
    try:
        from app import redis_client
        redis_client.delete(key)
    except RedisError:
        pass


def generate_and_save_email_code(email_address, email_type):
    """
    return a dict contains code and expire time (in seconds)
    """
    code = str(random.randint(1000, 9999))
    expire_time = save_email_code(email_address, code, email_type)
    if not expire_time:
        raise ServerError(message='Database error, please try it later')
    return {
        'code': code,
        'expire_time': expire_time
    }


def save_email_code(email, code, email_type):
    if email_type == EmailType.REGISTER:
        key_format = current_app.config.get('REGISTER_EMAIL_CODE_SAVE_FORMAT')
    elif email_type == EmailType.FORGET:
        key_format = current_app.config.get('FORGET_PASSWORD_EMAIL_CODE_SAVE_FORMAT')
    else:
        raise ServerError('Email type error')
    key = key_format.format(email=email)
    expire_time = current_app.config.get('EMAIL_CODE_EXPIRE_TIME')
    try:
        from app import redis_client
        redis_client.set(key, code, ex=expire_time)
    except RedisError:
        raise ServerError(message='Database error, please try it later')
    return expire_time


def check_email_code(input_code, email, email_type):
    raw_code = get_email_code(email, email_type)
    if not raw_code:
        return False
    if not raw_code == input_code:
        return False
    delete_email_code_by_email(email, email_type)
    return True


def get_email_code(email, email_type):
    if email_type == EmailType.REGISTER:
        key_format = current_app.config.get('REGISTER_EMAIL_CODE_SAVE_FORMAT')
    elif email_type == EmailType.FORGET:
        key_format = current_app.config.get('FORGET_PASSWORD_EMAIL_CODE_SAVE_FORMAT')
    else:
        raise ServerError('Email type error')
    key = key_format.format(email=email)
    try:
        from app import redis_client
        code = redis_client.get(key)
    except RedisError:
        raise ServerError(message='Database error, please try it later')
    if not code:
        raise Fail(message='Email code expired')
    return code.decode('utf-8')


def delete_email_code_by_email(email, email_type):
    if email_type == EmailType.REGISTER:
        key_format = current_app.config.get('REGISTER_EMAIL_CODE_SAVE_FORMAT')
    elif email_type == EmailType.FORGET:
        key_format = current_app.config.get('FORGET_PASSWORD_EMAIL_CODE_SAVE_FORMAT')
    else:
        raise ServerError('Email type error')
    key = key_format.format(email=email)
    try:
        from app import redis_client
        redis_client.delete(key)
    except RedisError:
        pass


def generate_password_hash(raw_password):
    return g_password_hash(raw_password)


def check_password_hash(password_hash, password):
    return c_password_hash(password_hash, password)
