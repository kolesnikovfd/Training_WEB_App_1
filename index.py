from flask import Flask, render_template, redirect, request, make_response, session, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.job import JobForm
from forms.user import RegisterForm, LoginForm

from data import db_session
from data.users import User
from data.jobs import Jobs
# from data.departments import Department

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/training/<prof>')  # мусор
def training(prof):
    return render_template('training.html', prof=prof)


@app.route('/list_prof/<list>')  # мусор
def list_prof(list):
    return render_template('list_prof.html', list=list)


@app.route('/answer')
@app.route('/auto_answer')  # мусор
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


@app.route('/distribution')  # мусор
def distribution():
    crew = ['Ридли Скотт', 'Harry Potter', 'Vasya Pupkin']  # Некий список членов команды
    return render_template('distribution.html', title='Размещение', crew=crew)


@app.route('/table/<sex>/<int:age>')  # мусор
def table(sex, age):
    return render_template('table.html', title='Оформление каюты', sex=sex, age=age)


@app.route("/cookie_test")  # мусор
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


@app.route("/session_test")  # мусор
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return render_template('index.html', jobs=jobs, title='Works log')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
        user = User()
        user.email = form.email.data,
        user.surname = form.surname.data,
        user.name = form.name.data,
        user.age = form.age.data,
        user.position = form.position.data,
        user.speciality = form.speciality.data,
        user.address = form.address.data,

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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
                               title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/job', methods=['GET', 'POST'])
@login_required
def create_job():
    form = JobForm()
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
        team_leader = load_user(job.team_leader)
        team_leader.jobs.append(job)
        db_sess.merge(team_leader)
        db_sess.commit()
        return redirect("/")
    return render_template('create_job.html', title='Добавление работы', form=form)


@app.route('/job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    form = JobForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.id == 1:
            job = db_sess.query(Jobs).get(job_id, 0)
        else:
            job = db_sess.query(Jobs).filter(Jobs.id == job_id, Jobs.user == current_user).first()
        if job:
            form.team_leader.data = job.team_leader
            form.job.data = job.job
            form.work_size.data = job.work_size
            form.collaborators.data = job.collaborators
            form.start_date.data = job.start_date
            form.end_date.data = job.end_date
            form.is_finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if current_user.id == 1:
            job = db_sess.query(Jobs).get(job_id, 0)
        else:
            job = db_sess.query(Jobs).filter(Jobs.id == job_id, Jobs.user == current_user).first()
        if job:
            job.team_leader = form.team_leader.data
            job.job = form.job.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            job.start_date = form.start_date.data
            job.end_date = form.end_date.data
            job.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect("/")
        else:
            abort(404)
    return render_template('create_job.html', form=form, title='Редактирование работы')


@app.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    db_sess = db_session.create_session()
    if current_user.id == 1:
        job = db_sess.query(Jobs).get(job_id, 0)
    else:
        job = db_sess.query(Jobs).filter(Jobs.id == job_id, Jobs.user == current_user).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/mars_explorer.db")
    app.run(port='8080', host='127.0.0.1')


if __name__ == '__main__':
    main()
