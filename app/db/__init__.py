from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery as _BaseQuery
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import SQLAlchemyError


class BaseQuery(_BaseQuery):
    def filter(self, *criterion):
        return self.filter_by(id_deleted=0)


class SQLAlchemy(_SQLAlchemy):
    Query = BaseQuery

    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e


db = SQLAlchemy()
ma = Marshmallow()

from . import model
from . import serializer
