from typing import Optional
from dataclasses import dataclass
from mlplatform_lib.dataclass import SelectorProperty


@dataclass
class FileDownload:
    file_name: str
    file_type: str
    selector_property: SelectorProperty
    file_token: Optional[str]
