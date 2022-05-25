
from dataclasses import dataclass
from datetime import datetime, timedelta

import psutil
from sqlalchemy import extract

from ...extensions import db


@dataclass
class LoadStatus(db.Model):
    id: int
    load_1: float
    load_5: float
    load_15: float
    time_stamp: datetime  # 需要UTC标准时间，避免Javascript解析时暴毙

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime)
    load_1 = db.Column(db.Float)
    load_5 = db.Column(db.Float)
    load_15 = db.Column(db.Float)

    def __init__(self):
        self.load_1, self.load_5, self.load_15 = psutil.getloadavg()
        self.time_stamp = datetime.utcnow().replace(microsecond=0)

    @staticmethod
    def save(status=None):
        if not status:
            db.session.add(LoadStatus())
        else:
            db.session.add(status)
        db.session.commit()

    @staticmethod
    def get_last():
        start = datetime.utcnow() - timedelta(minutes=1)
        return (
            LoadStatus.query.filter(LoadStatus.time_stamp > start)
            .order_by(LoadStatus.time_stamp.desc())
            .first()
        )

    @staticmethod
    def get_batch():
        count = LoadStatus.query.count()
        if count > 100:
            count = 100
        return (
            LoadStatus.query.order_by(LoadStatus.time_stamp.desc())
            .limit(count)
            .all()[::-1]
        )

    @staticmethod
    def get_in_one_day():
        start = datetime.utcnow() - timedelta(days=1)
        return (
            LoadStatus.query.filter(LoadStatus.time_stamp >= start)
            .filter(extract("minute", LoadStatus.time_stamp) % 5 == 0)
            .filter(extract("second", LoadStatus.time_stamp) == 0)
            .all()
        )
