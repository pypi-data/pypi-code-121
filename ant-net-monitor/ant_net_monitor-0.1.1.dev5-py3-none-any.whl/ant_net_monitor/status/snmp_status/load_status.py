from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import extract

from ...extensions import db
from .snmp_utils import snmp_walk_int


class LoadStatus:
    def __init__(self, agent):
        self.agent = agent

    def save(self):
        load = [
            (value / 100)
            for value in snmp_walk_int(
                self.agent.host, self.agent.community, "UCD-SNMP-MIB", "laLoadInt"
            )
        ]

        db.session.add(LoadStatusInfo(load[0], load[1], load[2], self.agent))
        db.session.commit()


@dataclass
class LoadStatusInfo(db.Model):
    id: int
    load_1: float
    load_5: float
    load_15: float
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime)
    load_1 = db.Column(db.Float)
    load_5 = db.Column(db.Float)
    load_15 = db.Column(db.Float)

    agent_id = db.Column(db.Integer, db.ForeignKey("snmp_agent.id"))
    agent = db.relationship(
        "SnmpAgent", backref=db.backref("load_status_info", lazy="dynamic")
    )

    def __init__(self, load_1, load_5, load_15, agent):
        self.load_1 = load_1
        self.load_5 = load_5
        self.load_15 = load_15
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
            cls.query.order_by(cls.time_stamp.desc())
            .filter(cls.agent == agent)
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
