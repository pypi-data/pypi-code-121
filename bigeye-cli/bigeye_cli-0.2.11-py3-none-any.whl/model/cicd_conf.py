from dataclasses import dataclass, field
from typing import Optional, List

import yaml
from smart_open import smart_open

from bigeye_cli.model.vendor_report import VersionControlReportType


@dataclass
class DeltaCicdConf:
    delta_name_prefix: str
    source_warehouse_id: int
    source_fqtn: str
    target_warehouse_id: int
    target_fqtn: str
    vendor: str
    report_type: VersionControlReportType = None
    second_pass_group_bys: Optional[List[str]] = field(default_factory=lambda: [])

    def __post_init__(self):
        self.report_type = VersionControlReportType[self.vendor.upper()]

    @classmethod
    def load_conf(cls, delta_conf_file: str):
        with smart_open(delta_conf_file, 'r') as stream:
            conf = yaml.safe_load(stream)
            dc = DeltaCicdConf(**conf)
            if dc is None:
                raise Exception('Could not load delta configuration file.')
            return dc