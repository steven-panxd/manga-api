from datetime import datetime

from flask import current_app, g

from app.db import db
from app.utils.enum import Identity as IdentityEnum
from app.utils.dangerous import generate_password_hash
from app.utils.response import Fail


class BaseModel(db.Model):
    __abstract__ = True

    add_time = db.Column('add_time', db.DateTime, nullable=False, default=datetime.utcnow())
    is_deleted = db.Column('is_deleted', db.SmallInteger, nullable=False, default=0)


class Slide(BaseModel):
    __tablename__ = "slide"

    id = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('title', db.String(64), nullable=False, default='')
    url = db.Column('url', db.String(128), nullable=False)
    order = db.Column('order', db.Integer, nullable=False, default=0)
    image = db.Column('image', db.String(128), nullable=False)

    def __repr__(self):
        return '<Slide %s>' % self.title


class Identity(BaseModel):
    __tablename__ = 'identity'

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(64), nullable=False, unique=True, default='')
    weight = db.Column('weight', db.Integer, nullable=False, default=0)

    @staticmethod
    def init_identities():
        with db.auto_commit():
            for item in IdentityEnum.items():
                identity = db.session.query(Identity).filter(Identity.name == item.get('key')).first()
                if not identity:
                    new_identity = Identity()
                    new_identity.name = item.get('key')
                    new_identity.weight = item.get('value')
                    db.session.add(new_identity)

    def __repr__(self):
        return '<Identity %s>' % self.name


class User(BaseModel):
    __tablename__ = "user"

    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(128), nullable=False, unique=True)
    email = db.Column('email', db.String(128), nullable=False, unique=True)
    password_hash = db.Column('password_hash', db.String(256), nullable=False)
    bio = db.Column('bio', db.String(256), nullable=False, default='')
    avatar = db.Column('avatar', db.String(128), nullable=False, default='')
    coin_num_raw = db.Column('coin_num_raw', db.Integer, nullable=False, default=100)
    post_num = db.Column('post_num', db.Integer, nullable=False, default=0)

    identity_id = db.Column(db.Integer, db.ForeignKey('identity.id'))
    identity = db.relationship('Identity', backref=db.backref('users', lazy='dynamic'))

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    @property
    def coin_num(self):
        return self.coin_num_raw / 100

    def modify_coin(self, value):
        if self.coin_num_raw + value < 100:
            raise Fail(message="Your coin is not enough")
        self.coin_num_raw += value

    def check_like(self, post):
        key_format = current_app.config.get('USER_LIKE_POST_IDS_SAVE_FORMAT')
        key = key_format.format(user_id=self.id)
        from app import redis_client
        return redis_client.sismember(key, post.id)

    def unlike(self, post):
        with db.auto_commit():
            post.like_num -= 1
        key_format = current_app.config.get('USER_LIKE_POST_IDS_SAVE_FORMAT')
        key = key_format.format(user_id=self.id)
        from app import redis_client
        redis_client.srem(key, [post.id])

    def like(self, post):
        with db.auto_commit():
            post.like_num += 1
        key_format = current_app.config.get('USER_LIKE_POST_IDS_SAVE_FORMAT')
        key = key_format.format(user_id=self.id)
        from app import redis_client
        redis_client.sadd(key, [post.id])

    def __repr__(self):
        return '<User %s>' % self.username


class Category(BaseModel):
    __tablename__ = 'category'

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(64), nullable=False, default='')
    index = db.Column('index', db.Integer, nullable=False, default=0)

    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    parent = db.relationship('Category', backref=db.backref('sub_category'), remote_side=[id])

    def __repr__(self):
        return '<Category %s>' % self.name


class Post(BaseModel):
    __tablename__ = "post"

    id = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('title', db.String(256), nullable=False)
    author = db.Column('author', db.String(64), nullable=False, default='')
    content = db.Column('content', db.Text, nullable=False, default='')
    like_num = db.Column('like_num', db.Integer, nullable=False, default=0)
    view_num = db.Column('view_num', db.Integer, nullable=False, default=0)
    coin_num = db.Column('coin_num', db.Integer, nullable=False, default=0)
    collected_num = db.Column('collected_num', db.Integer, nullable=False, default=0)
    cover_image = db.Column('cover_image', db.String(128), nullable=False, default='')
    comment_num = db.Column('comment_num', db.Integer, nullable=False, default=0)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'))

    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploader = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))

    @property
    def like(self):
        return g.user.check_like(self) if g.user else False

    def __repr__(self):
        return '<Post %s>' % self.title


class Comment(BaseModel):
    __tablename__ = "comment"

    id = db.Column('id', db.Integer, primary_key=True)
    content = db.Column('content', db.String(1024), nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))

    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    parent = db.relationship('Comment', backref=db.backref('replies', lazy='dynamic'), remote_side=[id])

    def __repr__(self):
        return '<Comment %d>' % self.id
