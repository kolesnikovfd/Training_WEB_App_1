import json
import datetime

from flask import Flask, render_template, redirect
from forms.user import RegisterForm
from loginform import LoginForm
from data import db_session, __all_models

from data.users import User
from data.jobs import Jobs
from data.departments import Department

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/<title>')
@app.route('/index/<title>')
def index(title):
    return render_template('index.html', title=title)


@app.route('/training/<prof>')
def training(prof):
    return render_template('training.html', prof=prof)


@app.route('/list_prof/<list>')
def list_prof(list):
    return render_template('list_prof.html', list=list)


@app.route('/answer')
@app.route('/auto_answer')
def auto_answer():
    # Откуда мы должны брать значения??
    # Подставил из примера в задании
    param = {
        'title': 'Анкета',
        'surname': 'Watny',
        'name': 'Mark',
        'education': 'высше среднего',
        'profession': 'штурман марсохода',
        'sex': 'male',
        'motivation': 'Всегда мечтал зависнуть на Марсе!',
        'ready': 'True',
    }
    return render_template('auto_answer.html', **param)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/Доступ разрешён')
    return render_template('login.html', title='Аварийный доступ', form=form)


@app.route('/distribution')
def distribution():
    crew = ['Ридли Скотт', 'Harry Potter', 'Vasya Pupkin']  # Некий список членов команды
    return render_template('distribution.html', title='Размещение', crew=crew)


@app.route('/table/<sex>/<int:age>')
def table(sex, age):
    return render_template('table.html', title='Оформление каюты', sex=sex, age=age)


@app.route('/works_log')
def works_log():
    db_session.global_init("db/mars_explorer.db")
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    for job in jobs:
        tl = db_sess.query(User).filter(User.id == job.team_leader).first()
        job.team_leader = f'{tl.surname} {tl.name}'
    return render_template('works_log.html', jobs=jobs)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def search():
    db_sess = db_session.create_session()
    membs = db_sess.query(Department).filter(Department.id == 1).first().members
    users = db_sess.query(User).filter(User.id.in_(map(int, membs.split(', '))))
    for user in users:

        work_time = 25
        for job in user.jobs:
            if job.is_finished:
                work_time -= job.work_size
                if work_time < 0:
                    print(f'{user.name} {user.surname}')
                    break
    """
    # Задание 4. Первая работа
    job = Jobs()
    job.team_leader = 2
    job.job = 'deployment of residential module 3'
    job.work_size = 11
    job.collaborators = '4'
    job.start_date = datetime.datetime.now()
    job.is_finished = True
    db_sess.add(job)
    db_sess.commit()
    """


def main():
    db_session.global_init("db/mars_explorer.db")
    app.run(port='8080', host='127.0.0.1')


if __name__ == '__main__':
    main()
