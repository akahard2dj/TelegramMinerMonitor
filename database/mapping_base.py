from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

from database.database_engine import DatabaseEngine

db_engine = DatabaseEngine(dbname='database.sqlite')
session = db_engine.session
engine = db_engine.engine
metadata = MetaData(bind=engine)
Base = declarative_base()
