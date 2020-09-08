from flask import Blueprint, request, current_app, render_template, redirect, url_for, abort, make_response, flash
from flask_login import current_user
from loguru import logger

from bluelog.models import Post, Category, Comment, Admin
from bluelog.forms import CommentForm, AdminComment
from bluelog.tools import redirect_back
from bluelog.extensions import db


blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    # logger.debug(dir(current_app.logger))
    current_app.logger.warning('url:{}'.format(request.url))
    # current_app.logger.file_handler.warning('host_url:{}'.format(request.host_url))
    # current_app.logger.file_handler.warning('host:{}'.format(request.host))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=posts)


@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=['post', 'get'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config["BLUELOG_COMMENT_PER_PAGE"]
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items
    # 通过是否登陆，登陆给出管理员评论表单，没登陆给出普通匿名用户的登陆表单
    if current_user.is_authenticated:
        # logger.debug("是管理员登陆的！")
        form = AdminComment()
    else:
        # logger.debug("不是管理员登陆的！")
        form = CommentForm()

    if form.validate_on_submit():
        # 是否为回复评论
        reply_id = request.args.get('reply')
        if current_user.is_authenticated:
            # 是管理员的评论
            admin = Admin.query.first()
            comment = Comment(
                author=admin.username,
                # email=url_for('blog.index'),
                site=url_for('blog.index'),
                body=form.body.data,
                post_id=post_id,
                from_admin=True,
                reviewed=True,
                replied_id=reply_id if reply_id else None
            )
            flash('评论发布成功', 'success')
        else:
            # 不是管理员的评论
            comment = Comment(
                author=form.author.data,
                email=form.email.data,
                site=form.site.data,
                body=form.body.data,
                post_id=post_id,
                from_admin=False,
                reviewed=False,
                replied_id=reply_id if reply_id else None
            )
        db.session.add(comment)
        db.session.commit()
        flash('你的评论需要审核', 'info')
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)


@blog_bp.route('/reply_comment/<int:comment_id>', methods=['get', 'post'])
def reply_comment(comment_id):
    # todo: 添加回复评论功能
    comment = Comment.query.get_or_404(comment_id)

    return redirect(url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author)+'#comment-form')


@blog_bp.route('/change_theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)

    return response