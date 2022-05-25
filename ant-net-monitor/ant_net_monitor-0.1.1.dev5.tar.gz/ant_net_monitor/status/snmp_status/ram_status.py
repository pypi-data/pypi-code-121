from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import extract

from ...extensions import db
from .snmp_utils import snmp_get_value


class RAMStatus:
    def __init__(self, agent):
        self.agent = agent

    def save(self):
        available = float(
            format(
                snmp_get_value(
                    self.agent.host,
                    self.agent.community,
                    "UCD-SNMP-MIB",
                    "memAvailReal",
                )
                / 1024**2,
                ".2f",
            )
        )
        cached = format(
            snmp_get_value(
                self.agent.host, self.agent.community, "UCD-SNMP-MIB", "memCached"
            )
            / 1024**2,
            ".2f",
        )
        buffers = format(
            snmp_get_value(
                self.agent.host, self.agent.community, "UCD-SNMP-MIB", "memBuffer"
            )
            / 1024**2,
            ".2f",
        )
        total = float(
            format(
                snmp_get_value(
                    self.agent.host,
                    self.agent.community,
                    "UCD-SNMP-MIB",
                    "memTotalReal",
                )
                / 1024**2,
                ".2f",
            )
        )
        percent = format(100 - available / total * 100, ".2f")

        db.session.add(RAMStatusInfo(available, cached, buffers, percent, self.agent))
        db.session.commit()


@dataclass
class RAMStatusInfo(db.Model):
    id: int
    available: float
    cached: float
    buffers: float
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime)
    available = db.Column(db.Float)
    cached = db.Column(db.Float)
    buffers = db.Column(db.Float)
    used_percent = db.Column(db.Float)

    agent_id = db.Column(db.Integer, db.ForeignKey("snmp_agent.id"))
    agent = db.relationship(
        "SnmpAgent", backref=db.backref("ram_status_info", lazy="dynamic")
    )

    def __init__(self, available, cached, buffers, percent, agent):
        self.available = available
        self.cached = cached
        self.buffers = buffers
        self.used_percent = percent
        self.agent = agent
        self.time_stamp = datetime.utcnow().replace(microsecond=0)

    @classmethod
    def get_last(cls, agent):
        start = datetime.utcnow() - timedelta(minutes=1)
        return (
            cls.query.filter(cls.time_stamp >= start)
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
            cls.query.filter(cls.time_stamp >= start)
            .filter(cls.agent == agent)
            .filter(extract("minute", cls.time_stamp) % 5 == 0)
            .filter(extract("second", cls.time_stamp) == 0)
            .all()
        )
