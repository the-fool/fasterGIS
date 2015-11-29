from .. import celery
import sys
import os
import subprocess
from celery.signals import task_revoked

@celery.task(bind=True, name='fooboo')
def foo(self):
    task = self.AsyncResult(self.request.id)
    cwd = os.getcwd()
    proc = subprocess.Popen('{0}/long'.format(cwd),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while proc.poll() is None:
        if (task.state == 'SCALING'):
            node_num = task.info.get('node_num')
            proc.communicate(input='scale back to {0}'.format(node_num))
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
