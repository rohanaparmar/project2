from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

engine = create_engine("postgres://username:password@host_name/database_name")
db = scoped_session(sessionmaker(bind=engine))
