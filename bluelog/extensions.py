from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension


# 数据库
db = SQLAlchemy()
# 渲染表单
bootstrap = Bootstrap()
# 渲染时间
moment = Moment()
# 邮件
mail = Mail()
# 富编辑器
ckeditor = CKEditor()
# 登陆管理
login_manager = LoginManager()
# csrf保护
csrf = CSRFProtect()
# 分析工具
toolbar = DebugToolbarExtension()


@login_manager.user_loader
def load_user(user_id):
    from bluelog.models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
login_manager.login_message = '请先登陆管理员账户'
