from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import extract

from ...extensions import db
from .snmp_utils import snmp_get_value


class InterruptStatus:
    def __init__(self, agent):
        self.interrupts = snmp_get_value(
            agent.host, agent.community, "UCD-SNMP-MIB", "ssRawInterrupts"
        )
        self.timer = datetime.utcnow().replace(microsecond=0)
        self.agent = agent

    def save(self):
        interrupts = snmp_get_value(
            self.agent.host, self.agent.community, "UCD-SNMP-MIB", "ssRawInterrupts"
        )
        timer = datetime.utcnow().replace(microsecond=0)
        time_delta = timer - self.timer

        interrupt_speed = format(
            (interrupts - self.interrupts) / time_delta.total_seconds(), ".2f"
        )

        self.set_counter(interrupts, timer)

        db.session.add(InterruptStatusInfo(interrupt_speed, self.agent))
        db.session.commit()

    def set_counter(self, counter, timer):
        self.interrupts = counter
        self.timer = timer


@dataclass
class InterruptStatusInfo(db.Model):
    id: int
    interrupt: int
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime)
    interrupt = db.Column(db.Integer)

    agent_id = db.Column(db.Integer, db.ForeignKey("snmp_agent.id"))
    agent = db.relationship(
        "SnmpAgent", backref=db.backref("interrupt_status_info", lazy="dynamic")
    )

    def __init__(self, interrupt, agent):
        self.interrupt = interrupt
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
