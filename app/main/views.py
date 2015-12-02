from flask import render_template, make_response, redirect,\
url_for, abort, flash, jsonify, request, send_from_directory
from flask.ext.login import login_required, current_user
from . import main
from .forms import AddTaskForm
from ..database import db_session as sess
from ..models import User, Task
from ..scripts import simul_types
from ..tasks import celtasks as cel
import os
from datetime import datetime
@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    form = AddTaskForm()
    form.simul_type.choices = simul_types 
    if form.validate_on_submit():
        create_simulation(form)
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

@main.route('/user/results/<task_id>')
@login_required
def results(task_id):
    t = Task.query.filter(Task.task_id == task_id).first()
    return render_template('results.html', t=t)
    #return send_from_directory('/var/www/fastGIS/', 'foo.png', as_attachment=False)

@main.route('/user/results/img/<fname>')
def img(fname):
    path = os.path.join(os.getcwd(), 'app/users/{0}/results/{1}.png'.format(current_user.id, fname))
    resp = make_response(open(path).read())
    resp.content_type = 'image/png'
    return resp


def create_simulation(form):
    task = cel.iterative_simulation.delay(iterations=form.iterations.data,
                                      uid=current_user.get_id(),
                                      simtype=form.simul_type.data)
    sess.add(Task(task_id=task.id,
                  status=task.status,
                  user_id=current_user.get_id(),
                  name=form.name.data,
                  date_begun=datetime.now(),
                  date_done=None,
                  simtype=form.simul_type.data))
    sess.commit()
