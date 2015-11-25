from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import shutil
import datetime

engine = create_engine(os.environ.get('DEV_DATABASE_URL'), convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def init_users():
    t = datetime.date.today()
    shutil.copytree(src='users', dst='users.bak/{0}'.format(t))
    shutil.rmtree('users')
