#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: model 基类


import uuid
from sqlalchemy import (
    create_engine,
    Column, String,
    and_,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from multitasker.models import constants

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + constants.DB_PATH
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class BaseDB(object):

    """模型基类"""
    __tablename__ = ''
    id = Column(String(32), primary_key=True, default=uuid.uuid4)

    def format(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    def save(self):
        """TODO: Docstring for save.
        :returns: TODO

        """
        self.format()
        session.add(self)
        session.commit()
        return self

    @classmethod
    def find(cls, query):
        """TODO: Docstring for find.

        :**kwargs: TODO
        :returns: TODO

        """
        return session.query(cls).filter_by(**query).all()

    @classmethod
    def find_one(cls, query):
        """TODO: Docstring for find.

        :**kwargs: TODO
        :returns: TODO

        """
        return session.query(cls).filter_by(**query).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.find_one({"id": _id})

    @classmethod
    def insert_many(cls, items):
        """批量插入

        :items: TODO
        :returns: TODO

        """
        session.execute(cls.__table__.insert(), items)
        session.commit()

    @classmethod
    def delete(cls, query):
        """删除

        """
        args = []
        for key, value in query.items():
            k = getattr(cls, key) == value
            args.append(k)
        sql = cls.__table__.delete().where(and_(*args))
        session.execute(sql)
        session.commit()

    @classmethod
    def count(cls, query):
        """TODO: Docstring for count.
        :returns: TODO

        """
        return session.query(cls.id).filter_by(**query).count()

    @classmethod
    def update(cls, query, update_data):
        """修改数据

        :query: TODO
        :update_data: TODO
        :returns: TODO

        """
        for item in cls.find(query):
            for k, v in update_data.items():
                setattr(item, k, v)
            item.save()


    def dict(self):
        return self.__dict__


def init_db():
    """创建数据库
    """
    print("init database")
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    #  Task( url = 'test').save()
    #  for item in Task.find({ "url": 'test' }):
        #  print(item)
        #  print(item.id)
    #  SubTask.update({ "task_id": "1ba2807b-864f-4813-83ee-09ff0be5d7b6" }, {"status": "success"})
