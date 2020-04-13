from flask import request, g
from wtforms import Form, StringField, ValidationError, IntegerField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, Email, URL

from app.db.model import db, User, Category, Comment
from app.utils.enum import EmailType, PostOrderType, CommentOrderType
from app.utils.response import ValidationError as _ValidationError
from app.utils.dangerous import check_captcha_by_flag, check_email_code, check_password_hash, check_login_token


class BaseForm(Form):
    def __init__(self, dict_data=None):
        data = request.get_json(silent=True)
        if not data:
            data = request.args.to_dict()
        if not data and dict_data is not None:
            data = dict_data
        super(BaseForm, self).__init__(data=data)

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()
        if not valid:
            error_key = list(self.errors.keys())[0]
            error_message = self.errors.get(error_key)[0]
            raise _ValidationError(payload={
                'error_field': error_key,
                'error_message': error_message
            })
        return self


class RegisterForm(BaseForm):
    username = StringField('username', validators=[
        DataRequired(message='Please input username'),
        Length(min=6, max=15, message='The length of username should be 6-12')
    ])
    password = StringField('password', validators=[
        DataRequired(message='Please input password'),
        Length(min=6, max=32, message='The length of password should be 6-32')
    ])
    password2 = StringField('password2', validators=[
        DataRequired(message='Please repeat password'),
        EqualTo('password', message='Two inputs of password are not equal')
    ])
    email = StringField('email', validators=[
        DataRequired(message='Please input email'),
        Email(message='The email is not valid')
    ])
    code = StringField('code', validators=[
        DataRequired(message='Please input the email code'),
        Length(min=4, max=4, message='Email code validation failed')
    ])

    def validate_username(self, field):
        if db.session.query(User).filter(User.username == field.data).first():
            raise ValidationError(message='Duplicated registration for username')
        return True

    def validate_email(self, field):
        if db.session.query(User).filter(User.email == field.data).first():
            raise ValidationError(message='Duplicated registration for email address')
        return True

    def validate_code(self, field):
        if not check_email_code(field.data, self.email.data, EmailType.REGISTER):
            raise ValidationError(message='Email code error')
        return True


class ValidateCaptchaForm(BaseForm):
    flag = StringField('flag', validators=[
        DataRequired(message='Captcha validation failed'),
    ])
    captcha = StringField('captcha', validators=[
        DataRequired(message='Please input captcha'),
        Length(min=4, max=4, message='Captcha error')
    ])

    def validate_captcha(self, field):
        if not check_captcha_by_flag(field.data, self.flag.data):
            raise ValidationError('Captcha error')
        return True


class SendRegisterEmailForm(ValidateCaptchaForm):
    username = StringField('username', validators=[
        DataRequired(message='Please input username'),
        Length(min=6, max=15, message='The length of username should be 6-12'),
        Regexp(r'[A-Za-z0-9_.@]+', message='Do not use special characters except ._@')
    ])
    email = StringField('email', validators=[
        DataRequired(message='Please input email'),
        Email(message='The email is not valid')
    ])

    def validate_username(self, field):
        if db.session.query(User).filter(User.username == field.data).first():
            raise ValidationError(message='Duplicated registration of the username')
        return True

    def validate_email(self, field):
        if db.session.query(User).filter(User.email == field.data).first():
            raise ValidationError(message='Duplicated registration of the email')
        return True


class LoginForm(BaseForm):
    username = StringField('username', validators=[
        DataRequired(message='Please input username or email address')
    ])
    password = StringField('password', validators=[
        DataRequired(message='Please input password'),
        Length(min=6, max=32, message='The length of password should be 6-32')
    ])

    def validate_username(self, field):
        user = db.session.query(User).filter(User.username == field.data).first()
        if not user:
            user = db.session.query(User).filter(User.email == field.data).first()
        if not user:
            raise ValidationError(message='Username or password is wrong')
        g.user = user
        return True


class CheckTokenForm(BaseForm):
    token = StringField('token', validators=[
        DataRequired(message='Params invalid')
    ])

    def validate_token(self, field):
        if not check_login_token(field.data):
            raise ValidationError('Token is invalid')
        return True


class CreatePostForm(BaseForm):
    title = StringField('title', validators=[
        DataRequired(message='Please input title'),
        Length(min=1, max=100, message='The length of title must be shorter than 100 characters')
    ])
    author = StringField('author', validators=[
        DataRequired(message='Please input author'),
        Length(min=1, max=50, message='The length of author\' name must be shorter than 50 characters')
    ])
    cover_image = StringField('cover_image', validators=[
        DataRequired(message='Please input url of cover image'),
        Length(min=1, max=128, message='The length of the url must be shorter than 128 characters')
    ])
    content = StringField('content', validators=[
        DataRequired(message='Please input content'),
        Length(min=1, max=5000, message='The length of content must be shorter than 5000 characters')
    ])
    category = IntegerField('category', validators=[
        DataRequired(message='Please choose a category'),
    ])

    def validate_category(self, field):
        category = db.session.query(Category).filter(Category.id == field.data).first()
        if not category:
            raise ValidationError('This category is not valid')
        self.category.data = category
        return True


class GetPostsForm(BaseForm):
    page = IntegerField('page', default=1)
    cid = IntegerField('cid', default=0)
    uid = IntegerField('uid', default=0)
    oby = StringField('oby', default='ADD_TIME_DEC')

    def validate_page(self, field):
        try:
            self.page.data = int(field.data)
        except TypeError:
            raise ValidationError(message='Invalid page number')
        return True

    def validate_cid(self, field):
        try:
            self.cid.data = int(field.data)
        except TypeError:
            raise ValidationError(message='Invalid category id')
        return True

    def validate_uid(self, field):
        try:
            self.uid.data = int(field.data)
        except TypeError:
            raise ValidationError(message='Invalid user id')
        return True

    def validate_oby(self, field):
        if not PostOrderType.contains(field.data.upper()):
            raise ValidationError(message='Invalid order param')
        self.oby.data = field.data.upper()
        return True


class SendForgetPasswordEmailForm(ValidateCaptchaForm):
    email = StringField('email', validators=[
        DataRequired(message='Please input email used for registration'),
        Email(message='This email is invalid')
    ])

    def validate_email(self, field):
        user = db.session.query(User).filter(User.email == field.data).first()
        if not user:
            raise ValidationError(message='This email has not been registered')
        g.user = user
        return True


class ForgetPasswordForm(BaseForm):
    email = StringField('email', validators=[
        DataRequired(message='Please input email used for registration'),
        Email(message='This email is invalid')
    ])
    password = StringField('password', validators=[
        DataRequired(message='Please input password'),
        Length(min=6, max=32, message='The length of password should be 6-32')
    ])
    password2 = StringField('password2', validators=[
        DataRequired(message='Please repeat password'),
        EqualTo('password', message='Two inputs of password are not equal')
    ])
    code = StringField('code', validators=[
        DataRequired(message='Please input the email code'),
        Length(min=4, max=4, message='Email code validation failed')
    ])

    def validate_email(self, field):
        user = db.session.query(User).filter(User.email == field.data).first()
        if not user:
            raise ValidationError(message='This email has not been registered')
        g.user = user
        return True

    def validate_code(self, field):
        if not check_email_code(field.data, self.email.data, EmailType.FORGET):
            raise ValidationError(message='Email code error')
        return True


class ResetPasswordForm(BaseForm):
    old_password = StringField('old_password', validators=[
        DataRequired(message='Please input original password'),
        Length(min=6, max=32, message='The length of password should be 6-32')
    ])
    new_password = StringField('new_password', validators=[
        DataRequired(message='Please input new password'),
        Length(min=6, max=32, message='The length of new password should be 6-32')
    ])
    new_password2 = StringField('new_password2', validators=[
        DataRequired(message='Please repeat password'),
        EqualTo('password', message='Two inputs of new password are not equal')
    ])

    def validate_old_password(self, field):
        if not check_password_hash(g.user.password, field.data):
            raise ValidationError(message='The original password is wrong')
        return True


class ModifyUserForm(BaseForm):
    bio = StringField(default=None, validators=[
        Length(max=100, message='The bio should be shorter than 100 characters')
    ])
    avatar = StringField(default=None, validators=[
        URL(message='The url of avatar is invalid'),
        Length(max=128, message='The link of avatar is too long')
    ])


class ModifyPostForm(BaseForm):
    title = StringField('title', validators=[
        Length(min=1, max=100, message='The length of title must be shorter than 100 characters')
    ])
    content = StringField('content', validators=[
        Length(min=1, max=5000, message='The length of content must be shorter than 5000 characters')
    ])
    category = IntegerField('category_id')

    def validate_category(self, field):
        if field.data:
            category = db.session.query(Category).filter(Category.id == field.data).first()
            if not category:
                raise ValidationError('This category is not valid')
            self.category.data = category
        return True


class GetPostCommentsForm(BaseForm):
    page = IntegerField('page', default=1)
    oby = StringField('oby', default='ADD_TIME_DEC')

    def validate_page(self, field):
        try:
            self.page.data = int(field.data)
        except TypeError:
            raise ValidationError(message='Invalid page number')
        return True

    def validate_oby(self, field):
        if not CommentOrderType.contains(field.data.upper()):
            raise ValidationError(message='Invalid order param')
        self.oby.data = field.data.upper()
        return True


class CreatePostCommentForm(BaseForm):
    content = StringField('content', validators=[
        DataRequired(message='Comment can not be blank'),
        Length(min=1, max=300, message='The length of the comment should be 1-300 characters')
    ])


class ReplyPostCommentForm(CreatePostCommentForm):
    parent = IntegerField('parent', validators=[
        DataRequired(message='Invalid comment id')
    ])

    def validate_parent(self, field):
        comment = db.session.query(Comment).filter(Comment.id == field.data).first()
        if not comment:
            raise ValidationError(message='Can not find comment')
        self.parent.data = comment
        return True


class ModifyPostCommentForm(BaseForm):
    content = StringField('content', validators=[
        Length(min=1, max=300, message='The length of the comment should be 1-300 characters')
    ])
    parent = IntegerField('parent')

    def validate_parent(self, field):
        if not field.data:
            comment = db.session.query(Comment).filter(Comment.id == field.data).first()
            if not comment:
                raise ValidationError(message='Can not find comment')
            self.parent.data = comment
        return True
