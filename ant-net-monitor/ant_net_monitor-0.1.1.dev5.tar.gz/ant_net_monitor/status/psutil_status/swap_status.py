from dataclasses import dataclass
from datetime import datetime, timedelta

import psutil
from sqlalchemy import extract

from ...extensions import db


@dataclass
class SwapStatus(db.Model):
    id: int
    used: int
    # percent: float #不需要包裹在JSON中
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime)
    used = db.Column(db.Float)
    percent = db.Column(db.Float)

    def __init__(self):
        self.used = format(psutil.swap_memory().used / 1024**3, '.2f')
        self.percent = psutil.swap_memory().percent
        self.time_stamp = datetime.utcnow().replace(microsecond=0)

    @staticmethod
    def save(status=None):
        if not status:
            db.session.add(SwapStatus())
        else:
            db.session.add(status)
        db.session.commit()

    @staticmethod
    def get_last():
        start = datetime.utcnow() - timedelta(minutes=1)
        return (
            SwapStatus.query.filter(SwapStatus.time_stamp > start)
            .order_by(SwapStatus.time_stamp.desc())
            .first()
        )

    @staticmethod
    def get_batch():
        count = SwapStatus.query.count()
        if count > 100:
            count = 100
        return (
            SwapStatus.query.order_by(SwapStatus.time_stamp.desc())
            .limit(count)
            .all()[::-1]
        )

    @staticmethod
    def get_in_one_day():
        start = datetime.utcnow() - timedelta(days=1)
        return (
            SwapStatus.query.filter(SwapStatus.time_stamp >= start)
            .filter(extract("minute", SwapStatus.time_stamp) % 5 == 0)
            .filter(extract("second", SwapStatus.time_stamp) == 0)
            .all()
        )
