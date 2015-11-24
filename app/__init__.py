from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_lazyviews import LazyViews
from flask import session, redirect, current_app

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = None
login_manager.login_view = 'auth.login'


def create_app(config_filename):
    app = Flask(__name__)
    app.debug = True
    app.config.from_pyfile(config_filename)
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    app.jinja_env.globals.update(title=str.title,
                                 iteritems=dict.iteritems, len=len)
    return app
