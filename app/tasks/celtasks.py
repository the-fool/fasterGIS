from .. import celery
import sys
import os
import subprocess
from celery.signals import task_revoked

@celery.task(bind=True)
def foo(self):
    cwd = os.getcwd()
    proc = subprocess.Popen('{0}/long'.format(cwd),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while proc.poll() is None:
        line = proc.stdout.readline()
        sys.stdout.write(line)
        self.update_state(state='PROGRESS',
                          meta={'current': line})
    proc.wait()
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 'FINISHED!!'}

@task_revoked.connect(sender='foo')
def foo_revoked(*args, **kwargs):
    print "I, Foo, was revoked"
