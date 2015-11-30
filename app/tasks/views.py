from flask import jsonify, url_for
from flask.ext.login import current_user
from . import tasks
from .celtasks import foo
from time import sleep
from .. import celery
from ..models import Task
from ..database import db_session as sess
from celery.task.control import revoke
from celery.signals import task_revoked

@tasks.route('/foo_status/<task_id>')
def foostatus(task_id):
    task = foo.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 'pending',
            'status': 'Pending...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'current': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@tasks.route('/foo', methods=['POST'])
def run_foo():
    task = foo.apply_async()
    sess.add(Task(task_id=task.id, user_id=current_user.get_id()))
    sess.commit()
    return jsonify({}), 202, {'Progress': url_for('.foostatus',
                                                  task_id=task.id),
                              'Input': url_for('.input_foo',
                                               task_id=task.id),
                              'Revoke': url_for('.revoke_foo',
                                                task_id=task.id)  }


@tasks.route('/input/<task_id>', methods=['POST'])
def input_foo():
    Task.query.filter(task_id == task_id).update({"input": "check 1 2"})

@tasks.route('/revoke_foo/<task_id>', methods=['POST'])
def revoke_foo(task_id):
    return 'revoked'

@tasks.route('/scale_foo/<task_id>', methods=['POST'])
def scale_foo(task_id):
    return 'scaled'

@tasks.route('/kill_foo/<task_id>')
def kill_foo():
    task = foo.AsyncResult(task_id)
    task.update_state(state='KILLED', meta={'killed': True})

