import unittest

from flask import url_for

from bluelog import create_app
from bluelog.extensions import db
from bluelog.models import Admin


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app('testing')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        user = Admin()
        user.username = 'James'
        user.name = '詹姆斯'
        user.about = '我是一个测试账号'
        user.blog_title = '测试账号'
        user.blog_sub_title = '测试'
        user.set_password('1234')
        db.session.add(user)
        db.session.commit()

    def tearDown(self) -> None:
        db.drop_all()
        self.context.pop()

    def login(self, username=None, password=None):
        if username is None and password is None:
            username = 'James'
            password = '1234'

        return self.client.post(url_for('auth.login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.post(url_for('auth.logout'), follow_redirects=True)
