from flask import Blueprint, render_template, redirect, url_for, flash
from bluelog.tools import redirect_back
from bluelog.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from bluelog.models import Admin


auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        user = Admin.query.filter_by(username=username).first()
        if not user:
            flash('用户名和密码不匹配', 'warning')
            return redirect(url_for('auth.login'))
        if user.validate_password(password):
            # 表示验证通过
            login_user(user, remember)
            flash('%s, 登陆成功, 欢迎回来' % username, 'info')
            return redirect_back()
        else:
            # 验证不通过
            flash('用户名和密码不匹配', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required # 视图保护
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()


@auth_bp.route('/settings', methods=['post', 'get'])
@login_required
def settings():
    return render_template('blog/index.html')