from dataclasses import dataclass
from datetime import datetime, timedelta
from tracemalloc import start

from sqlalchemy import extract

from ...extensions import db
from .snmp_utils import snmp_walk_int


class NetworkStatus:
    def __init__(self, agent):
        self.send_bytes = sum(
            [
                value
                for value in snmp_walk_int(
                    agent.host, agent.community, "IF-MIB", "ifOutOctets"
                )
            ]
        )
        self.recv_bytes = sum(
            [
                value
                for value in snmp_walk_int(
                    agent.host, agent.community, "IF-MIB", "ifInOctets"
                )
            ]
        )
        self.timer = datetime.utcnow().replace(microsecond=0)
        self.agent = agent

    def save(self):
        send_bytes = sum(
            [
                value
                for value in snmp_walk_int(
                    self.agent.host, self.agent.community, "IF-MIB", "ifOutOctets"
                )
            ]
        )
        recv_bytes = sum(
            [
                value
                for value in snmp_walk_int(
                    self.agent.host, self.agent.community, "IF-MIB", "ifInOctets"
                )
            ]
        )
        timer = datetime.utcnow().replace(microsecond=0)
        time_delta = timer - self.timer

        send_speed = format(
            (send_bytes - self.send_bytes) / time_delta.total_seconds() / 1024**2,
            ".2f",
        )
        recv_speed = format(
            (recv_bytes - self.recv_bytes) / time_delta.total_seconds() / 1024**2,
            ".2f",
        )

        self.set_counter(send_bytes, recv_bytes, timer)

        db.session.add(NetworkStatusInfo(recv_speed, send_speed, self.agent))

    def set_counter(self, send_bytes, recv_bytes, timer):
        self.send_bytes = send_bytes
        self.recv_bytes = recv_bytes
        self.timer = timer


@dataclass
class NetworkStatusInfo(db.Model):
    id: int
    recv_speed: float
    send_speed: float
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recv_speed = db.Column(db.Float)
    send_speed = db.Column(db.Float)
    time_stamp = db.Column(db.DateTime)

    agent_id = db.Column(db.Integer, db.ForeignKey("snmp_agent.id"))
    agent = db.relationship(
        "SnmpAgent", backref=db.backref("network_status_info", lazy="dynamic")
    )

    def __init__(self, recv_speed, send_speed, agent):
        self.recv_speed = recv_speed
        self.send_speed = send_speed
        self.agent = agent
        self.time_stamp = datetime.utcnow().replace(microsecond=0)

    @classmethod
    def get_last(cls, agent):
        start = datetime.utcnow() - timedelta(minutes=1)
        return (
            cls.query.filter(cls.time_stamp > start)
            .filter(cls.agent == agent)
            .order_by(cls.time_stamp.desc())
            .first()
        )

    @classmethod
    def get_batch(cls, agent):
        count = cls.query.filter(cls.agent == agent).count()
        if count > 100:
            count = 100
        return (
            cls.query.filter(cls.agent == agent)
            .order_by(cls.time_stamp.desc())
            .limit(count)
            .all()[::-1]
        )

    @classmethod
    def get_in_one_day(cls, agent):
        start = datetime.utcnow() - timedelta(days=1)
        return (
            cls.query.filter(cls.time_stamp > start)
            .filter(cls.agent == agent)
            .filter(extract("minute", cls.time_stamp) % 5 == 0)
            .filter(extract("second", cls.time_stamp) == 0)
            .all()
        )
