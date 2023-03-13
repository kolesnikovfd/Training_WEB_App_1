import json
from loginform import LoginForm
from flask import Flask, render_template, redirect
from data import db_session, __all_models
from data.users import User


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


def main():
    db_session.global_init("db/mars_explorer.db")
    db_sess = db_session.create_session()
    surnames = ["Scott", "Smith", "Johnson", "Williams"]
    names = ["Ridley", "James", "Mary", "David"]
    ages = [21, 16, 20, 30]
    positions = ["captain", "sailor", "bosun", "chief mate"]
    specialities = ["research engineer", "navigator/pilot", "life-support engineer", "doctor"]
    emails = ["scott_chief@mars.org", "smith@mars.org", "johnson@mars.org", "williams@mars.org"]
    passwords = ["cap", "sailor228", "mary_j", "da_will"]
    for i in range(4):
        user = User()
        user.surname = surnames[i]
        user.name = names[i]
        user.age = ages[i]
        user.position = positions[i]
        user.speciality = specialities[i]
        user.address = f"module_{i + 1}"
        user.email = emails[i]
        user.hashed_password = passwords[i]
        db_sess.add(user)
    db_sess.commit()


if __name__ == '__main__':
    # app.run(port='8080', host='127.0.0.1')
    main()
