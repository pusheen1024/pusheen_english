import random
from io import BytesIO

from PIL import Image
from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_restful import Api
from werkzeug.security import generate_password_hash

from data import db_session, users_resource, random_word_api
from data.locations_model import Location
from data.users_model import User
from data.achievements_model import Achievements
from data.words_model import Nouns, Verbs, Adjectives
from fill_gaps_form import FillGapsForm
from crossword_form import CrosswordForm
from add_word_form import AddWordForm
from login_form import LoginForm, RegistrationForm
from maps_api import MapsAPI
from words_api import WordsAPI
from config import SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/english.db")
db_sess = db_session.create_session()

api = Api(app)
api.add_resource(users_resource.UsersListResource, '/api/users')
api.add_resource(users_resource.AchievementsResource, '/api/users/<email>')
app.register_blueprint(random_word_api.blueprint)

maps_api = MapsAPI()
words_api = WordsAPI()


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    params = {'title': 'Авторизация',
              'form': form}
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        params['message'] = 'Неправильный логин или пароль'
        return render_template('login.html', **params)
    return render_template('login.html', **params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    fields = ['email', 'password', 'password_again', 'surname', 'name', 'age']
    params = {'title': 'Регистрация',
              'fields': fields,
              'form': form}
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            params['message'] = 'Пароли не совпадают'
        elif '@' not in form.email.data:
            params['message'] = 'Некорректный адрес электронной почты'
        elif db_sess.query(User).filter(User.email == form.email.data).first():
            params['message'] = 'Такой пользователь уже есть'
        else:
            user_params = {field: getattr(form, field).data for field in fields if 'password' not in field}
            user_params['hashed_password'] = generate_password_hash(form.password.data)
            user_params['like_english'] = form.like_english.data
            user = User(**user_params)
            db_sess.add(user)
            db_sess.commit()
            achievement_params = {'user_id': user.id,
                                  'success': 0,
                                  'total': 0}
            achievements = Achievements(**achievement_params)
            db_sess.add(achievements)
            db_sess.commit()
            return redirect('/login')
    return render_template('register.html', **params)


@app.route('/my_profile')
@login_required
def my_profile():
    achievements = db_sess.query(Achievements).filter(Achievements.user_id == current_user.id).first()
    params = {'title': 'Мой профиль',
              'success': achievements.success,
              'success_rate': (round(achievements.success / achievements.total * 100)
                               if achievements.total else '?')}
    return render_template('my_profile.html', **params)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/add_word', methods=['GET', 'POST'])
@login_required
def add_word():
    form = AddWordForm()
    params = {'title': 'Добавить слово',
              'form': form}
    if form.validate_on_submit():
        parts_of_speech = {'Существительное': Nouns, 'Глагол': Verbs, 'Прилагательное': Adjectives}
        class_name = parts_of_speech[form.part_of_speech.data]
        if db_sess.query(class_name).filter(class_name.word == form.word.data).first():
            params['message'] = 'Такое слово уже есть в базе данных!'
            return render_template('add_word.html', **params)
        word = class_name(word=form.word.data)
        db_sess.add(word)
        db_sess.commit()
        return redirect('/my_profile')
    return render_template('add_word.html', **params)


@app.route('/crossword', methods=['GET', 'POST'])
@login_required
def crossword():
    form = CrosswordForm()
    params = {'title': 'Кроссворд',
              'form': form}
    if 'size' not in session:
        control_word = words_api.get_word().lower()
        words = words_api.get_crossword_words(control_word)
        definitions = [', '.join(syn) for syn in words.values()]
        words_list = list(words.keys())
        square = Image.open('static/img/square.png')
        first_square = Image.open('static/img/first_square.png')
        x, y = square.size
        crossword_image = Image.new("RGB", (y * max(map(len, words_list)), x * len(words_list)), 'white')
        for i in range(len(words_list)):
            for j in range(len(words_list[i])):
                crossword_image.paste([first_square, square][bool(j)], (j * y, i * x))
        crossword_image.save('static/img/crossword.png')
        session['size'] = (crossword_image.size[0], crossword_image.size[1])
        session['control_word'] = control_word
        session['definitions'] = definitions
    params['width'], params['height'] = session['size']
    params['definitions'] = session['definitions']
    if form.validate_on_submit():
        return redirect(f'/check_crossword/{session["control_word"]}/{form.control_word.data}')
    return render_template('crossword.html', **params)


@app.route('/check_crossword/<corr_word>/<word>')
@login_required
def check_crossword(corr_word, word):
    achievements = db_sess.query(Achievements).filter(Achievements.user_id == current_user.id).first()
    params = {'href': '/crossword',
              'result': corr_word.lower() == word.lower(),
              'message': f'Правильный ответ - {corr_word}!'}
    session.pop('control_word', None)
    session.pop('crossword_params', None)
    session.pop('size', None)
    achievements.success += params['result']
    achievements.total += 1
    return render_template('result.html', **params)


@app.route('/fill_gaps', methods=['GET', 'POST'])
@login_required
def fill_gaps():
    form = FillGapsForm()
    if 'sentences' not in session:
        word = words_api.get_word()
        sentences = words_api.get_sentences(word)
        session['word'] = word
        session['sentences'] = sentences
    if form.validate_on_submit():
        return redirect(f'/check_answer/{session["word"]}/{form.word.data}')
    params = {'title': 'Заполнение пропусков',
              'sentences': session['sentences'],
              'form': form}
    return render_template('fill_gaps.html', **params)


@app.route('/check_answer/<corr_word>/<word>')
@login_required
def check_answer(corr_word, word):
    achievements = db_sess.query(Achievements).filter(Achievements.user_id == current_user.id).first()
    params = {'href': '/fill_gaps',
              'result': corr_word.lower() == word.lower(),
              'message': f'Правильный ответ - {corr_word}!'}
    session.pop('word', None)
    session.pop('sentences', None)
    achievements.success += params['result']
    achievements.total += 1
    return render_template('result.html', **params)


@app.route('/country_studies')
@login_required
def country_studies():
    corr_id = random.choice([loc.id for loc in db_sess.query(Location).all()])
    add_ids = random.sample([loc.id for loc in db_sess.query(Location).filter(Location.id != corr_id).all()], 2)
    filenames = list()
    for loc_id in [corr_id] + add_ids:
        entry = db_sess.query(Location).filter(Location.id == loc_id).first()
        if loc_id == corr_id:
            corr_toponym = entry.toponym
        picture = maps_api.search_by_name(entry.toponym)
        Image.open(BytesIO(picture)).save(f'static/{entry.picture}')
        filenames.append((entry.id, entry.picture))
    params = {'title': 'Страноведение',
              'filenames': filenames,
              'corr_id': corr_id,
              'corr_toponym': corr_toponym}
    return render_template('country_studies.html', **params)


@app.route('/choose/<int:corr_id>/<int:id>')
@login_required
def choose(id, corr_id):
    achievements = db_sess.query(Achievements).filter(Achievements.user_id == current_user.id).first()
    params = {'href': '/country_studies',
              'result': id == corr_id,
              'message': ['Неверно :(', 'Верно :)'][id == corr_id]}
    achievements.success += params['result']
    achievements.total += 1
    return render_template('result.html', **params)


@app.route('/random_word')
def random_word():
    word = words_api.get_word()
    entry = words_api.get_entry(word)
    params = {'title': 'Случайное слово',
              'word': word,
              'href': f'https://dictionary.cambridge.org/dictionary/english/{word}'}
    try:
        params['pronunciation'] = entry['def'][0]['ts']
    except (KeyError, IndexError):
        params['pronunciation'] = 'Sorry, we do not have the pronunciation of this word!'
    return render_template('random_word.html', **params)


@app.route('/about')
def about():
    return render_template('about.html', title='О сайте')


@app.route('/')
def main_page():
    return render_template('main_page.html', title='Главная страница')


if __name__ == '__main__':
    app.run()
