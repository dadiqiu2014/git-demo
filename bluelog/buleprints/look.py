from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

look_bp = Blueprint('look', __name__)


@look_bp.route('/')
def index():
    form = TestForm()
    return render_template('look/index.html', form=form)


class TestForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    select = SelectField('类别', coerce=int, default=1)
    body = CKEditorField('正文', validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        self.select.choices = [(1, '默认'), (2, '欧美'), (3, '亚洲')]