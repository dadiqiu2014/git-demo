from flask import url_for

from tests.base import BaseTestCase


class AuthTestCase(BaseTestCase):

    def test_login_user(self):
        response = self.login()
        data = response.get_data(as_text=True)
        self.assertIn('欢迎回来', data)

    def test_fail_login(self):
        response = self.login(username='wrong_username', password='wrong')
        data = response.get_data(as_text=True)
        self.assertIn('用户名和密码不匹配', data)

    def test_logout_user(self):
        self.login()
        response = self.logout()
        data = response.get_data(as_text=True)
        self.assertIn('Logout success', data)

    def test_login_protect(self):
        response = self.client.get(url_for('admin.settings'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先登陆管理员账户', data)
        
