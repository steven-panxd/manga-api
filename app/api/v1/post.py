from flask import g, current_app

from . import api_v1
from app.db import db
from app.db.model import Post, Comment
from app.form import CreatePostForm, GetPostsForm, ModifyPostForm, GetPostCommentsForm, CreatePostCommentForm, \
    ReplyPostCommentForm, ModifyPostCommentForm
from app.utils.enum import PostOrderType, CommentOrderType
from app.utils.response import Success, Fail
from app.utils.enum import Identity
from app.utils.decoration import login_required, identity_required


@api_v1.route('/post', methods=['POST'])
@login_required
@identity_required(Identity.AUTHOR)
def create_post():  # create a post
    form = CreatePostForm().validate_for_api()
    with db.auto_commit():
        post = Post()
        post.uploader = g.user
        post.title = form.title.data
        post.author = form.author.data
        post.cover_image = form.cover_image.data
        post.content = form.content.data
        post.category = form.category.data
        g.user.post_num += 1
        db.session.add(post)
    return Success('Created post successfully')


@api_v1.route('/posts', methods=['GET'])
@login_required
def get_posts():  # get a posts list with some filters
    form = GetPostsForm().validate_for_api()
    post_query = db.session.query(Post)
    if form.cid.data != 0:
        post_query = post_query.filter(Post.category_id == form.cid.data)
    if form.uid.data != 0:
        post_query = post_query.filter(Post.author_id == form.uid.data)
    order_rule = PostOrderType.get(form.oby.data)
    post_query = post_query.order_by(eval(order_rule))
    post_paginator = post_query.paginate(page=form.page.data, per_page=current_app.config.get('POSTS_NUMBER_PER_PAGE'))
    return Success(payload={
        "posts": post_paginator.items,
        "total_page": post_paginator.pages,
        "current_page": post_paginator.page
    })


@api_v1.route('/post/<int:post_id>', methods=['GET'])
@login_required
def get_post(post_id):  # get a post by id
    post = db.session.query(Post).filter(Post.id == post_id).first_or_404()
    return Success(payload={
        'post': post
    })


@api_v1.route('/post/<int:post_id>', methods=['PATCH'])
@login_required
@identity_required(Identity.AUTHOR)
def modify_post(post_id):  # modify a post by id
    form = ModifyPostForm().validate_for_api()
    post = db.session.query(Post).filter(Post.id == post_id).first_or_404()
    if (form.title is not None) or (form.content.data is not None) or (form.category.data is not None):
        with db.auto_commit():
            if form.title.data is not None:
                post.title = form.title.data
            if form.content.data is not None:
                post.content = form.content.data
            if form.category.data is not None:
                post.category = form.category.data
    else:
        raise Fail(message='Invalid params')
    return Success()


@api_v1.route('/post/<int:post_id>', methods=['DELETE'])
@login_required
@identity_required(Identity.AUTHOR)
def delete_post(post_id):  # delete a post by id
    post = db.session.query(Post).filter(Post.id == post_id).first_or_404()
    if post.author_id != g.user.id:
        raise Fail(message='You are not the author of this post')
    with db.auto_commit():
        post.is_deleted = 1
        post.author.post_num -= 1
    return Success()


@api_v1.route('/post/<int:post_id>/like', methods=['GET'])
@login_required
def like_post(post_id):  # like a post by id
    post = db.session.query(Post).filter(Post.id == post_id).first_or_404()
    if post.author_id == g.user.id:
        raise Fail(message='You can not like your own post')
    if post.like:
        g.user.unlike(post)
        return Success(payload={
            'message': 'Successfully unlike the post',
            'action': 'unlike'
        })
    else:
        g.user.like(post)
        return Success(payload={
            'message': 'Successfully like the post',
            'action': 'like'
        })


@api_v1.route('/post/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):  # get a post comments list by post id
    form = GetPostCommentsForm().validate_for_api()
    post = db.session.query(Post).filter(Post.id == post_id).first_or_404()
    comment_query = post.comments
    order_rule = CommentOrderType.get(form.oby.data)
    comment_query = comment_query.order_by(eval(order_rule))
    comment_paginator = comment_query.paginate(page=form.page.data, per_page=current_app.config.get('COMMENTS_NUMBER_PER_PAGE'))
    return Success(payload={
        "comments": comment_paginator.items,
        "total_page": comment_paginator.pages,
        "current_page": comment_paginator.page
    })


@api_v1.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def new_post_comment(post_id):  # create a post comment by post id
    form = CreatePostCommentForm().validate_for_api()
    post = db.session.query(Post).filter(Post.id == post_id).first_or_404()
    with db.auto_commit():
        comment = Comment()
        comment.post_id = post.id
        comment.author_id = g.user.id
        comment.content = form.content.data
        db.session.add(comment)
        post.comment_num += 1
    return Success()


@api_v1.route('/post/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_comment(comment_id):  # reply a comment by comment id
    form = ReplyPostCommentForm().validate_for_api()
    comment = db.session.query(Comment).filter(Comment.id == comment_id).first_or_404()
    with db.auto_commit():
        reply = Comment()
        reply.author_id = g.user.id
        reply.parent_id = form.parent.id
        reply.content = form.content.data
        reply.post_id = form.parent.post.id
        db.session.add(comment)
    return Success()


@api_v1.route('/post/comment/<int:comment_id>', methods=['PATCH'])
@login_required
@identity_required(Identity.MANAGER)
def modify_comment(comment_id):  # edit a comment by comment id
    form = ModifyPostCommentForm().validate_for_api()
    comment = db.session.query(Comment).filter(Comment.id == comment_id).first_or_404()
    if (form.parent.data is not None) or (form.content.data is not None):
        with db.auto_commit():
            if form.parent.data:
                comment.parent = form.parent.data
            if form.content.data:
                comment.content = form.content.data
    else:
        raise Fail(message='Invalid params')
    return Success()


@api_v1.route('/post/comment/<int:comment_id>', methods=['DELETE'])
@login_required
@identity_required(Identity.MANAGER)
def delete_comment(comment_id):  # delete a comment by comment id
    comment = db.session.query(Comment).filter(Comment.id == comment_id).first_or_404()
    with db.auto_commit():
        comment.is_deleted = 1
        comment.author.post_num -= 1
    return Success()


@api_v1.route('/posts/comments', methods=['DELETE'])
def delete_comments():  # delete comments by comment id list
    return "delete_comments"


