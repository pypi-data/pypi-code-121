from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import extract

from ...extensions import db
from .snmp_utils import snmp_get_value


class SwapStatus:
    def __init__(self, agent):
        self.agent = agent

    def save(self):
        swap_total = snmp_get_value(
            self.agent.host, self.agent.community, "UCD-SNMP-MIB", "memTotalSwap"
        )
        swap_free = snmp_get_value(
            self.agent.host, self.agent.community, "UCD-SNMP-MIB", "memAvailSwap"
        )
        swap_percent = format(100 - swap_free / swap_total * 100, ".2f")
        swap_used = format((swap_total - swap_free) / 1024**2, ".2f")

        db.session.add(SwapStatusInfo(swap_percent, swap_used, self.agent))
        db.session.commit()


@dataclass
class SwapStatusInfo(db.Model):
    id: int
    # percent: float
    used: float
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime)
    percent = db.Column(db.Float)
    used = db.Column(db.Float)

    agent_id = db.Column(db.Integer, db.ForeignKey("snmp_agent.id"))
    agent = db.relationship(
        "SnmpAgent", backref=db.backref("swap_status_info", lazy="dynamic")
    )

    def __init__(self, percent, used, agent):
        self.percent = percent
        self.used = used
        self.time_stamp = datetime.utcnow().replace(microsecond=0)
        self.agent = agent

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
