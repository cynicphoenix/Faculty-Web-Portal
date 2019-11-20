import os
from flask import Flask
from config import app_config
from flask import render_template
from flask_bootstrap import Bootstrap
from home import home as home_blueprint
from about import about as about_blueprint
from auth import auth as auth_blueprint
from admin import admin as admin_blueprint
from database_postgres.database import initialize, delete_table
from user import user as user_blueprint

config_name = os.getenv('FLASK_CONFIG')

# Database initialization
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(app_config['development'])
app.config.from_pyfile('config.py')
Bootstrap(app)

# delete_table()
# initialize()

# Registering Blueprints
app.register_blueprint(home_blueprint)
app.register_blueprint(about_blueprint, url_prefix='/about')
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(user_blueprint, url_prefix='/user')

if __name__ == '__main__':
    app.run()
