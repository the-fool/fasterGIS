from .. import celery
from flask.ext.login import current_user
from ..models import Task, Script
from ..database import db_session as sess
import sys
import os
from subprocess import Popen, PIPE, STDOUT
from celery.signals import task_revoked
from datetime import datetime


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

    while True:
        t = Task.query.filter(Task.task_id == tid).first()
        
        if t and t.input:
            sys.stdout.write("Echo to MPI:" + t.input)
            proc.stdin.write("{}\n".format(t.input))
            if t.input == "SHUTDOWN":
                state = "SHUTTING DOWN"
            self.update_state(state=state)
            t.input =  None
        else:
            line = proc.stdout.readline()
            if not line: break
            sys.stdout.write(line)
            
            o = line.split(' ')
            if o[1] and o[1] == 'COMPLETED': 
                completed += 1
                if completed == nodes * iterations: proc.stdin.write("FINISHED\n")
            self.update_state(state='PROGRESS',
                              meta={'current': completed, 'total': iterations * nodes})
            if t: 
                t.status = "PROGRESS"
        sess.commit()
    proc.wait()
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 'FINISHED!!'}

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

