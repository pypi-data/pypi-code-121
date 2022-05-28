import json
from pathlib import Path
from typing import Any


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Path):
            return str(o)

        return json.JSONEncoder.default(self, o)
