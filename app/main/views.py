from flask import render_template, redirect, url_for, abort, flash, jsonify, request
from flask.ext.login import login_required, current_user
from . import main
from .. import db
from ..models import User
from .. import celery
import random
import time
import os
import sys
import subprocess


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user and current_user.id == user.id:
        return render_template('user.html', user=user)
    elif user:
        return render_template('public_user.html', user=user)
    else:
        return abort(404)
