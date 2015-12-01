from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_lazyviews import LazyViews
from flask import session, redirect, current_app
from celery import Celery
import config

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = None
login_manager.login_view = 'auth.login'
celery = Celery(__name__, broker=config.CELERY_BROKER_URL, 
                backend=config.CELERY_RESULT_BACKEND)

def create_app(config_filename):
    global celery

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

    from .tasks import tasks as tasks_blueprint
    app.register_blueprint(tasks_blueprint, url_prefix='/tasks')
    
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    celery = init_celery(app)
    app.jinja_env.globals.update(title=str.title,
                                 iteritems=dict.iteritems, len=len)
    return app

def init_celery(app):
    global celery
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    
    celery.Task = ContextTask
    return celery

