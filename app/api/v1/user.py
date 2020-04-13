from flask import g, request

from . import api_v1
from app.db.model import db, User
from app.form import RegisterForm, ForgetPasswordForm, ResetPasswordForm, ModifyUserForm
from app.utils.response import Success, Fail
from app.utils.decoration import login_required, identity_required
from app.utils.enum import Identity


@api_v1.route('/user', methods=['POST'])
def register():  # register
    form = RegisterForm().validate_for_api()
    with db.auto_commit():
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.identity_id = 1
        user.password = form.password.data
        db.session.add(user)
    return Success(message='Successfully registered')


@api_v1.route('/user', methods=['GET'])
@login_required
def get_user():  # get self information
    return Success(payload={
        'user': g.user
    })


@api_v1.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_another_user(user_id):  # get another user information by user id
    user = db.session.query(User).filter(User.id == user_id).first_or_404()
    return Success(payload={
        'user': user
    })


@api_v1.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
@identity_required(Identity.ADMINISTRATOR)
def delete_user(user_id):  # delete user by user id
    user = db.session.query(User).filter(User.id == user_id).first_or_404()
    with db.auto_commit():
        user.is_deleted = 1
    return Success()


@api_v1.route('/user/password/forget', methods=['PUT'])
def forget_user_password():  # forget password
    form = ForgetPasswordForm().validate_for_api()
    with db.auto_commit():
        g.user.password = form.password.data
    return Success('Reset password successfully')


@api_v1.route('/user/password/reset', methods=['PUT'])
@login_required
def modify_user_password():  # modify self password
    form = ResetPasswordForm().validate_for_api()
    with db.auto_commit():
        g.user.password = form.new_password
    return Success('Reset password successfully')


@api_v1.route('/user', methods=['PATCH'])
@login_required
def modify_user():  # modify self information
    form = ModifyUserForm().validate_for_api()
    if (form.bio.data is not None) or (form.avatar.data is not None):
        with db.auto_commit():
            if form.bio.data is not None:
                g.user.bio = form.bio.data
            if form.avatar.data is not None:
                g.user.avatar = form.avatar.data
    else:
        return Fail(message='Invalid params')
    return Success('Information modified successfully')
