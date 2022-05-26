# -*- coding:utf-8 -*-
from __future__ import absolute_import

import datetime
import sqlite3

import hashlib
import io
import numpy as np
import os
from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint, Text, Boolean, DateTime, BINARY
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ..basic_tools.md5_tools import get_md5

Base = declarative_base()


def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())  # todo only support sqlite3 ?


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


def get_sqlite_engine(sqlite_file="tmp.dat"):
    """

    :rtype: Engine
    """
    return create_engine("sqlite:///{}".format(os.path.abspath(sqlite_file)),
                         echo=False).connect()


def get_sqlite_session(engine) -> Session:
    return sessionmaker(bind=engine)()


class RecordMixin(object):
    """保存account 信息"""

    # global var
    sqlite_file = "sqlite.dat"
    NULL_TIME = datetime.datetime(2000, 1, 1, 0, 0, 0)
    _engine = None

    @classmethod
    def create_table_by_code(cls):
        """
        创建表格
        :rtype: None
        """
        cls.__table__.create(cls.get_engine())

    @classmethod
    def get_engine(cls):
        """

        :rtype: Engine
        """
        if cls._engine is None:
            cls._engine = get_sqlite_engine(sqlite_file=cls.sqlite_file)

        return cls._engine

    @classmethod
    def get_new_session(cls) -> Session:
        return get_sqlite_session(engine=get_sqlite_engine(sqlite_file=cls.sqlite_file))

    @classmethod
    def destroy_new_session(cls, db_session: Session):
        if db_session is None:
            return
        db_session.bind.close()
        db_session.close()

    @classmethod
    def close_engine(cls):
        if cls._engine:
            cls._engine.close()
            cls._engine = None

    @classmethod
    def get_session(cls) -> Session:
        return get_sqlite_session(cls.get_engine())

    @classmethod
    def init_table_object(cls):
        if not cls.is_table_exists():
            cls.create_table_by_code()

    @classmethod
    def is_table_exists(cls):
        engine = cls.get_engine()
        return engine.dialect.has_table(engine.connect(), cls.__tablename__)


class FeatureRecord(Base, RecordMixin):
    """保存account 信息"""
    __tablename__ = 'feature'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    # pk
    id = Column(String(32), nullable=False, primary_key=True)
    image_id = Column(String(32))
    label = Column(Integer)
    feature = Column(BINARY)

    TEST_LABEL = -1

    @classmethod
    def get_info(cls, db_session: Session) -> (int, int):
        all_count = db_session.query(cls).count()
        assert isinstance(all_count, int)

        test_count = db_session.query(cls).filter(cls.label == cls.TEST_LABEL).count()
        assert isinstance(test_count, int)

        return all_count - test_count, test_count

    @classmethod
    def create_uid(cls, image_id: str, is_train: bool) -> str:
        raw = "{}:{}".format(image_id, is_train)
        return get_md5(raw.encode("utf-8"))

    @classmethod
    def add_feature(cls, db_session: Session, label: int, feature: np.ndarray, image_id: str):
        uid = cls.create_uid(image_id=image_id, is_train=bool(label != cls.TEST_LABEL))
        obj = db_session.query(cls).filter(cls.id == uid).first()
        if not obj:
            obj = cls()
            obj.id = uid

        obj.label = label
        obj.feature = adapt_array(feature)
        obj.image_id = image_id
        db_session.add(obj)
        db_session.commit()
        return obj

    @classmethod
    def list_feature(cls, db_session: Session, uid_list: list) -> list:
        result = db_session.query(cls).filter(cls.id.in_(uid_list))
        result_list = []
        for obj in result:
            result_list.append((obj.id, obj.image_id, obj.label, convert_array(obj.feature)))

        return result_list

    @classmethod
    def get_feature(cls, db_session: Session, uid: str):
        obj = db_session.query(cls).filter(cls.id == uid).first()
        if obj:
            return obj.id, obj.image_id, obj.label, convert_array(obj.feature)
        return None


class SpiderRecord(Base, RecordMixin):
    """保存account 信息"""
    __tablename__ = 'spider_record'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
    )

    # pk
    id = Column(Integer)
    uid = Column(String(32), nullable=False, unique=True)

    # record
    class_name = Column(String(128))
    url = Column(Text)
    added_time = Column(DateTime, nullable=False)
    account_count = Column(Integer)
    last_crawled_time = Column(DateTime, nullable=False)
    next_crawled_time = Column(DateTime, nullable=False)
    crawled_every_seconds = Column(Integer)

    # deleted_status
    deleted = Column(Boolean, default=False)
    fail_count = Column(Integer, default=0)
    MAX_FAIL_COUNT = 5

    # default crawl every_seconds
    CRAWLED_EVERY_SECONDS = 300

    @classmethod
    def get_next_task(cls, db_session):
        """

        :rtype: SpiderRecord|None
        :type db_session: Session
        """
        time_now = datetime.datetime.now()

        return db_session.query(cls) \
            .filter(cls.deleted == False, cls.next_crawled_time <= time_now) \
            .order_by(cls.next_crawled_time.asc()) \
            .first()

    @classmethod
    def recrawl_all_tasks(cls, db_session):
        """
        :type db_session: Session
        """
        time_now = datetime.datetime.now()

        db_session.query(cls) \
            .filter(cls.deleted == False, cls.next_crawled_time > time_now) \
            .update(dict(next_crawled_time=time_now))

        db_session.commit()

    @classmethod
    def from_target_url(cls, db_session, target_url):
        """

        :type db_session: Session
        :rtype: (SpiderRecord, is_created)
        :type target_url: str
        """
        class_name = "function"
        url = target_url.rstrip("/")

        hash_md5 = hashlib.md5("{}:{}".format(class_name, url).encode("utf-8"))
        uid = hash_md5.hexdigest()

        instance = db_session.query(cls).filter_by(uid=uid).first()
        if instance is None:
            now = datetime.datetime.now()
            instance = cls()
            instance.uid = uid
            instance.class_name = class_name
            instance.url = url
            instance.added_time = now
            instance.account_count = 0
            instance.last_crawled_time = cls.NULL_TIME
            instance.next_crawled_time = now
            instance.crawled_every_seconds = cls.CRAWLED_EVERY_SECONDS
            instance.deleted = False
            instance.fail_count = 0
            return instance, True
        else:
            return instance, False

    def commit_crawled_record(self, db_session, is_success=True):
        """

        :type is_success: bool
        :type db_session: Session
        """
        self.last_crawled_time = datetime.datetime.now()
        self.next_crawled_time = self.last_crawled_time \
                                 + datetime.timedelta(seconds=self.crawled_every_seconds)
        if is_success:
            self.fail_count = 0
        else:
            self.fail_count += 1
            if self.fail_count > self.MAX_FAIL_COUNT:
                self.deleted = True

        db_session.add(self)
        db_session.commit()

    @classmethod
    def delete_all_tasks(cls, db_session):
        """
        将所有使用中的账号设置为未使用
        :rtype: bool
        """
        db_session.query(cls) \
            .filter_by(deleted=False) \
            .update(dict(deleted=True))
        db_session.commit()

    @classmethod
    def reactive_task(cls, instance):
        now = datetime.datetime.now()
        instance.next_crawled_time = now
        instance.deleted = False
        instance.fail_count = 0


__all__ = ("Base", "get_sqlite_engine", "get_sqlite_session", "RecordMixin",
           "FeatureRecord", "adapt_array", "convert_array")
