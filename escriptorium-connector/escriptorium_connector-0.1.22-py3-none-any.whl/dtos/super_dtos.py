from escriptorium_connector.utils.pydantic_dataclass_fix import dataclass
from typing import List, Union, Any


# It would be nice if results could be a list of a Generic type,
# but when I tried that pydantic seemed to stumble trying
# to serialize data into the dataclass.
@dataclass
class PagenatedResponse:
    count: int
    next: Union[str, None]
    previous: Union[str, None]
    results: List[Any]
