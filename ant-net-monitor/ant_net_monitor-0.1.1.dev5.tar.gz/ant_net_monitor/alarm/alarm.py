from dataclasses import dataclass
from datetime import datetime, timedelta

from ..extensions import db
from .alarm_log import AlarmLog


@dataclass
class Alarm(db.Model):
    id: int
    name: str
    alarm_value: float
    flag: bool
    activated: bool
    interval_time: int
    duration_time: int

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    alarm_value = db.Column(db.Float)
    flag = db.Column(db.Boolean)
    activated = db.Column(db.Boolean)
    interval_time = db.Column(db.Integer)

    duration_time = db.Column(db.Integer)
    last_warning_time = db.Column(db.DateTime)
    last_recover_time = db.Column(db.DateTime)

    def __init__(self, name, alarm_value):
        self.name = name
        self.alarm_value = alarm_value
        self.flag = False
        self.activated = True
        self.interval_time = 300
        self.duration_time = 10
        self.last_warning_time = datetime.utcnow().replace(microsecond=0)
        self.last_recover_time = datetime.utcnow().replace(microsecond=0)

    def set_alarm_flag(self, flag):
        self.flag = flag
        status = 'warning' if flag else 'recover'
        AlarmLog.save(self.name, status)

    def check_alarm(self, value):
        if self.alarm_value < value:
            if self.flag == False:
                if self.last_warning_time <= self.last_recover_time:
                    self.last_warning_time = datetime.utcnow().replace(microsecond=0)
                else:
                    if (
                        datetime.utcnow().replace(microsecond=0)
                        - self.last_warning_time
                    ).seconds >= self.duration_time:
                        self.set_alarm_flag(True)
            else:
                self.last_warning_time = datetime.utcnow().replace(microsecond=0)
        else:
            if self.flag == False:
                self.last_recover_time = datetime.utcnow().replace(microsecond=0)
            else:
                if self.last_recover_time <= self.last_warning_time:
                    self.last_recover_time = datetime.utcnow().replace(microsecond=0)
                else:
                    if (
                        datetime.utcnow().replace(microsecond=0)
                        - self.last_recover_time
                    ).seconds >= self.duration_time:
                        self.set_alarm_flag(False)

        db.session.commit()

    @classmethod
    def create_cpu_alarm(cls):
        db.session.add(cls(name="cpu_usage", alarm_value=80))
        db.session.add(cls(name="cpu_iowait", alarm_value=40))
        db.session.add(cls(name="cpu_steal", alarm_value=10))

        db.session.commit()

    @classmethod
    def create_ram_alarm(cls):
        db.session.add(cls(name="ram_usage", alarm_value=80))

        db.session.commit()

    @classmethod
    def create_swap_alarm(cls):
        db.session.add(cls(name="swap_usage", alarm_value=80))

        db.session.commit()

    @classmethod
    def get_all_alarm_items(cls):
        try:
            return cls.query.all()
        except Exception:
            return None

    @classmethod
    def init_alarm(cls, app):
        with app.app_context():
            if len(cls.get_all_alarm_items()) == 0:
                cls.create_cpu_alarm()
                cls.create_ram_alarm()
                cls.create_swap_alarm()

    @classmethod
    def update_alarm(cls, alarm):
        target = cls.query.filter_by(name=alarm["name"]).first()
        target.alarm_value = alarm["alarmValue"]
        target.activated = alarm["activated"]
        target.interval_time = alarm["intervalTime"]
        target.duration_time = alarm["durationTime"]
        db.session.commit()

    @classmethod
    def check_cpu_alarm(cls, cpu_usage, cpu_iowait, cpu_steal):
        cpu_usage_alarm = cls.query.filter_by(name="cpu_usage").first()
        cpu_iowait_alarm = cls.query.filter_by(name="cpu_iowait").first()
        cpu_steal_alarm = cls.query.filter_by(name="cpu_steal").first()

        if cpu_usage_alarm.activated:
            cpu_usage_alarm.check_alarm(cpu_usage)
        else:
            cpu_usage_alarm.set_alarm_flag(False)
        if cpu_iowait_alarm.activated:
            cpu_iowait_alarm.check_alarm(cpu_iowait)
        else:
            cpu_iowait_alarm.set_alarm_flag(False)
        if cpu_steal_alarm.activated:
            cpu_steal_alarm.check_alarm(cpu_steal)
        else:
            cpu_steal_alarm.set_alarm_flag(False)

    @classmethod
    def check_ram_alarm(cls, ram_usage):
        ram_usage_alarm = cls.query.filter_by(name="ram_usage").first()

        if ram_usage_alarm.activated:
            ram_usage_alarm.check_alarm(ram_usage)
        else:
            ram_usage_alarm.set_alarm_flag(False)

    @classmethod
    def check_swap_alarm(cls, swap_usage):
        swap_usage_alarm = cls.query.filter_by(name="swap_usage").first()

        if swap_usage_alarm.activated:
            swap_usage_alarm.check_alarm(swap_usage)
        else:
            swap_usage_alarm.set_alarm_flag(False)


    #XXX:以下为SNMP方式下的相关方法
    @classmethod
    def create_snmp_cpu_alarm(cls):
        db.session.add(cls(name="cpu_usage", alarm_value=80))
        db.session.commit()

    @classmethod
    def create_snmp_ram_alarm(cls):
        db.session.add(cls(name="ram_usage", alarm_value=80))
        db.session.commit()

    @classmethod
    def create_snmp_swap_alarm(cls):
        db.session.add(cls(name="swap_usage", alarm_value=80))
        db.session.commit()

    @classmethod
    def init_snmp_alarm(cls, app):
        with app.app_context():
            if len(cls.get_all_alarm_items()) == 0:
                cls.create_snmp_cpu_alarm()
                cls.create_snmp_ram_alarm()
                cls.create_snmp_swap_alarm()

    @classmethod
    def check_snmp_cpu_alarm(cls, cpu_usage):
        cpu_usage_alarm = cls.query.filter_by(name="cpu_usage").first()

        if cpu_usage_alarm.activated:
            cpu_usage_alarm.check_alarm(cpu_usage)
        else:
            cpu_usage_alarm.set_alarm_flag(False)

    @classmethod
    def check_snmp_ram_alarm(cls, ram_usage):
        ram_usage_alarm = cls.query.filter_by(name="ram_usage").first()

        if ram_usage_alarm.activated:
            ram_usage_alarm.check_alarm(ram_usage)
        else:
            ram_usage_alarm.set_alarm_flag(False)

    @classmethod
    def check_snmp_swap_alarm(cls, swap_usage):
        swap_usage_alarm = cls.query.filter_by(name="swap_usage").first()

        if swap_usage_alarm.activated:
            swap_usage_alarm.check_alarm(swap_usage)
        else:
            swap_usage_alarm.set_alarm_flag(False)
