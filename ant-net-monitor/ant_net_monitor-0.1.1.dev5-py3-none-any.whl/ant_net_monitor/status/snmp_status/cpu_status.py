from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import extract

from ...extensions import db
from .snmp_utils import snmp_get_value


class CPUStatus:
    def __init__(self, agent):
        self.agent = agent

    def save(self):
        user_percent = snmp_get_value(
            self.agent.host, self.agent.community, "UCD-SNMP-MIB", "ssCpuUser"
        )
        system_percent = snmp_get_value(
            self.agent.host, self.agent.community, "UCD-SNMP-MIB", "ssCpuSystem"
        )
        used_percent = 100 - snmp_get_value(
            self.agent.host, self.agent.community, "UCD-SNMP-MIB", "ssCpuIdle"
        )

        db.session.add(
            CPUStatusInfo(user_percent, system_percent, used_percent, self.agent)
        )
        db.session.commit()


@dataclass
class CPUStatusInfo(db.Model):
    id: int
    user_percent: int
    system_percent: int
    #used_percent: int
    time_stamp: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_stamp = db.Column(db.DateTime)
    user_percent = db.Column(db.Integer)
    system_percent = db.Column(db.Integer)
    used_percent = db.Column(db.Integer)

    agent_id = db.Column(db.Integer, db.ForeignKey("snmp_agent.id"))
    agent = db.relationship(
        "SnmpAgent", backref=db.backref("cpu_status_info", lazy="dynamic")
    )

    def __init__(self, user_percent, system_percent, used_percent, agent):
        self.user_percent = user_percent
        self.system_percent = system_percent
        self.used_percent = used_percent
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