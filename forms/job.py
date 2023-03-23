from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, TextAreaField, DateField
from wtforms.validators import DataRequired


class CreateForm(FlaskForm):
    team_leader = IntegerField('Руководитель', validators=[DataRequired()])
    job = TextAreaField('Описание работы', validators=[DataRequired()])
    work_size = IntegerField('Объем работы в часах', validators=[DataRequired()])
    collaborators = StringField('Список участников')
    start_date = DateField('Дата начала')
    end_date = DateField('Дата окончания')
    is_finished = BooleanField('Флаг завершения работ')
    submit = SubmitField('Создать')
