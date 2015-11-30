from .. import celery
from flask.ext.login import current_user
from ..models import Task
from ..database import db_session as sess
import sys
import os
from subprocess import Popen, PIPE, STDOUT
from celery.signals import task_revoked
from datetime import datetime

@celery.task(bind=True)
def iterative_simulation(self):
    cwd = os.getcwd()
    proc = Popen(['/usr/bin/mpirun','-n', '2', 
                  '{0}/app/mpi/simulation'.format(cwd)], 
                 stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    while proc.poll() is None:
        t = Task.query.filter(Task.task_id == self.request.id).first()
        
        if t and t.input:
            sys.stdout.write("got an input:" + t.input)
            proc.stdin.write("{}\n".format(t.input))
            t.input =  None
            self.update_state(state='PROGRESS',
                              meta={'current': 'just scaled'})
        else:
            line = proc.stdout.readline()
            sys.stdout.write(line)
            self.update_state(state='PROGRESS',
                              meta={'current': line})
        sess.commit()
    proc.wait()
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 'FINISHED!!'}

@task_revoked.connect
def simul_revoked(*args, **kwargs):
    print "I was revoked in celtask"

def create_simulation(form):
    task = iterative_simulation.apply_async()
    sess.add(Task(task_id=task.id, status=task.status, 
                  user_id=current_user.get_id(), name=form.name.data,
                  date_begun=datetime.now()))
    sess.commit()

