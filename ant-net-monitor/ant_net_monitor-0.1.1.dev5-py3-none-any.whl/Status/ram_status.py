from datetime import datetime
import psutil
from ..extensions import db
from dataclasses import dataclass


@dataclass
class RAMStatus(db.Model):
    id: int
    available: float  # using GB
    used: float  # using GB
    cached: float  # using GB
    buffers: float  # using GB
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    available = db.Column(db.Float)
    used = db.Column(db.Float)
    cached = db.Column(db.Float)
    buffers = db.Column(db.Float)

    def __init__(self):
        current_status = psutil.virtual_memory()
        self.available = format(current_status.free / (1024 ** 3), ".2f")
        self.used = format(current_status.used / (1024 ** 3), ".2f")
        self.cached = format(current_status.cached / (1024 ** 3), ".2f")
        self.buffers = format(current_status.buffers / (1024 ** 3), ".2f")

    def __str__(self):
        return f"free:{self.available}, used:{self.used}, cached:{self.cached}, buffers:{self.buffers}"


def save_ram_status(ram_status):
    db.session.add(ram_status)
    db.session.commit()


def get_last_ram_status():
    return RAMStatus.query.order_by(RAMStatus.time_stamp.desc()).first()


def get_batch_ram_status():
    count = RAMStatus.query.count()
    if count > 100:
        count = 100
    return RAMStatus.query.order_by(RAMStatus.time_stamp.desc()).limit(count).all()
