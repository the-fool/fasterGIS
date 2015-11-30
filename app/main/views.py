from flask import render_template, redirect, url_for, abort, flash, jsonify, request
from flask.ext.login import login_required, current_user
from . import main
from .forms import AddTaskForm
from .. import db
from ..models import User, Task
from ..scripts import simul_types



@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    add_task_form = AddTaskForm()
    add_task_form.simul_type.choices = simul_types 
    user = User.query.filter_by(username=username).first()
    if user and current_user.id == user.id:
        return render_template('dashboard.html', user=user)
    elif user:
        return render_template('public_user.html', user=user)
    else:
        return abort(404)
