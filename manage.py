import os
from app import create_app
from flask.ext.script import Manager, Shell
from app.models import User
from app.database import init_db

app = create_app(os.path.abspath("config.py"))
manager = Manager(app)

def make_shell_context():
    return dict(app=app, User=User, init_db=init_db)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
