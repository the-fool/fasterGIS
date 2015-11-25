import os
import errno
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from database import Base
from sqlalchemy import Numeric, Column, ForeignKey, Integer, String, Table, text, Sequence
from sqlalchemy.orm import relationship



class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_seq'), primary_key=True)
    email = Column(String(64), unique=True, index=True)
    username = Column(String(64), unique=True, index=True)
    password_hash = Column(String(128))
    name = Column(String(64))

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
        user_dir = 'users/{0}'.format(self.id)
        assert not os.path.exists(user_dir)
        try:
            os.makedirs('{0}/data'.format(user_dir))
            os.makedirs('{0}/results'.format(user_dir))
            os.makedirs('{0}/scripts'.format(user_dir))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
