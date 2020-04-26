from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

engine = create_engine("postgres://omrsibmiyjpkoo:86522c90f799b962a757466e47336ae9af8453782a279a5459864b86567648b0@ec2-52-202-146-43.compute-1.amazonaws.com:5432/d8utk3ksiareqt")
db = scoped_session(sessionmaker(bind=engine))
