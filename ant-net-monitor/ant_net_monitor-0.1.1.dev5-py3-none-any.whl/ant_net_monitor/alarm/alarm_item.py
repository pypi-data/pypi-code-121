from dataclasses import dataclass
from ..extensions import db

@dataclass
class AlarmItem(db.Model):
    id: int
    name: str
    alarm_value: float

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    alarm_value = db.Column(db.Float)
    alarm_id = db.Column(db.Integer, db.ForeignKey("alarm.id"))

    def __init__(self, name, alarm_id, alarm_value):
        self.name = name
        self.alarm_id = alarm_id
        self.alarm_value = alarm_value
