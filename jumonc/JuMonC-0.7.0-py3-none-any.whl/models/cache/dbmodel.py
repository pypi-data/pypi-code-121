import logging

from typing import List

import datetime
from sqlalchemy import Column, Integer, Text, DATETIME, ForeignKey, Float
from sqlalchemy.orm import relationship, Mapped

import sys


from JuMonC import settings
from JuMonC.models.cache.database import Base, db_session
from JuMonC._version import __DB_version__


logger = logging.getLogger(__name__)

class CacheEntry(Base):
    __tablename__ = 'cache_entry'
    query = db_session.query_property()
    cache_id = Column('cache_id', Integer, primary_key=True)
    time = Column('time', DATETIME, unique=False)
    API_path = Column('API_path', Text, unique=False)
    
    parameters:Mapped[List["Parameter"]] = relationship("Parameter",
                                  back_populates="cache_entry",
                                  cascade="all, delete",
                                  passive_deletes=True,
                                  uselist=True
                             )
    
    results_int:Mapped[List["ResultInt"]] = relationship("ResultInt",
                                  back_populates="cache_entry",
                                  cascade="all, delete",
                                  passive_deletes=True,
                                  uselist=True
                             )
    
    results_float:Mapped[List["ResultFloat"]] = relationship("ResultFloat",
                                  back_populates="cache_entry",
                                  cascade="all, delete",
                                  passive_deletes=True,
                                  uselist=True
                             )
    
    results_str:Mapped[List["ResultStr"]] = relationship("ResultStr",
                                  back_populates="cache_entry",
                                  cascade="all, delete",
                                  passive_deletes=True,
                                  uselist=True
                             )

    def __init__(self, API_path:str) -> None:
        """DB class!"""
        self.time = datetime.datetime.now()
        self.API_path = API_path

    def __repr__(self) -> str:
        """DB to string method."""
        if self.time:
            return f'<cache_id {self.cache_id!r}, time {self.time.strftime(settings.DATETIME_FORMAT)!r}, API_path {self.API_path!r}>'
        logging.warning("There is a time value missing in the database for ID: %i", self.cache_id)
        return ""

    
class Parameter(Base):
    __tablename__ = 'parameter'
    query = db_session.query_property()
    cache_id = Column('cache_id', Integer, ForeignKey('cache_entry.cache_id', ondelete="CASCADE"), primary_key=True)
    parameter_name = Column('parameter_name', Text, unique=False, primary_key=True)
    parameter_value = Column('parameter_value', Text, unique=False)
    
    cache_entry:Mapped[CacheEntry] = relationship("CacheEntry", back_populates="parameters", uselist=False)

    def __init__(self, cache_id:int, parameter_name:str, parameter_value:str) -> None:
        """DB class!"""
        self.cache_id = cache_id
        self.parameter_name = parameter_name
        self.parameter_value = parameter_value

    def __repr__(self) -> str:
        """DB to string method."""
        return (f'<cache_id {self.cache_id!r}, '
                f'parameter_name {self.parameter_name!r}, parameter_value {self.parameter_value!r}>')

    
class ResultInt(Base):
    __tablename__ = 'results_int'
    query = db_session.query_property()
    cache_id = Column('cache_id', Integer, ForeignKey('cache_entry.cache_id', ondelete="CASCADE"), primary_key=True)
    result_name = Column('result_name', Text, unique=False, primary_key=True)
    result = Column('result', Integer, unique=False)
    
    cache_entry:Mapped[CacheEntry] = relationship("CacheEntry", back_populates="results_int", uselist=False)

    def __init__(self, cache_id:int, result_name:str, result:int) -> None:
        """DB class!"""
        self.cache_id = cache_id
        self.result_name = result_name
        self.result = result

    def __repr__(self) -> str:
        """DB to string method."""
        return f'<cache_id {self.cache_id!r}, result_name {self.result_name!r}, result {self.result!r}>'

    
class ResultFloat(Base):
    __tablename__ = 'results_float'
    query = db_session.query_property()
    cache_id = Column('cache_id', Integer, ForeignKey('cache_entry.cache_id', ondelete="CASCADE"), primary_key=True)
    result_name = Column('result_name', Text, unique=False, primary_key=True)
    result = Column('result', Float, unique=False)
    
    cache_entry:Mapped[CacheEntry] = relationship("CacheEntry", back_populates="results_float", uselist=False)

    def __init__(self, cache_id:int, result_name:str, result:float) -> None:
        """DB class!"""
        self.cache_id = cache_id
        self.result_name = result_name
        self.result = result

    def __repr__(self) -> str:
        """DB to string method."""
        return f'<cache_id {self.cache_id!r}, result_name {self.result_name!r}, result {self.result!r}>'

    
class ResultStr(Base):
    __tablename__ = 'results_str'
    query = db_session.query_property()
    cache_id = Column('cache_id', Integer, ForeignKey('cache_entry.cache_id', ondelete="CASCADE"), primary_key=True)
    result_name = Column('result_name', Text, unique=False, primary_key=True)
    result = Column('result', Text, unique=False)
    
    cache_entry:Mapped[CacheEntry] = relationship("CacheEntry", back_populates="results_str", uselist=False)

    def __init__(self, cache_id:int, result_name:str, result:str) -> None:
        """DB class!"""
        self.cache_id = cache_id
        self.result_name = result_name
        self.result = result

    def __repr__(self) -> str:
        """DB to string method."""
        return f'<cache_id {self.cache_id!r}, result_name {self.result_name!r}, result {self.result!r}>'

    
class Version(Base):
    __tablename__ = 'version'
    query = db_session.query_property()
    entry = Column('entry', Text, unique=True, primary_key=True)
    value = Column('value', Text, unique=False)

    def __init__(self, entry:str, value:str) -> None:
        """DB class!"""
        self.entry = entry
        self.value = value

    def __repr__(self) -> str:
        """DB to string method."""
        return f'<entry {self.entry!r}, value {self.value!r}>'
    
def check_db_version() -> None:
    logging.debug("Checking DB version")
    db_name = Version.query.filter_by(entry="name").first()
    if db_name:
        if db_name.value == "JuMonC":
            logging.debug("Version table contains the name JuMonC")
        else:
            logging.error(("Version table in db contains the name: %s, that is unexpected."
                            " To prevent JuMonC deleting the database of another projekt,"
                            " JuMonC will stop. DB_PATH: %s"), db_name.name, settings.DB_PATH)
            sys.exit(-2)
    else:
        db_name = Version("name", "JuMonC")
        db_session.add(db_name)
    
    db_version = Version.query.filter_by(entry="DB_version").first()
    if db_version:
        if db_version.value == __DB_version__:
            logging.info("Using exsiting DB with db version: %s", __DB_version__)
        else:
            logging.error(("Version table in db contains the version: %s, that is unexpected."
                            " To prevent JuMonC causing errors in an older version,"
                            " JuMonC will stop. DB_PATH: %s"), db_version.value, settings.DB_PATH)
            sys.exit(-2)
    else:
        db_version = Version("DB_version", __DB_version__)
        logging.info("Creating DB with db version: %s", __DB_version__)
        db_session.add(db_version)
    
    db_session.commit()