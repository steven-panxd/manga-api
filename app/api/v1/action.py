from flask import g, request

from . import api_v1
from app.db import db
from app.db.model import Slide
from app.db.serializer import SlideSchema
from app.utils.enum import EmailType
from app.utils.email import send_email
from app.utils.response import Fail, Success
from app.utils.dangerous import generate_captcha_by_flag
from app.form import ValidateCaptchaForm, SendRegisterEmailForm, SendForgetPasswordEmailForm


@api_v1.route('/action/get_homepage_slide', methods=['GET'])
def get_homepage_slide():  # get the slides for home page including url, image and title
    slides = db.session.query(Slide).order_by(Slide.order).limit(5).all()
    return Success(payload={
        'slides': slides
    })


@api_v1.route('/action/send_register_email', methods=['GET'])
def send_register_email():  # send email
    form = SendRegisterEmailForm().validate_for_api()
    send_email(email_type=EmailType.REGISTER, email_address=form.email.data, username=form.username.data)
    return Success(message='Send email successfully')


@api_v1.route('/action/send_forget_password_email', methods=['GET'])
def send_forget_password_email():  # send forget password email
    form = SendForgetPasswordEmailForm().validate_for_api()
    send_email(email_type=EmailType.FORGET, email_address=form.email.data, username=g.user.username)
    return Success(message='Send email successfully')


@api_v1.route('/action/captcha/<flag>', methods=['GET'])
def get_captcha(flag):  # get a new captcha by flag
    captcha = generate_captcha_by_flag(flag)
    if not captcha:
        return Fail(message='Database Error')
    return Success(payload={
        'flag': flag,
        'captcha': captcha
    })


@api_v1.route('/action/captcha/', methods=['POST'])
def validate_captcha():  # validate a captcha
    ValidateCaptchaForm().validate_for_api()
    return Success()
