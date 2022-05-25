from dataclasses import dataclass
from itertools import islice

from ...extensions import db
from .snmp_utils import snmp_get_value, snmp_walk_int, snmp_walk_str


class System:
    def __init__(self, agent):
        self.agent = agent

    def save(self):
        def get_disk_info(self):
            disks = [
                name
                for name in snmp_walk_str(
                    self.agent.host,
                    self.agent.community,
                    "HOST-RESOURCES-MIB",
                    "hrStorageDescr",
                )
            ]
            index = disks.index("/")

            allocate_unit = next(
                islice(
                    snmp_walk_int(
                        self.agent.host,
                        self.agent.community,
                        "HOST-RESOURCES-MIB",
                        "hrStorageAllocationUnits",
                    ),
                    index,
                    None,
                )
            )

            size = float(
                format(
                    next(
                        islice(
                            snmp_walk_int(
                                self.agent.host,
                                self.agent.community,
                                "HOST-RESOURCES-MIB",
                                "hrStorageSize",
                            ),
                            index,
                            None,
                        )
                    )
                    * allocate_unit
                    / 1024**3,
                    ".2f",
                )
            )

            usage = float(
                format(
                    next(
                        islice(
                            snmp_walk_int(
                                self.agent.host,
                                self.agent.community,
                                "HOST-RESOURCES-MIB",
                                "hrStorageUsed",
                            ),
                            index,
                            None,
                        )
                    )
                    * allocate_unit
                    / 1024**3,
                    ".2f",
                )
            )

            percent = format(usage / size * 100, ".2f")

            return (size, percent)

        cpu_count = snmp_get_value(
            self.agent.host, self.agent.community, "UCD-SNMP-MIB", "ssCpuNumCpus"
        )

        total_ram = format(
            snmp_get_value(
                self.agent.host, self.agent.community, "UCD-SNMP-MIB", "memTotalReal"
            )
            / 1024**2,
            ".2f",
        )

        total_swap = format(
            snmp_get_value(
                self.agent.host, self.agent.community, "UCD-SNMP-MIB", "memTotalSwap"
            )
            / 1024**2,
            ".2f",
        )

        disk_size, disk_percent = get_disk_info(self)

        db.session.add(
            SystemInfo(
                cpu_count, total_ram, total_swap, disk_size, disk_percent, self.agent
            )
        )
        db.session.commit()


@dataclass
class SystemInfo(db.Model):
    id: int
    cpu_count: int
    ram_total: float
    swap_total: float
    disk_total: float
    disk_percent: float

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cpu_count = db.Column(db.Integer)
    ram_total = db.Column(db.Float)
    swap_total = db.Column(db.Float)
    disk_total = db.Column(db.Float)
    disk_percent = db.Column(db.Float)

    agent_id = db.Column(db.Integer, db.ForeignKey("snmp_agent.id"))
    agent = db.relationship(
        "SnmpAgent", backref=db.backref("system_info", lazy="dynamic")
    )

    def __init__(
        self, cpu_count, ram_total, swap_total, disk_total, disk_percent, agent
    ):
        self.cpu_count = cpu_count
        self.ram_total = ram_total
        self.swap_total = swap_total
        self.disk_total = disk_total
        self.disk_percent = disk_percent
        self.agent = agent

    @classmethod
    def get_last(cls, agent):
        return cls.query.filter_by(agent=agent).order_by(-cls.id).first()
