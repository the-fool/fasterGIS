"""
Main module for Celery's task logic
"""

from .. import celery
from flask.ext.login import current_user
from ..models import Task, Script, Result
from ..database import db_session as sess
import sys
import os
from time import sleep
from subprocess import Popen, PIPE, STDOUT
from celery.signals import task_revoked
from datetime import datetime

"""
Logger and Persister just take care of encapsulating some basic
functions of the Celery worker
"""
class Logger():
    flog = None
    def __init__(self, uid=0, tid='x'):
        udir = '{0}/app/users/{1}/logs'.format(os.getcwd(), uid)
        self.flog = open(os.path.join(udir,tid), 'w+', 0)
        self.uid = uid
        self.tid = tid
        
    def log(self, line=' '):
        if line[0] == 'P':
            self.flog.write('[{0}] {1}'.format(
                datetime.now().isoformat(), line))

    def close(self):
        self.flog.close()

class Persister():
    udir = None
    def __init__(self, uid=0, tid='x'):
        self.udir = '{0}/app/users/{1}/results'.format(os.getcwd(), uid)
        self.uid = uid
        self.tid = tid
    
    def persist(self, fname):
        path = os.path.join(self.udir, fname)
        sess.add(Result(path=path, name=fname, task_id=self.tid))
        sess.commit()
        

@celery.task(bind=True)
def iterative_simulation(self, iterations=1, uid=0, 
                         simtype='SGS', data_set=''):
    
    nodes = 4 # Hard-coded num of mpi nodes
    completed = 0 # number of simulations run
    tid = self.request.id
    logger = Logger(uid=uid, tid=tid)
    persister = Persister(uid=uid, tid=tid)
    cwd = os.getcwd()
    # Execute simulation with piped i/o
    proc = Popen(['/usr/bin/mpirun','-n', str(nodes + 1), 
                  '{0}/app/mpi/simulation'.format(cwd),
                  str(uid), str(tid), str(iterations), str(simtype), data_set],  
                 stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    state = 'PENDING'
    while True:
        # poll server for messages from client
        if state not in ('SHUTTING DOWN', 'FINISHED'):
            t = Task.query.filter(Task.task_id == tid).first()
        if t and t.input:
            sys.stdout.write("Echo to MPI:" + t.input)
            proc.stdin.write("{}\n".format(t.input))
            if t.input == "SHUTDOWN":
                state = "SHUTTING DOWN"
            elif t.input == "PAUSE":
                state = "PAUSED"
            t.input =  None
        # if no messages, proceed as normal
        else:
            line = proc.stdout.readline()
            if not line: break # EOF

            sys.stdout.write(line)
            logger.log(line=line)

            o = line.split(' ')
            # Do not update state if in shut-down sequence
            if state not in ('PAUSED', 'SHUTTING DOWN', 'FINISHED') and len(o) > 1:
                if o[1] == 'BEGIN':
                    state = 'PROGRESS'
                elif o[1] == 'COMPLETED':
                    completed += 1
                    persister.persist(o[2].rstrip('\n'))
                    state = 'PROGRESS'
                    if completed == iterations: 
                        proc.stdin.write("FINISHED\n")
                        state = 'FINISHED'
        self.update_state(state=state,
                          meta={'current': completed, 'total': iterations})
            
        if t: # safety check in case db access failed 
            t.status = state
        sess.commit()
    proc.wait() # collect child

    if state == "SHUTTING DOWN":
        state = "CANCELLED"
        self.update_state(state=state, 
                          meta={'current': completed, 'total': iterations})
        t.status = state
    
    # clean up and exit
    logger.close()
    t.date_done = datetime.now()
    sess.commit()
    sess.remove()

    return {'current': completed, 'total': iterations, 'status': state,
            'result': state}

@task_revoked.connect
def simul_revoked(*args, **kwargs):
    # log revocation
    print "I was revoked in celtask"


    
