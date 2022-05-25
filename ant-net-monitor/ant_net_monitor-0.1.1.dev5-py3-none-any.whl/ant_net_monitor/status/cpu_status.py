from datetime import datetime, timedelta
import psutil
from ..extensions import db
from dataclasses import dataclass
import random
from sqlalchemy import extract


@dataclass
class CPUStatus(db.Model):
    id: int
    user_percent: float
    nice_percent: float
    system_percent: float
    idle_percent: float
    iowait_percent: float
    irq_percent: float
    softirq_percent: float
    steal_percent: float
    guest_percent: float
    guest_nice_percent: float
    time_stamp: datetime  # 需要UTC标准时间，避免Javascript解析时暴毙

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime)
    user_percent = db.Column(db.Float)
    nice_percent = db.Column(db.Float)
    system_percent = db.Column(db.Float)
    idle_percent = db.Column(db.Float)
    iowait_percent = db.Column(db.Float)
    irq_percent = db.Column(db.Float)
    softirq_percent = db.Column(db.Float)
    steal_percent = db.Column(db.Float)
    guest_percent = db.Column(db.Float)
    guest_nice_percent = db.Column(db.Float)

    def __init__(self, *, blank=False, time_stamp=None, is_random=False):
        if blank:
            self.user_percent = 0
            self.nice_percent = 0
            self.system_percent = 0
            self.idle_percent = 0
            self.iowait_percent = 0
            self.irq_percent = 0
            self.softirq_percent = 0
            self.steal_percent = 0
            self.guest_percent = 0
            self.guest_nice_percent = 0
            self.time_stamp = time_stamp
        elif is_random:
            self.user_percent = format(round(random.uniform(0, 100), 2), ".2f")
            self.nice_percent = format(round(random.uniform(0, 100), 2), ".2f")
            self.system_percent = format(round(random.uniform(0, 100), 2), ".2f")
            self.idle_percent = format(round(random.uniform(0, 100), 2), ".2f")
            self.iowait_percent = format(round(random.uniform(0, 100), 2), ".2f")
            self.irq_percent = format(round(random.uniform(0, 100), 2), ".2f")
            self.softirq_percent = format(round(random.uniform(0, 100), 2), ".2f")
            self.steal_percent = format(round(random.uniform(0, 100), 2), ".2f")
            self.guest_percent = format(round(random.uniform(0, 100), 2), ".2f")
            self.guest_nice_percent = format(round(random.uniform(0, 100), 2), ".2f")
            self.time_stamp = time_stamp
        else:
            current_status = psutil.cpu_times_percent()
            self.user_percent = current_status.user
            self.nice_percent = current_status.nice
            self.system_percent = current_status.system
            self.idle_percent = current_status.idle
            self.iowait_percent = current_status.iowait
            self.irq_percent = current_status.irq
            self.softirq_percent = current_status.softirq
            self.steal_percent = current_status.steal
            self.guest_percent = current_status.guest
            self.guest_nice_percent = current_status.guest_nice
            self.time_stamp = datetime.utcnow().replace(microsecond=0)

    def __str__(self):
        return f"user:{self.user_percent}, nice:{self.nice_percent}, system:{self.system_percent}, idle:{self.idle_percent}, iowait:{self.iowait_percent}, irq:{self.irq_percent}, softirq:{self.softirq_percent}, steal:{self.steal_percent}, guest:{self.guest_percent}, guest_nice:{self.guest_nice_percent}"

    @staticmethod
    def save(status=None):
        if not status:
            db.session.add(CPUStatus())
        else:
            db.session.add(status)
        db.session.commit()

    @staticmethod
    def get_last():
        start = datetime.utcnow() - timedelta(minutes=1)
        return CPUStatus.query.filter(CPUStatus.time_stamp >= start).order_by(CPUStatus.time_stamp.desc()).first()

    @staticmethod
    def get_batch():
        count = CPUStatus.query.count()
        if count > 100:
            count = 100
        return (
            CPUStatus.query.order_by(CPUStatus.time_stamp.desc())
            .limit(count)
            .all()[::-1]
        )

    @staticmethod
    def get_in_one_day():
        start = datetime.utcnow() - timedelta(days=1)
        return (
            CPUStatus.query.filter(CPUStatus.time_stamp >= start)
            .filter(extract("minute", CPUStatus.time_stamp) % 5 == 0)
            .filter(extract("second", CPUStatus.time_stamp) == 0)
            .all()
        )
