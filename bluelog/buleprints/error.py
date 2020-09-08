from flask import Blueprint


err_bp = Blueprint('error', __name__)


@err_bp.errorhandler(404)
def handle_404(e):

    return '<h2>对不起，没有找到相关内容！</h2>'