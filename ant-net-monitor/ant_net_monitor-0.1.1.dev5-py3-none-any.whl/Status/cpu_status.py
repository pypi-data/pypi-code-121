from datetime import datetime
import psutil
from ..extensions import db
from dataclasses import dataclass


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
    time_stamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
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

    def __init__(self):
        current_status = psutil.cpu_times_percent(interval=1)
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

    def __str__(self):
        return f"user:{self.user_percent}, nice:{self.nice_percent}, system:{self.system_percent}, idle:{self.idle_percent}, iowait:{self.iowait_percent}, irq:{self.irq_percent}, softirq:{self.softirq_percent}, steal:{self.steal_percent}, guest:{self.guest_percent}, guest_nice:{self.guest_nice_percent}"


def save_cpu_status(cpu_status):
    db.session.add(cpu_status)
    db.session.commit()


def get_last_cpu_status():
    return CPUStatus.query.order_by(CPUStatus.time_stamp.desc()).first()


def get_batch_cpu_status():
    # get count of CPUStatus
    count = CPUStatus.query.count()
    if count > 100:
        count = 100
    return CPUStatus.query.order_by(CPUStatus.time_stamp.desc()).limit(count).all()
