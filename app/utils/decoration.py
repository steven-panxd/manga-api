from functools import wraps

from flask import request, g

from app.db.model import db, User
from app.utils.dangerous import check_login_token
from app.utils.response import AuthError


__all__ = (
    'login_required',
    'identity_required'
)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('ACCESS-TOKEN')
        if not token:
            raise AuthError()
        token_payload = check_login_token(token)
        if not token_payload:
            raise AuthError()
        user = db.session.query(User).filter(User.id == token_payload.get('user_id')).first()
        if not user:
            raise AuthError()
        g.user = user
        return func(*args, **kwargs)
    return wrapper


def identity_required(identity):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not g.user:
                raise AuthError()
            if g.user.identity.weight < identity.value:
                raise AuthError(message='You are not allowed to do it')
            return func(*args, **kwargs)
        return wrapper
    return decorate
