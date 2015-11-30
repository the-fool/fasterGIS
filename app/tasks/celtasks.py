from .. import celery
import sys
import os
from subprocess import Popen, PIPE, STDOUT
from celery.signals import task_revoked

@celery.task(bind=True, name='fooboo')
def foo(self):
    task = self.AsyncResult(self.request.id)
    cwd = os.getcwd()
    proc = Popen(['/usr/bin/mpirun','-n', '2', '{0}/app/mpi/simulation'.format(cwd)], stdin=PIPE,
                 stdout=PIPE, stderr=STDOUT)
    while proc.poll() is None:
        if (task.state == 'SCALING'):
            node_num = task.info.get('node_num')
            proc.stdin.write('scale back to {0}'.format(node_num))
            self.update_state(STATE='PROGRESS',
                              meta={'current': 'just scaled'})
        else:
            line = proc.stdout.readline()
            sys.stdout.write(line)
            
            self.update_state(state='PROGRESS',
                              meta={'current': line})
        
    proc.wait()
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 'FINISHED!!'}

@task_revoked.connect
def foo_revoked(*args, **kwargs):
 
    print "I, Foo, was revoked in celtask"
