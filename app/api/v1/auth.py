from flask import g

from . import api_v1
from app.form import LoginForm, CheckTokenForm
from app.utils.response import Success, Fail
from app.utils.dangerous import generate_login_token, check_password_hash


@api_v1.route('/auth/token', methods=['POST'])
def login():  # get a new token
    form = LoginForm().validate_for_api()
    if not check_password_hash(g.user.password, form.password.data):
        raise Fail(message='Username or password is wrong')
    token = generate_login_token(g.user.id)
    return Success(payload={
        "token": token.decode('utf-8')
    })


@api_v1.route('/auth/token', methods=['GET'])
def check_login():  # check a token
    form = CheckTokenForm().validate_for_api()
    return Success(payload={
        "token": form.token.data
    })
