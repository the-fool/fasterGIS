from flask import after_this_request, request, Response, jsonify, send_from_directory
from flask.ext.login import login_required,  current_user
from . import api
from ..database import db_session as sess
from ..models import User, Task, Result
import json
import zipfile
from datetime import datetime
import os


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


@api.route('/zip_results', methods=['POST'])
def zip_results():
    l = request.get_json()['path']
    fname = os.path.join(os.getcwd(), 'app/users/{0}/results/{1}_{0}'
                         .format(current_user.id, datetime.now().isoformat('_')))  
    Zip = zipfile.ZipFile(fname + '.zip', 'w')
    for x in l:
        Zip.write(x, os.path.basename(x))
    fname = fname.split('results/')[1]  
    return jsonify({"fname": fname}), 202 
    
@api.route('/logs/<task_id>')
def log(task_id):
    path = Task.query.filter(Task.task_id == task_id).first().log
    print path
    with open(path, 'r') as f:
        l = [{'time': x.split(' ')[0].rstrip(']').lstrip('['), 'text': x.split(' ',1)[1].rstrip('\n')} for x in f]
       
    sess.commit()
    return Response(json.dumps(l), content_type='application/json', 
                    mimetype='application/json')

@api.route('/results/<task_id>')
def results(task_id):
    l = [q.serializer for q in  Result.query.filter(Result.task_id == task_id).all()]
    return Response(json.dumps(l), content_type='application/json', 
                    mimetype='application/json')

@api.route('/download/<fname>')
def download(fname):
    path = os.path.join(os.getcwd(),'app/users/{0}/results/'.format(current_user.id))
    @after_this_request
    def remove_file(response):
        os.remove(os.path.join(path, fname + '.zip'))
        return response
    return send_from_directory(path, fname+'.zip', as_attachment=True) 


