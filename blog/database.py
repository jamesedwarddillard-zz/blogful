from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from blog import app

engine = create_engine(app.config["SQLALCHEMY_DATAASE_URI"])
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()