from .. import celery
import sys
import os
import subprocess
from celery.signals import task_revoked

@celery.task(bind=True, name='fooboo')
def foo(self):
    cwd = os.getcwd()
    proc = subprocess.Popen('{0}/long'.format(cwd),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while proc.poll() is None:
        line = proc.stdout.readline()
        sys.stdout.write(line)
       # if fooboo.id != 'KILLED':
       self.update_state(state='PROGRESS',
                              meta={'current': line})
        else:
            proc.terminate()
    proc.wait()
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 'FINISHED!!'}

@task_revoked.connect
def foo_revoked(*args, **kwargs):
    f = open('foo.txt','w')
    f.write('celtasks')
    f.close()
    print "I, Foo, was revoked in celtask"
