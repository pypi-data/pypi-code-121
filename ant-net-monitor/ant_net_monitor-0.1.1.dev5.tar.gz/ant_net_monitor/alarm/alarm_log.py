from dataclasses import dataclass
from datetime import datetime, timedelta

from ..extensions import db


@dataclass
class AlarmLog(db.Model):
    id: int
    name: str
    status: str
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    status = db.Column(db.String(64))
    time_stamp = db.Column(db.DateTime)

    def __init__(self, name, status):
        self.name = name
        self.status = status
        self.time_stamp = datetime.utcnow().replace(microsecond=0)

    @classmethod
    def save(cls, name, status):
        alarm_log = cls(name, status)
        db.session.add(alarm_log)
        db.session.commit()

    @classmethod
    def get_in_one_day(cls):
        return cls.query.filter(
            cls.time_stamp
            >= datetime.utcnow().replace(microsecond=0) - timedelta(days=1)
        ).all()
