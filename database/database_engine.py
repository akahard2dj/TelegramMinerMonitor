import os

from sqlalchemy import create_engine
from sqlalchemy.orm import (scoped_session, sessionmaker)


class DatabaseEngine(object):
    def __init__(self, **kwargs):
        self.__dbname = str()
        self.__base_dir = os.getcwd()

        self._check_parameters(**kwargs)

        create_engine_msg = 'sqlite:///{}'.format(os.path.join(self.__base_dir, self.__dbname))

        self._engine = create_engine(create_engine_msg, convert_unicode=True, encoding='utf-8')
        self._session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self._engine))

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._session

    def _check_parameters(self, **kwargs):
        if 'dbname' in kwargs:
            self.__dbname = kwargs['dbname']
