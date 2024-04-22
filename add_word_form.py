from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class AddWordForm(FlaskForm):
    choices = ['Существительное', 'Прилагательное', 'Глагол']
    part_of_speech = SelectField('Часть речи', choices=choices, validators=[DataRequired()])
    word = StringField('Слово:', validators=[DataRequired()])
    submit = SubmitField('Добавить!')
