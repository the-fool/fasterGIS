from .. import celery
from flask.ext.login import current_user
from ..models import Task, Script
from ..database import db_session as sess
import sys
import os
from subprocess import Popen, PIPE, STDOUT
from celery.signals import task_revoked
from datetime import datetime

class Logger():
    flog = None
    def __init__(self, uid=0, tid='x'):
        udir = '/var/www/fastGIS/app/users/{0}/logs'.format(uid)
        self.flog = open(os.path.join(uid,tid), 'w+')
    

@celery.task(bind=True)
def iterative_simulation(self, iterations=1, uid=0):
    nodes = 4
    completed = 0
    tid = self.request.id
    cwd = os.getcwd()
    proc = Popen(['/usr/bin/mpirun','-n', '5', 
                  '{0}/app/mpi/simulation'.format(cwd),
                  str(uid), str(tid), str(iterations)], 
                 stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    state = 'PENDING'
    while True:
        t = Task.query.filter(Task.task_id == tid).first()
      
        if t and t.input:
            sys.stdout.write("Echo to MPI:" + t.input)
            proc.stdin.write("{}\n".format(t.input))
            if t.input == "SHUTDOWN":
                state = "SHUTTING DOWN"
            elif t.input == "PAUSE":
                state = "PAUSED"
            t.input =  None
        else:
            line = proc.stdout.readline()
            if not line: break
            sys.stdout.write(line)
            o = line.split(' ')
            if state not in ("PAUSED", "SHUTTING DOWN") and len(o) > 1:
                if o[1] == 'BEGIN':
                    state = 'PROGRESS'
                elif o[1] == 'COMPLETED':
                    completed += 1
                    state = 'PROGRESS'
                    if completed == nodes * iterations: 
                        proc.stdin.write("FINISHED\n")
                        state = 'FINISHED'
        self.update_state(state=state,
                          meta={'current': completed, 'total': iterations * nodes})
            
        if t: 
            t.status = state
        sess.commit()
    proc.wait()
    if state == "SHUTTING DOWN":
        self.update_state(state="CANCELLED", 
                          meta={'current': completed, 'total': iterations * nodes})
        t.status = "CANCELLED"
        sess.commit()
    return {'current': completed, 'total': iterations * nodes, 'status': 'Finished',
            'result': 'yes'}

@task_revoked.connect
def simul_revoked(*args, **kwargs):
    print "I was revoked in celtask"



def create_simulation(form):
    task = iterative_simulation.delay(iterations=form.iterations.data, 
                                            uid=current_user.get_id())
    sess.add(Task(task_id=task.id, 
                  status=task.status, 
                  user_id=current_user.get_id(), 
                  name=form.name.data,
                  date_begun=datetime.now()))
    sess.add(Script(task_id=task.id, 
                    iterations=form.iterations.data, 
                    type=form.simul_type.data))
    sess.commit()
    
