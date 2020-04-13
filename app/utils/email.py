from flask_mail import Message, current_app

from app import mail
from app.utils.enum import EmailType
from app.utils.response import ServerError
from app.utils.dangerous import generate_and_save_email_code

__all__ = (
    'send_email',
)


def send_email(email_address, email_type, **kwargs):
    if email_type == EmailType.REGISTER:
        return send_register_email(email_address, **kwargs)
    elif email_type == EmailType.FORGET:
        return send_forget_password_email(email_address, **kwargs)
    elif email_type == EmailType.NOTIFY:
        pass
    else:
        return False


def send_register_email(email_address, username):
    data = generate_and_save_email_code(email_address, EmailType.REGISTER)
    html = """
    <html>
        <p>
            Hello {username}, your code is {code} which will expire in {expire_time} seconds
        </p>
    </html>
    """.format(username=username, code=data.get('code'), expire_time=data.get('expire_time'))
    msg = Message(
        subject='Welcome to manga',
        html=html,
        recipients=[email_address]
    )
    try:
        mail.async_send(msg, app=current_app._get_current_object())
    except Exception:
        raise ServerError(message='Mail server error, please try it later')


def send_forget_password_email(email_address, username):
    data = generate_and_save_email_code(email_address, EmailType.FORGET)
    html = """
        <html>
            <p>
                Hello {username}, your code is {code} which will expire in {expire_time} seconds
            </p>
        </html>
        """.format(username=username, code=data.get('code'), expire_time=data.get('expire_time'))
    msg = Message(
        subject='Forget Password',
        html=html,
        recipients=[email_address]
    )
    try:
        mail.async_send(msg, app=current_app._get_current_object())
    except Exception:
        raise ServerError(message='Mail server error, please try it later')

