from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import shutil
import datetime
import errno


engine = create_engine(os.environ.get('DEV_DATABASE_URL'), convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=True,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def init_users():
    t = str(datetime.datetime.utcnow())
    t.replace(' ', '_')
    cwd = os.getcwd()
    try:
        shutil.copytree(src='{0}/app/users'.format(cwd), dst='users.bak/{0}'.format(t))
        shutil.rmtree('{0}/app/users'.format(cwd))
    except OSError as e:
        if e.errno != 2:
            raise
    
