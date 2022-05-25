from datetime import datetime, timedelta
import psutil
from ..extensions import db
from dataclasses import dataclass
from sqlalchemy import extract


@dataclass
class NetworkStatus(db.Model):
    id: int
    send_speed: float
    recv_speed: float
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    send_speed = db.Column(db.Float)
    recv_speed = db.Column(db.Float)
    time_stamp = db.Column(db.DateTime)

    send_bytes = 0
    recv_bytes = 0

    def __init__(self):
        send_bytes = psutil.net_io_counters().bytes_sent
        recv_bytes = psutil.net_io_counters().bytes_recv
        self.send_speed = format((send_bytes - self.send_bytes) / 1024 ** 2, ".2f")
        self.recv_speed = format((recv_bytes - self.recv_bytes) / 1024 ** 2, ".2f")
        self.time_stamp = datetime.utcnow().replace(microsecond=0)
        NetworkStatus.set_counter(send_bytes, recv_bytes)

    def __str__(self):
        return f"send_speed:{self.send_speed}, recv_speed:{self.recv_speed}"

    @classmethod
    def init_counter(cls):
        cls.send_bytes = psutil.net_io_counters().bytes_sent
        cls.recv_bytes = psutil.net_io_counters().bytes_recv

    @classmethod
    def set_counter(cls, send_bytes, recv_bytes):
        cls.send_bytes = send_bytes
        cls.recv_bytes = recv_bytes

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
            NetworkStatus.query.filter(NetworkStatus.time_stamp > start)
            .order_by(NetworkStatus.time_stamp.desc())
            .first()
        )

    @classmethod
    def get_batch(cls):
        count = NetworkStatus.query.count()
        if count > 100:
            count = 100
        return (
            NetworkStatus.query.order_by(NetworkStatus.time_stamp.desc())
            .limit(count)
            .all()[::-1]
        )

    @classmethod
    def get_in_one_day(cls):
        start = datetime.utcnow() - timedelta(days=1)
        return (
            NetworkStatus.query.filter(NetworkStatus.time_stamp > start)
            .filter(extract("minute", NetworkStatus.time_stamp) % 5 == 0)
            .filter(extract("second", NetworkStatus.time_stamp) == 0)
            .all()
        )
