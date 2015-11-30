from flask import request, Response
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
