import os
import logging
import click
from logging.handlers import RotatingFileHandler, SMTPHandler

from flask import Flask, render_template, Markup, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from loguru import logger

from bluelog.settings import config
from bluelog.buleprints.auth import auth_bp
from bluelog.buleprints.admin import admin_bp
from bluelog.buleprints.blog import blog_bp
from bluelog.buleprints.look import look_bp
from bluelog.extensions import bootstrap, moment, mail, ckeditor, db, login_manager, csrf, toolbar
from bluelog.models import Admin, Category, Post, Comment
from bluelog.settings import basedir


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errors(app)
    register_template_context(app)
    register_request_handlers(app)
    register_logging(app)
    return app


def register_extensions(app):
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    toolbar.init_app(app)


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(look_bp, url_prefix='/look')


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories, unread_comments=unread_comments)


def register_commands(app):

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='drop and create database')
    def initdb(drop):
        if drop:
            click.confirm('删除存在的数据库和数据？', abort=True)
            db.drop_all()
            click.echo('数据库数据删除完成')
        db.create_all()
        click.echo("数据库创建完成")

    @app.cli.command()
    @click.option('--category', default=10, help='生成虚拟数据--分类数据')
    @click.option('--post', default=50, help='生成虚拟数据--文章数据')
    @click.option('--comment', default=500, help='生成虚拟数据--评论数据')
    def forge(category, post, comment):
        from bluelog.fakes import fake_admin, fake_categories, fake_posts, fake_comments

        db.drop_all()
        db.create_all()

        click.echo('正在生成管理员数据')
        fake_admin()

        click.echo('正在生成%s条分类数据' % category)
        fake_categories(category)

        click.echo('正在生成%s条文章数据' % post)
        fake_posts(post)

        click.echo('正在生成%s条评论数据' % comment)
        fake_comments(comment)

        click.echo("数据生成完毕！！！")

    @app.cli.command()
    @click.option('--username', prompt=True, help='登陆用户名')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='密码')
    def init(username, password):
        click.echo('初始化数据库')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('管理员已经存在， 更新数据。。。')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('创建账号中。。。。')
            admin = Admin(
                username=username,
                blog_title='博客',
                blog_sub_title='小小博客，容纳天地～',
                name='沧海一刀断银河',
                about='醉侠骨柔情',
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo("创建默认分类。。。")
            category = Category(name='default')
            db.session.add(category)

        db.session.commit()
        click.echo("初始化完成")


def register_errors(app):

    @app.errorhandler(400)
    def bad_requests(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return '<h2>500 -- 处理错误</h2>', 500


def register_request_handlers(app):
    @app.after_request
    def query_profile(response):
        # result = get_debug_queries()
        # logger.debug('result:{}'.format(type(result)))
        # logger.debug(len(result))
        # for r in result[:5]:
        #     logger.debug(type(r))
        #     logger.debug(r)
        #     logger.debug('sql:{}'.format(r.statement))
        #     logger.debug('parameters:{}'.format(r.parameters))
        #     logger.debug('duration:{}'.format(r.duration))
        #     logger.debug(r.context)
        # logger.debug(app.extensions)
        # logger.debug(app.jinja_env.globals)
        # logger.debug(Markup('<h1>hello,world</h1>'))
        # logger.debug(dir(Markup('<h1>hello,world</h1>')))
        # logger.debug(Markup.escape('<h1>hello,world</h1>'))
        return response


def register_logging(app):
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/bluelog.log'),
                                       maxBytes=1 * 10 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=['ADMIN_EMAIL'],
        subject='Bluelog Application Error',
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.INFO)
    mail_handler.setFormatter(request_formatter)

    # if not app.debug:
    # app.logger.addHandler(mail_handler)
    app.logger.addHandler(file_handler)

