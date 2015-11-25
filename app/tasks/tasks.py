from .. import celery

@celery.task
def mult(a, b):
    return a * b
