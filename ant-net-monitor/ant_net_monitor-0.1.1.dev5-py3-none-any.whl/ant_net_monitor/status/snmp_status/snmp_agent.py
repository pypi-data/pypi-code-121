from dataclasses import dataclass

from ...extensions import db


@dataclass
class SnmpAgent(db.Model):
    id: int
    host: str
    community: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host = db.Column(db.String(64), nullable=False)
    community = db.Column(db.String(64), nullable=False)

    def __init__(self, host, community):
        self.host = host
        self.community = community

    def __str__(self):
        return f"{self.host} {self.community}"

    @staticmethod
    def save(agent):
        db.session.add(agent)
        db.session.commit()

    @staticmethod
    def get_all():
        return SnmpAgent.query.all()

    @staticmethod
    def get_by_host(host):
        return SnmpAgent.query.filter_by(host=host).first()

    @staticmethod
    def init_agent(app, host, community):
        with app.app_context():
            if len(SnmpAgent.get_all()) == 0:
                agent = SnmpAgent(host, community)
                SnmpAgent.save(agent)
