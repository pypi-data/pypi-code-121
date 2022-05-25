from dataclasses import dataclass
from datetime import datetime, timedelta

import psutil
from sqlalchemy import extract

from ...extensions import db


@dataclass
class DiskStatus(db.Model):
    id: int
    read_speed: float
    write_speed: float
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    read_speed = db.Column(db.Float)
    write_speed = db.Column(db.Float)
    time_stamp = db.Column(db.DateTime)

    read_bytes = 0
    write_bytes = 0

    def __init__(self):
        read_bytes = psutil.disk_io_counters().read_bytes
        write_bytes = psutil.disk_io_counters().write_bytes
        self.read_speed = format((read_bytes - self.read_bytes) / 1024**2, ".2f")
        self.write_speed = format((write_bytes - self.write_bytes) / 1024**2, ".2f")
        self.time_stamp = datetime.utcnow().replace(microsecond=0)
        DiskStatus.set_counter(read_bytes, write_bytes)

    def __str__(self):
        return f"read_speed:{self.read_speed}, write_speed:{self.write_speed}"

    @classmethod
    def init_counter(cls):
        cls.read_bytes = psutil.disk_io_counters().read_bytes
        cls.write_bytes = psutil.disk_io_counters().write_bytes

    @classmethod
    def set_counter(cls, read_bytes, write_bytes):
        cls.read_bytes = read_bytes
        cls.write_bytes = write_bytes

    @classmethod
    def save(cls, status=None):
        if not status:
            db.session.add(cls())
        else:
            db.session.add(status)
        db.session.commit()

    @classmethod
    def get_last(cls):
        start = datetime.utcnow() - timedelta(minutes=1)
        return (
            DiskStatus.query.filter(DiskStatus.time_stamp > start)
            .order_by(DiskStatus.time_stamp.desc())
            .first()
        )

    @classmethod
    def get_batch(cls):
        count = DiskStatus.query.count()
        if count > 100:
            count = 100
        return (
            DiskStatus.query.order_by(DiskStatus.time_stamp.desc())
            .limit(count)
            .all()[::-1]
        )

    @classmethod
    def get_in_one_day(cls):
        start = datetime.utcnow() - timedelta(days=1)
        return (
            DiskStatus.query.filter(DiskStatus.time_stamp >= start)
            .filter(extract("minute", DiskStatus.time_stamp) % 5 == 0)
            .filter(extract("second", DiskStatus.time_stamp) == 0)
            .all()
        )
