from flask import url_for

from bluelog.models import Category, Comment, Post
from bluelog.extensions import db
from tests.base import BaseTestCase


class AdminTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(AdminTestCase, self).setUp()
        self.login()

        category = Category(name='default')
        post = Post(title='Hello', category=category, body='hahaha...')
        comment = Comment(body='a comment', post=post, from_admin=True)
        db.session.add_all([category, post, comment])
        db.session.commit()

    def test_new_post(self):
        response = self.client.get(url_for('admin.new_post'))
        data = response.get_data(as_text=True)
        self.assertIn('新文章', data)

        response = self.client.post(url_for('admin.new_post'), data=dict(
            title='something',
            category=1,
            body='hello, world'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('文章发表成功', data)
        self.assertIn('something', data)

    def test_edit_post(self):
        # 测试get请求
        response = self.client.get(url_for('admin.edit_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('编辑文章', data)
        self.assertIn('Hello', data)
        self.assertIn('haha', data)

        # 测试post请求
        response = self.client.post(url_for('admin.edit_post', post_id=1), data=dict(
            title='new post',
            category=1,
            body='鱼翅吃多了，糊嗓子啊～'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('new post', data)
        self.assertIn('鱼翅吃多了，糊嗓子啊', data)

    def test_delete_post(self):
        response = self.client.post(url_for('admin.delete_post', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('文章删除成功', data)

        response = self.client.get(url_for('admin.delete_post', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('文章删除成功', data)
        self.assertIn('Method Not Allowed', data)

    def test_delete_comment(self):
        response = self.client.get(url_for('admin.delete_comment', comment_id=1),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('删除评论成功', data)
        self.assertIn('Method Not Allowed', data)

        response = self.client.post(url_for('admin.delete_comment', comment_id=1)
                                    , follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('删除评论', data)

    def test_enable_comment(self):
        post = Post.query.get(1)
        post.can_comment = False
        db.session.commit()

        response = self.client.post(url_for('admin.set_comment', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('评论开启', data)

    def test_disable_comment(self):
        response = self.client.post(url_for('admin.set_comment', post_id=1),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('评论关闭', data)

        response = self.client.get(url_for('blog.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertNotIn('<form id="comment-form">', data)

    def test_approve_comment(self):
        # 1，退出登陆
        self.logout()
        # 2, 发一评论
        response = self.client.post(url_for('blog.show_post', post_id=1),
                                    data=dict(
                                        author='访客',
                                        email='122800@qq.com',
                                        site='http://www.hello.com',
                                        post_id=1,
                                        body='there is a dog'
                                    ), follow_redirects=True)
        data = response.get_data(as_text=True)
        # 3, 验证是不是发布了
        self.assertIn('你的评论需要审核', data)
        self.assertNotIn('there is a dog', data)

        # 4, 登陆
        self.login()
        response = self.client.post(url_for('admin.approve_comment', comment_id=2),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('评论审核通过', data)

        response = self.client.get(url_for('blog.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('there is a dog', data)

    def test_new_category(self):
        response = self.client.get(url_for('admin.new_category'))
        data = response.get_data(as_text=True)
        self.assertIn('新建分类', data)

        response = self.client.post(url_for('admin.new_category'), data=dict(
            name='火影'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('分类创建成功', data)
        self.assertIn('火影', data)

        response = self.client.post(url_for('admin.new_category'), data=dict(
            name='火影'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('此分类已经存在', data)

        # todo： 单元测试继续





