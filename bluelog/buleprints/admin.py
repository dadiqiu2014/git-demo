from pprint import pprint
from loguru import logger
from flask import Blueprint, current_app, redirect, url_for, render_template, request, flash
from flask_login import login_required, current_user

from bluelog.models import Post, Category, Comment
from bluelog.forms import PostForm, CategoryForm, SettingForm
from bluelog.extensions import db
from bluelog.tools import redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
def admin():
    logger.debug(request.url)
    return '<h2>这是admin页面</h2>'


@admin_bp.route('/new_post', methods=['get','post'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        logger.debug(form.data)
        # 创建新文章
        post = Post(
            title=form.title.data,
            body=form.body.data,
            category_id=form.category.data,
        )
        db.session.add(post)
        db.session.commit()
        flash('文章发表成功！', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/new_category', methods=['post', 'get'])
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
        )
        db.session.add(category)
        db.session.commit()
        flash('分类创建成功！', 'success')
        return redirect(url_for('.manage_category'))
    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/show_category')
def show_category():
    form = CategoryForm()
    return render_template('blog/category.html', form=form)


@admin_bp.route('/new_link')
def new_link():
    return redirect(url_for('blog.index'))


@admin_bp.route('/manage_post')
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(page=page, per_page=current_app.config['BLUELOG_MANAGE_POST_PER_PAGE'])
    posts = pagination.items
    return render_template('admin/manage_post.html', posts=posts, pagination=pagination, page=page)


@admin_bp.route('/manage_category')
@login_required
def manage_category():
    pprint(current_user)
    logger.debug(current_user)
    categories = Category.query.all()
    return render_template('admin/manage_category.html', categories=categories)


@admin_bp.route('/edit_category/<int:category_id>', methods=['post', 'get'])
def edit_category(category_id):
    # 查询相应的分类
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('分类修改成功', 'success')
        return redirect(url_for('.manage_category'))
    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/delete_category/<int:category_id>', methods=['post'])
def delete_category(category_id):
    # 找到要删除的分类
    category = Category.query.get_or_404(category_id)
    # 找到此分类包含的所有文章
    # posts = category.posts
    # # 把属于此分类的文章转移到默认分类下
    # default = Category.query.first()
    # default.posts.extend(posts)
    # db.session.delete(category)
    # db.session.commit()
    category.delete()

    return redirect_back()


@admin_bp.route('/mange_link')
def manage_link():
    return redirect(url_for('blog.index'))


@admin_bp.route('/settings')
@login_required
def settings():
    form = SettingForm()
    return render_template('admin/settings.html', form=form)


@admin_bp.route('/edit_post/<int:post_id>', methods=['get', 'post'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        print(form.data)
        title = form.title.data
        category = Category.query.get(form.category.data)
        body = form.body.data
        post.title = title
        post.category = category
        post.body = body
        db.session.add(post)
        db.session.commit()
        flash('修改文章成功', 'success')
        return redirect(url_for('blog.show_post', post_id=post_id))
    form.title.data = post.title
    form.category.date = post.category.id
    form.body.data = post.body
    return render_template('admin/edit_post.html', form=form, post_id=post_id)


@admin_bp.route('/delete_post/<int:post_id>', methods=['post'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('文章删除成功', 'success')

    return redirect_back()


@admin_bp.route('/delete_comment/<int:comment_id>', methods=['post'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('删除评论成功', 'info')
    return redirect_back()


@admin_bp.route('/set_comment/<int:post_id>', methods=['post'])
@login_required
def set_comment(post_id):
    """
    设置文章是否可以评论
    :param post_id: 文章id
    :return:
    """
    # 查找相应文章
    post = Post.query.get_or_404(post_id)
    # 设置评论开关
    if post.can_comment is True:
        print("can_comment: True" )
        post.can_comment = False
        flash('评论关闭', 'success')
    else:
        print('can_comment: false')
        post.can_comment = True
        flash('评论开启', 'success')
    db.session.commit()
    return redirect_back()


@admin_bp.route('/manage_comment')
@login_required
def manage_comment():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    condition = request.args.get('filter')
    if condition == 'unread':
        pagination = Comment.query.filter_by(reviewed=False).paginate(page, per_page)
    elif condition == 'admin':
        pagination = Comment.query.filter_by(from_admin=True).paginate(page, per_page)
    else:
        pagination = Comment.query.paginate(page, per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', pagination=pagination, comments=comments)


@admin_bp.route('/approve_comment/<int:comment_id>', methods=['post'])
@login_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('评论审核通过', 'success')
    return redirect_back()
