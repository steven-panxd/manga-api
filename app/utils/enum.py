from enum import unique, Enum as _Enum

from app.config import DevelopmentConfig, TestingConfig, ProductionConfig


class Enum(_Enum):
    @classmethod
    def get(cls, key):
        return cls.__getitem__(key.upper()).value

    @classmethod
    def items(cls):
        items = []
        for item in cls.__members__.keys():
            item = {"key": item, "value": cls.get(item)}
            items.append(item)
        return items

    @classmethod
    def contains(cls, key):
        enum_keys = list(cls.__members__.keys())
        return enum_keys.__contains__(key.upper())


@unique
class Config(Enum):
    DEVELOPMENT = DevelopmentConfig
    TESTING = TestingConfig
    PRODUCTION = ProductionConfig


@unique
class EmailType(Enum):
    REGISTER = 0
    FORGET = 1
    NOTIFY = 2


@unique
class Identity(Enum):
    USER = 0
    AUTHOR = 1
    MANAGER = 2
    ADMINISTRATOR = 3


@unique
class PostOrderType(Enum):
    ADD_TIME_INC = 'Post.add_time'
    VIEW_NUM_INC = 'Post.view_num'
    LIKE_NUM_INC = 'Post.like_num'
    ADD_TIME_DEC = 'Post.add_time.desc()'
    VIEW_NUM_DEC = 'Post.view_num.desc()'
    LIKE_NUM_DEC = 'Post.like_num.desc()'


@unique
class CommentOrderType(Enum):
    ADD_TIME_INC = 'Comment.add_time'
    LIKE_NUM_INC = 'Comment.like_num'
    ADD_TIME_DEC = 'Comment.add_time.desc()'
    LIKE_NUM_DEC = 'Comment.like_num.desc()'
