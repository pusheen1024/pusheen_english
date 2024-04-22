from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class FillGapsForm(FlaskForm):
    word = StringField('Пропущено слово:', validators=[DataRequired()])
    submit = SubmitField('Ответить!')