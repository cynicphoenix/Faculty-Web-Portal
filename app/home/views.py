from flask import render_template
from auth.views import get_username, get_isadmin, get_role
from . import home

@home.route('/')
def homepage():
    return render_template('home/index.html', title="Welcome",username = get_username(), isadmin = get_isadmin(), role = get_role())

@home.route('/error403')
def error403():
    return render_template('errors/403.html', title="Error 403",username = get_username(), isadmin = get_isadmin(), role = get_role())

@home.route('/error')
def error():
    return render_template('errors/error.html', title="Error",username = get_username(), isadmin = get_isadmin(), role = get_role())