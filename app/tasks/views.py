from flask import jsonify, url_for
from flask.ext.login import current_user, login_required
from . import tasks
from .celtasks import iterative_simulation
from time import sleep
from .. import celery
from ..models import Task
from ..database import db_session as sess
from celery.task.control import revoke
from celery.signals import task_revoked

@tasks.route('/simul_status/<task_id>')
def simul_status(task_id):
    # returns response to client's AJAX request
    task = iterative_simulation.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 'pending',
            'status': 'Pending...',
            'total': ''
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'status': task.info.get('status', ''),
            'total': task.info.get('total',0)
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'status': task.info.get('status', ''),
            'total': task.info.get('total',0)
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'current': "Failed",
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@tasks.route('/input/<task_id>', methods=['POST'])
def input_foo(task_id):
    Task.query.filter(Task.task_id == task_id).update({"input": "check 1 2"})
    sess.commit()
    return jsonify({}), 202, {'OK': 'whatever'}

@tasks.route('/revoke_foo/<task_id>', methods=['POST'])
def revoke_simulation(task_id):
    return 'revoked'

@tasks.route('/scale_foo/<task_id>', methods=['POST'])
def cancel_simulation(task_id):
    task = foo.AsyncResult(task_id)
    task.update_state(state='KILLED', meta={'killed': True})
    return 'canceled'
                          
