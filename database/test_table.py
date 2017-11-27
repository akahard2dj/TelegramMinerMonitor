from sqlalchemy import (Column, Integer, String)
from database.mapping_base import Base
from database.mapping_base import engine


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __init__(self):
        if not engine.dialect.has_table(engine, self.__tablename__):
            Base.metadata.create_all(engine)

    def __str__(self):
        return "<User('%s', '%s', '%s')>" % (self.name, self.fullname, self.password)

    def set_entry(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password
