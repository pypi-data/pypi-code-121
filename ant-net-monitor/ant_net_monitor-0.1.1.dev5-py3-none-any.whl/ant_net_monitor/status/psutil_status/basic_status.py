from datetime import datetime,timedelta
import psutil
from ...extensions import db
from dataclasses import dataclass


@dataclass
class BasicStatus(db.Model):
    id: int
    cpu_percent: float
    ram_percent: float  # The percent of memory used to the system.
    swap_percent: float
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime)
    cpu_percent = db.Column(db.Float)
    ram_percent = db.Column(db.Float)
    swap_percent = db.Column(db.Float)

    def __init__(self):
        self.cpu_percent = psutil.cpu_percent()
        self.ram_percent = psutil.virtual_memory().percent
        self.swap_percent = psutil.swap_memory().percent
        self.time_stamp = datetime.utcnow().replace(microsecond=0)

    def __str__(self):
        return f"cpu:{self.cpu_percent}%, memory:{round(self.ram_percent/(1024**3),2)}G, disk:{round(self.disk/(1024**3),2)}G"

    @staticmethod
    def save(status=None):
        if not status:
            db.session.add(BasicStatus())
        else:
            db.session.add(status)
        db.session.commit()

    @staticmethod
    def get_last():
        start = datetime.utcnow() - timedelta(minutes=1)
        return BasicStatus.query.filter(BasicStatus.time_stamp > start).order_by(BasicStatus.time_stamp.desc()).first()
