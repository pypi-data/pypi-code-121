from enum import Enum
from typing import Dict, Any, List, Optional

from dataclasses import dataclass, field


class ImportModelTypeEnum(Enum):
    JSON_TF2 = "JSON_TF2"
    ONNX = "ONNX"
    PB_TF2 = "PB_TF2"
    H5_TF2 = "H5_TF2"


@dataclass
class WrapperData:
    type: str
    data: Dict


@dataclass
class NodeResponse:
    id: str
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    position: List[int] = field(default_factory=lambda: [0, 0])
    wrapper: Optional[WrapperData] = None

