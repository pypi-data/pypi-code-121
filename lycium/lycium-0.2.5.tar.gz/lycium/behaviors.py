#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import time
from sqlalchemy import Column, SmallInteger, String, BigInteger
import flask

def get_current_ts():
    return int(time.time()*1000)

def get_current_uid():
    if flask.session:
        return str(flask.session.get('uid', ''))
    return ''

class AppBehevior(object):
    """
    接入方相关字段定义
    """
    app_id = Column('app_id', String(50), index=True, nullable=False)

class ModifyingBehevior(object):
    """
    修改相关字段定义
    """
    obsoleted = Column('obsoleted', SmallInteger, default=0, comment='废弃标志 0:正常 1:废弃')
    created_at = Column('created_at', BigInteger, default=get_current_ts, comment='创建时间戳（毫秒）')
    updated_at = Column('updated_at', BigInteger, default=get_current_ts, onupdate=get_current_ts, comment='更新时间戳（毫秒）')
    created_by = Column('created_by', String(50), default=get_current_uid, comment='创建者用户ID')
    updated_by = Column('updated_by', String(50), default=get_current_uid, onupdate=get_current_uid, comment='更新者用户ID')
