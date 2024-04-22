from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CrosswordForm(FlaskForm):
    control_word = StringField('Ответ:', validators=[DataRequired()])
    submit = SubmitField('Ответить!')
