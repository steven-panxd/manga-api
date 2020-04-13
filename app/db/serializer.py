from collections import Iterable

from app.db import ma


class BaseSchema(ma.ModelSchema):
    class Meta:
        fields = []

    def add(self, field_name):
        if isinstance(field_name, Iterable):
            for i in field_name:
                self.Meta.fields.append(i)
        else:
            self.Meta.fields.append(field_name)

    def remove(self, field_name):
        if isinstance(field_name, Iterable):
            for i in field_name:
                self.Meta.fields.remove(i)
        else:
            self.Meta.fields.remove(field_name)


class SlideSchema(BaseSchema):
    class Meta:
        fields = ['id', 'title', 'url', 'image', 'order', 'add_time']


class IdentitySchema(BaseSchema):
    class Meta:
        fields = ['id', 'name', 'add_time']


class UserSchema(BaseSchema):
    class Meta:
        fields = ['id', 'username', 'email', 'bio', 'avatar', 'identity', 'post_num', 'coin_num', 'add_time']
    identity = ma.Nested(IdentitySchema)


class CategorySchema(BaseSchema):
    class Meta:
        fields = ['id', 'name', 'add_time']


class CommentSchema(BaseSchema):
    class Meta:
        fields = ['id', 'author', 'content', 'author', 'add_time']
    author = ma.Nested(UserSchema)


class PostSchema(BaseSchema):
    class Meta:
        fields = ['id', 'uploader', 'author', 'title', 'category', 'cover_image', 'like', 'like_num', 'view_num',
                  'coin_num', 'collected_num', 'comment_num', 'add_time']
    uploader = ma.Nested(UserSchema)
    category = ma.Nested(CategorySchema)
