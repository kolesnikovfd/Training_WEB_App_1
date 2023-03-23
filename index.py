from flask import Flask, render_template, redirect, request, make_response, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.job import CreateForm
from forms.user import RegisterForm, LoginForm

from data import db_session
from data.users import User
from data.jobs import Jobs
# from data.departments import Department

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


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


@app.route('/distribution')
def distribution():
    crew = ['Ридли Скотт', 'Harry Potter', 'Vasya Pupkin']  # Некий список членов команды
    return render_template('distribution.html', title='Размещение', crew=crew)


@app.route('/table/<sex>/<int:age>')
def table(sex, age):
    return render_template('table.html', title='Оформление каюты', sex=sex, age=age)


@app.route('/')
@app.route('/index')
def works_log():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
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


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/create_job', methods=['GET', 'POST'])
@login_required
def create_job():
    form = CreateForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs()
        job.team_leader = form.team_leader.data
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.start_date = form.start_date.data
        job.end_date = form.end_date.data
        job.is_finished = form.is_finished.data
        current_user.jobs.append(job)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect("/")
    return render_template('create_job.html', title='Добавление Работы', form=form)


def search():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(1)
    for job in user.jobs:
        print(job)
    """
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
