import json
#from loginform import LoginForm
from flask import Flask, render_template, url_for, redirect

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


if __name__ == '__main__':
    app.run(port='8080', host='127.0.0.1')
