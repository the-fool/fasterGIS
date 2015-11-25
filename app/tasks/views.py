from flask import jsonify, url_for
from . import tasks
from .celtasks import foo

@tasks.route('/foo_status/<task_id>')
def foostatus(task_id):
    task = foo.AsyncResult(task_id)
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
    return jsonify({}), 202, {'Location': url_for('.foostatus',
                                                  task_id=task.id)}
