from sqlalchemy import (Column, Integer, String, Date, Float)
from database.mapping_base import Base
from database.mapping_base import engine


class MiningHistory(Base):
    __tablename__ = 'mininghistory'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Date)
    currency = Column(String)
    amount = Column(Float)
    amount_btc = Column(Float)

    def __init__(self):
        if not engine.dialect.has_table(engine, self.__tablename__):
            Base.metadata.create_all(engine)
