import os
from app import celery, create_app

app = create_app(os.path.abspath("config.py"))
app.app_context().push()
