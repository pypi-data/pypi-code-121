from sqlalchemy.ext.automap import automap_base
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint,
    Float,
    BLOB,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref

from .models import (
    AlphaTable,
    AlphaTableId,
    AlphaColumn,
    AlphaFloat,
    AlphaInteger,
    AlphaTableIdUpdateDate,
    AlphaTableUpdateDate,
)

import datetime, inspect, ast

from core import core

db = core.db
ma = core.ma


class FilesProcess(db.Model, AlphaTableUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "files_process"
    ensure = True

    name = AlphaColumn(String(40), nullable=False, primary_key=True)
    key = AlphaColumn(String(100), nullable=False, primary_key=True)
    filename = AlphaColumn(String(100), nullable=False, primary_key=True)
    modifiation_time = AlphaColumn(Integer)
    filesize = AlphaColumn(Integer)
    lifetime = AlphaColumn(Integer)
    error = AlphaColumn(Integer)


class Processes(db.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "processes"

    uuid = AlphaColumn(String(36))
    name = AlphaColumn(String(20), primary_key=True)
    parameters = AlphaColumn(String(20), primary_key=True)
    status = AlphaColumn(String(5))

    __table_args__ = (
        UniqueConstraint("name", "parameters", name="processes_constraint"),
    )


class Logs(db.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "logs"

    level = AlphaColumn(String(6), primary_key=True)
    type_ = AlphaColumn(String(30), primary_key=True)
    origin = AlphaColumn(String(30), primary_key=True)
    message = AlphaColumn(Text, primary_key=True)
    stack = AlphaColumn(Text)


class Tests(db.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "tests"

    category = AlphaColumn(String(50), primary_key=True)
    tests_group = AlphaColumn(String(50), primary_key=True)
    name = AlphaColumn(String(50), primary_key=True)

    status = AlphaColumn(Integer)
    start_time = AlphaColumn(DateTime)
    end_time = AlphaColumn(DateTime)
    elapsed = AlphaColumn(Float)


class Request(db.Model, AlphaTable):
    __bind_key__ = "main"
    __tablename__ = "request"

    index = AlphaColumn(Integer, primary_key=True, autoincrement=True)
    response_time = AlphaColumn(Float)
    date = AlphaColumn(DateTime)
    method = AlphaColumn(String(6))
    size = AlphaColumn(Integer)
    status_code = AlphaColumn(Integer)
    path = AlphaColumn(String(100))
    user_agent = AlphaColumn(String(200))
    remote_address = AlphaColumn(String(20))
    exception = AlphaColumn(String(500))
    referrer = AlphaColumn(String(100))
    browser = AlphaColumn(String(100))
    platform = AlphaColumn(String(20))
    mimetype = AlphaColumn(String(30))


class NewsLetter(db.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "newsletter"
    name = AlphaColumn(String(100), primary_key=True)
    mail = AlphaColumn(String(50), primary_key=True)


class Test(db.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "test"

    id = AlphaColumn(Integer, autoincrement=True)

    name_ = AlphaColumn(String(30), primary_key=True)
    text_ = AlphaColumn(String(300))
    number_ = AlphaColumn(Integer)
    date_ = AlphaColumn(DateTime)

    __table_args__ = (db.UniqueConstraint("name_", name="test_name"),)


class Log(db.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "log"

    type = AlphaColumn(String(30), primary_key=True)
    origin = AlphaColumn(String(30), primary_key=True)
    message = AlphaColumn(Text, primary_key=True)
    stack = AlphaColumn(Text)


class ProcesseLog(db.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "process_log"

    uuid = AlphaColumn(String(36))
    name = AlphaColumn(String(20), primary_key=True)
    parameters = AlphaColumn(String(100), primary_key=True)
    status = AlphaColumn(String(5))


class MailHistory(db.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "mail_history"

    uuid = AlphaColumn(String(50))
    mail_type = AlphaColumn(String(250), primary_key=True)
    parameters = AlphaColumn(String(200), primary_key=True)
    parameters_full = AlphaColumn(String(500), primary_key=True)
    date = AlphaColumn(DateTime)


class MailBlacklist(db.Model, AlphaTableId):
    __bind_key__ = "main"
    __tablename__ = "mail_blacklist"
    __table_args__ = (
        UniqueConstraint("mail", "mail_type", name="unique_component_commit"),
    )

    mail = AlphaColumn(String(50), primary_key=True)
    mail_type = AlphaColumn(String(20), primary_key=True)


class Requests(db.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "requests"

    uuid = AlphaColumn(String(100))
    process = AlphaColumn(Integer, primary_key=True)
    message = AlphaColumn(Text, primary_key=True)
    message_type = AlphaColumn(String(20))
    lifetime = AlphaColumn(Integer)
    creation_date = AlphaColumn(DateTime, default=datetime.datetime.now)


class Answers(db.Model, AlphaTableIdUpdateDate):
    __bind_key__ = "main"
    __tablename__ = "answers"

    uuid = AlphaColumn(String(100))
    process = AlphaColumn(Integer, primary_key=True)
    message = AlphaColumn(Text, primary_key=True)
    message_type = AlphaColumn(String(20))
    lifetime = AlphaColumn(Integer)
    creation_date = AlphaColumn(DateTime, default=datetime.datetime.now)


class Constants(db.Model, AlphaTableUpdateDate):
    __tablename__ = "constants"
    __bind_key__ = "main"

    __table_args__ = (UniqueConstraint("name", name="constant_name"),)

    name = AlphaColumn(String(30), primary_key=True)
    value = AlphaColumn(String(100))


class Parameters(db.Model, AlphaTableUpdateDate):
    __tablename__ = "parameters"
    __bind_key__ = "main"

    __table_args__ = (UniqueConstraint("name", name="parameter_name"),)

    name = AlphaColumn(String(30), primary_key=True)
    value = AlphaColumn(Text)
