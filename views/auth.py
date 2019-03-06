from flask import render_template, Blueprint, request, session, redirect, url_for
from functools import wraps

from auth_utils import check_user_exists, check_user_without_password, register_new_user, check_user_password,\
                        get_user_path

bp = Blueprint('auth', __name__)


def is_someone_logged_in():
    if 'user_name' in session:
        return True
    else:
        return False


def get_logged_in_user_name():
    return session['user_name']


def get_current_user_path():
    return get_user_path(get_logged_in_user_name())


def required_login(func):
    @wraps(func)
    def decorated_func(**kwargs):
        if is_someone_logged_in():
            return func(**kwargs)
        else:
            return redirect(url_for('auth.login'))

    return decorated_func


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        name = request.form['userName']  # type: str
        password = request.form['password']

        if name is None or password is None:
            return "Ошибка! Необходимо ввести имя пользователя и пароль."

        if not (name.isalpha() and name.isascii()):
            return 'Ошибка! Имя содержит недопустимый(е) символ(ы).'

        if name.find('/') != -1 or name.find('\\') != -1:
            return "Ошибка! Имя пользователя содержит недопустимый символ."

        if check_user_exists(name) and not check_user_without_password(name):
            return "Ошибка! Пользователь с таким именем уже зарегистрирован."

        register_new_user(name, password)

        session['user_name'] = name

        return redirect(url_for("main"))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        name = request.form['userName']  # type: str
        password = request.form['password']

        if name is None or password is None:
            return "Ошибка: необходимо ввести имя пользователя и пароль."

        if not check_user_exists(name):
            return 'Ошибка! Пользователь с таким именем не зарегистрирован.'

        if check_user_password(name, password):
            session['user_name'] = name
            return redirect(url_for('main'))
        else:
            return "Ошибка: неверный пароль!"


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'user_name' in session:
        session.pop('user_name')

    return redirect(url_for("main"))
