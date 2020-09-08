from flask import url_for, current_app
from bluelog.extensions import mail
from flask_mail import Message
from threading import Thread


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, html):
    """
    发送邮件函数
    :param subject: 邮件的主题
    :param to: 收件人信息
    :param html: 邮件的内容
    :return:
    """
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=(app, message))
    thr.start()
    return thr


def send_new_comment_email(post):
    """
    当文章有新的评论时，发送邮件通知管理员
    :param post: 文章
    :return:
    """
    post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
    send_mail('新的评论', current_app.config['BLUELOG_EMAIL'],
              html='<p>有新的评论，在文章 <i>%s</i>, 点击下方连接查看详情:</p>'
                   '<p><a href="%s">%s</a></P>'
                   '<p><small style="color: #868e96">此邮件无需回复.</small></p>'
                   % (post.title, post_url, post_url))


def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comment'
    send_mail('新的回复', comment.email,
              html='<p>New reply for the comment you left in post <i>%s</i>, click the link below to check: </p>'
                   '<p><a href="%s">%s</a></p>'
                   '<p><small style="color: #868e96">Do not reply this email.</small></p>'
                   %(comment.post.title, post_url, post_url))