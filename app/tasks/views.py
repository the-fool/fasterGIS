from flask import jsonify, url_for
from . import tasks
from .celtasks import foo
from time import sleep
from .. import celery
from celery.task.control import revoke
from celery.signals import task_revoked
@tasks.route('/foo_status/<task_id>')
def foostatus(task_id):
    task = foo.AsyncResult(task_id)


   # revoke(task_id, terminate=True)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'status': 'Pending...'
        }
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
    sleep(1)
    print 'revoking'
    celery.control.revoke(task.id, terminate=True)
    return jsonify({}), 202, {'Location': url_for('.foostatus',
                                                  task_id=task.id)}

@tasks.route('/revoke_foo', methods=['POST'])
def revoke_foo():
    return 'revoked'

@task_revoked.connect
def foo_revoked(*args, **kwargs):
    f = open('foo.txt', 'w')
    f.write('foo to you')
    f.close()
    print "I, Foo, was revoked"

