from flask import render_template, redirect, url_for, abort, flash, jsonify, request
from flask.ext.login import login_required, current_user
from . import main
from .forms import AddTaskForm
from ..database import db_session as sess
from ..models import User, Task
from ..scripts import simul_types
from ..tasks import celtasks as cel


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    form = AddTaskForm()
    form.simul_type.choices = simul_types 
    if form.validate_on_submit():
        cel.create_simulation(form)
        return redirect(url_for('.user', username=username))
    elif request.method =='POST': 
        flash('Invalid field on creation form')
        return redirect(url_for('.user', username=username))
    user = User.query.filter_by(username=username).first()
    if user and current_user.id == user.id:
        return render_template('dashboard.html', user=user, form=form)
    elif user:
        return render_template('public_user.html', user=user)
    else:
        return abort(404)

@main.route('/user/logs/<task_id>')
@login_required
def logs(task_id):
    t = Task.query.filter(Task.task_id == task_id).first()
    return render_template('logs.html', t=t)
