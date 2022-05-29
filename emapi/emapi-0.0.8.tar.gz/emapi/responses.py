from typing import Any
import orjson
from starlette.responses import JSONResponse


class JsonResponse(JSONResponse):
	def render(self, content: Any) -> bytes:
		return orjson.dumps(content)
