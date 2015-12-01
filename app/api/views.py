from flask import request, Response, jsonify
from flask.ext.login import login_required,  current_user
from . import api
from ..database import db_session as sess
from ..models import User, Task
import json

@api.route('/tasks')
def tasks():
    f = request.args.get('filter')
    if f:
        f = f.split('_')
        l = [q.serializer for q in Task.query.filter(Task.user_id == f[1]).all()]
    else:
        l = [q.serializer for q in Task.query.all()]
    return Response(json.dumps(l), content_type='application/json', 
                    mimetype='application/json')

@api.route('/shutdown', methods=['POST'])
def shutdown():
    for x in request.get_json()['tid']:
       t =  Task.query.filter(Task.task_id == x).first()
       t.input = "SHUTDOWN"
       t.status = "Shutting Down"
       sess.commit()
       print "Shutdown ", t.name
    return jsonify({"Success": "very"}), 202 
    
@api.route('/logs/<task_id>')
def log(task_id):
    path = Task.query.filter(Task.task_id == task_id).first().log
    print path
    with open(path, 'r') as f:
        l = [{'time': x.split(' ')[0].rstrip(']').lstrip('['), 'text': x.split(' ',1)[1].rstrip('\n')} for x in f]
       
    sess.commit()
    return Response(json.dumps(l), content_type='application/json', 
                    mimetype='application/json')
