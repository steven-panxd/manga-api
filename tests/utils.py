from app.db import db
from app.db.model import User
from app.utils.enum import EmailType
from app.utils.dangerous import generate_and_save_email_code


def get_register_email_code(email_address):
    data = generate_and_save_email_code(email_address, EmailType.REGISTER)
    return data.get('code')


def set_user(username, email, password):
    with db.auto_commit():
        user = User()
        user.username = username
        user.password = password
        user.email = email
        user.identity_id = 1
        db.session.add(user)

