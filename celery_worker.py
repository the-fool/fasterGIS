import os
from app import celery, create_app, init_celery

app = create_app(os.path.abspath("config.py"))
app.app_context().push()

celery = init_celery(app)
