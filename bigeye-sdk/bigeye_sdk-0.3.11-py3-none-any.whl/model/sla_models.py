from __future__ import annotations

import json
from dataclasses import dataclass
from bigeye_sdk.generated.com.torodata.models.generated import Collection, MetricInfoList


@dataclass
class SlaMetrics:
    """TODO: move to proto?  Reusing Message because it has nice features for converting json camel -> snake."""
    sla: Collection
    metrics: MetricInfoList

    def as_dict(self) -> dict:
        return {"sla": self.sla.to_dict(), "metrics": self.metrics.to_dict()}

    @classmethod
    def from_json(cls, sla_metrics_json: str) -> SlaMetrics:
        d = json.loads(sla_metrics_json)
        r = SlaMetrics(sla=Collection().from_dict(d['sla']), metrics=MetricInfoList().from_dict(d['metrics']))
        return r

