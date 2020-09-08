from faker import Faker
from bluelog.models import Admin, Category, Post, Comment
from bluelog.extensions import db
from sqlalchemy.exc import IntegrityError
import random


fake = Faker(locale='zh-cn')


def fake_admin():
    admin = Admin(
        username='admin',
        blog_title='最武侠谈',
        blog_sub_title='刀光剑影，儿女情长，绝世神功，笑傲江湖！',
        name='金庸',
        about='中国现代最伟大的武侠小说作家，时评家，香港《明报》创办人'
    )
    # admin.set_password('hello,flask')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)
    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count*0.1)
    # 未审核的评论
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

    # 管理员发表的评论
    comment = Comment(
        author='康熙',
        email='kangxi@163.com',
        site='www.kangxi.com',
        body='朕知道了',
        timestamp=fake.date_time_this_year(),
        reviewed=True,
        from_admin=True,
        post=Post.query.get(random.randint(1, Post.query.count()))
    )
    db.session.add(comment)
    db.session.commit()

    # 回复
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count())),
        )
        db.session.add(comment)
    db.session.commit()



