import random
from dataclasses import dataclass
from datetime import datetime, timedelta

import psutil
from sqlalchemy import extract

from ...extensions import db


@dataclass
class RAMStatus(db.Model):
    id: int
    free: float  # using GB
    used: float  # using GB
    cached: float  # using GB
    buffers: float  # using GB
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime)
    free = db.Column(db.Float)
    used = db.Column(db.Float)
    cached = db.Column(db.Float)
    buffers = db.Column(db.Float)

    def __init__(self, *, blank=False, time_stamp=None, is_random=False):
        if blank:
            self.free = 0
            self.used = 0
            self.cached = 0
            self.buffers = 0
            self.time_stamp = time_stamp
        elif is_random:
            self.free = format(round(random.uniform(0, 100), 2), ".2f")
            self.used = format(round(random.uniform(0, 100), 2), ".2f")
            self.cached = format(round(random.uniform(0, 100), 2), ".2f")
            self.buffers = format(round(random.uniform(0, 100), 2), ".2f")
            self.time_stamp = time_stamp
        else:
            current_status = psutil.virtual_memory()
            self.free = format(current_status.free / (1024**3), ".2f")
            self.used = format(current_status.used / (1024**3), ".2f")
            self.cached = format(current_status.cached / (1024**3), ".2f")
            self.buffers = format(current_status.buffers / (1024**3), ".2f")
            self.time_stamp = datetime.utcnow().replace(microsecond=0)

    def __str__(self):
        return f"free:{self.free}, used:{self.used}, cached:{self.cached}, buffers:{self.buffers}"

    @staticmethod
    def save(status=None):
        if not status:
            db.session.add(RAMStatus())
        else:
            db.session.add(status)
        db.session.commit()

    @staticmethod
    def get_last():
        start = datetime.utcnow() - timedelta(minutes=1)
        return (
            RAMStatus.query.filter(RAMStatus.time_stamp > start)
            .order_by(RAMStatus.time_stamp.desc())
            .first()
        )

    @staticmethod
    def get_batch():
        count = RAMStatus.query.count()
        if count > 100:
            count = 100
        return (
            RAMStatus.query.order_by(RAMStatus.time_stamp.desc())
            .limit(count)
            .all()[::-1]
        )

    @staticmethod
    def get_in_one_day():
        start = datetime.utcnow() - timedelta(days=1)
        return (
            RAMStatus.query.filter(RAMStatus.time_stamp >= start)
            .filter(extract("minute", RAMStatus.time_stamp) % 5 == 0)
            .filter(extract("second", RAMStatus.time_stamp) == 0)
            .all()
        )
