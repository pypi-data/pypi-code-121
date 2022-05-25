from dataclasses import dataclass
from datetime import datetime, timedelta

import psutil
from sqlalchemy import extract

from ...extensions import db


@dataclass
class InterruptStatus(db.Model):
    id: int
    interrupt: int
    soft_interrupt: int
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    interrupt = db.Column(db.Integer)
    soft_interrupt = db.Column(db.Integer)
    time_stamp = db.Column(db.DateTime)

    total_interrupt = 0
    total_soft_interrupt = 0

    def __init__(self):
        total_interrupt = psutil.cpu_stats().interrupts
        total_soft_interrupt = psutil.cpu_stats().soft_interrupts
        self.interrupt = format(total_interrupt - self.total_interrupt, ".2f")
        self.soft_interrupt = format(total_soft_interrupt - self.total_soft_interrupt, ".2f")
        self.time_stamp = datetime.utcnow().replace(microsecond=0)
        InterruptStatus.set_counter(total_interrupt, total_soft_interrupt)

    def __str__(self):
        return f"interrupt:{self.interrupt}, soft_interrupt:{self.soft_interrupt}"

    @classmethod
    def init_counter(cls):
        cls.total_interrupt = psutil.cpu_stats().interrupts
        cls.total_soft_interrupt = psutil.cpu_stats().soft_interrupts

    @classmethod
    def set_counter(cls, total_interrupt, total_soft_interrupt):
        cls.total_interrupt = total_interrupt
        cls.total_soft_interrupt = total_soft_interrupt

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
            InterruptStatus.query.filter(InterruptStatus.time_stamp > start)
            .order_by(InterruptStatus.time_stamp.desc())
            .first()
        )

    @classmethod
    def get_batch(cls):
        count = cls.query.count()
        if count > 100:
            count = 100
        return (
            cls.query.order_by(cls.time_stamp.desc())
            .limit(count)
            .all()[::-1]
        )

    @classmethod
    def get_in_one_day(cls):
        start = datetime.utcnow() - timedelta(days=1)
        return (
            cls.query.filter(cls.time_stamp >= start)
            .filter(extract("minute", cls.time_stamp) % 5 == 0)
            .filter(extract("second", cls.time_stamp) == 0)
            .all()
        )
