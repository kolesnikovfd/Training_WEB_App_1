import json
import datetime
from loginform import LoginForm
from flask import Flask, render_template, redirect
from data import db_session, __all_models
from data.users import User
from data.jobs import Jobs

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
    print(1)
    jobs = db_sess.query(Jobs).all()
    print(*jobs)
    for job in jobs:
        print(job.team_leader)
        tl = db_sess.query(User).filter(User.id == job.team_leader).first()
        job.team_leader = f'{tl.surname} {tl.name}'
        print(4)
    """
    params = {'title': 'Список работ',
              'jobs': []
              }
        team_leader = 
        params['jobs'].append({
            'id': job.id,
            'job': job.job,
            'team_leader': f'{team_leader.surname} {team_leader.name}',
            'duration': {job.end_date - job.start_date} if job.is_finished else {datetime.datetime.now() - job.start_date},
            'collaborators': job.collaborators,
            'is_finised': job.is_finished
        })
    """
    return render_template('works_log.html', jobs=jobs)


def search():
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.age < 21, User.address == "module_1")
    for user in users:
        user.address = "module_3"
    db_sess.commit()

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
