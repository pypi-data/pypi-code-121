from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import extract

from ...extensions import db
from .snmp_utils import snmp_walk_int


class DiskStatus:
    def __init__(self, agent):
        self.read_bytes = sum(
            [
                value
                for value in snmp_walk_int(
                    agent.host, agent.community, "UCD-DISKIO-MIB", "diskIONRead"
                )
            ]
        )
        self.write_bytes = sum(
            [
                value
                for value in snmp_walk_int(
                    agent.host, agent.community, "UCD-DISKIO-MIB", "diskIONWritten"
                )
            ]
        )
        self.timer = datetime.utcnow().replace(microsecond=0)
        self.agent = agent

    def save(self):
        read_bytes = sum(
            [
                value
                for value in snmp_walk_int(
                    self.agent.host,
                    self.agent.community,
                    "UCD-DISKIO-MIB",
                    "diskIONRead",
                )
            ]
        )
        write_bytes = sum(
            [
                value
                for value in snmp_walk_int(
                    self.agent.host,
                    self.agent.community,
                    "UCD-DISKIO-MIB",
                    "diskIONWritten",
                )
            ]
        )
        timer = datetime.utcnow().replace(microsecond=0)
        time_delta = timer - self.timer

        read_speed = format(
            (read_bytes - self.read_bytes) / time_delta.total_seconds() / 1024**2,
            ".2f",
        )
        write_speed = format(
            (write_bytes - self.write_bytes) / time_delta.total_seconds() / 1024**2,
            ".2f",
        )

        self.set_counter(read_bytes, write_bytes, timer)

        db.session.add(DiskStatusInfo(read_speed, write_speed, self.agent))
        db.session.commit()

    def set_counter(self, read_bytes, write_bytes, timer):
        self.read_bytes = read_bytes
        self.write_bytes = write_bytes
        self.timer = timer


@dataclass
class DiskStatusInfo(db.Model):
    id: int
    read_speed: float
    write_speed: float
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    read_speed = db.Column(db.Float)
    write_speed = db.Column(db.Float)
    time_stamp = db.Column(db.DateTime)

    agent_id = db.Column(db.Integer, db.ForeignKey("snmp_agent.id"))
    agent = db.relationship(
        "SnmpAgent", backref=db.backref("disk_status_info", lazy="dynamic")
    )

    def __init__(self, read_speed, write_speed, agent):
        self.read_speed = read_speed
        self.write_speed = write_speed
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
        count = cls.query.count()
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
