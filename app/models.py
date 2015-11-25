import os
import errno
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from database import Base
from sqlalchemy import Numeric, DateTime, Column, ForeignKey, Integer, String, Table, text, Sequence
from sqlalchemy.orm import relationship, backref


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_seq'), primary_key=True)
    email = Column(String(64), unique=True, index=True)
    username = Column(String(64), unique=True, index=True)
    password_hash = Column(String(128))
    name = Column(String(64))

    tasks = relationship('Task', backref='user', 
                         cascade="all, delete, delete-orphan")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def build_directory(self):
        user_dir = '{0}/app/users/{1}'.format(os.getcwd(),self.id)
        assert not os.path.exists(user_dir)
        try:
            os.makedirs('{0}/data'.format(user_dir))
            os.makedirs('{0}/results'.format(user_dir))
            os.makedirs('{0}/scripts'.format(user_dir))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, Sequence('task_sq'), primary_key=True)
    task_id = Column(String(765), unique=True)
    status = Column(String(150))
    result = Column(String(200))
    date_done = Column(DateTime)
    traceback = Column(String(700))
    user_id = Column(Integer, ForeignKey('users.id'))


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
