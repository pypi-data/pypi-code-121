import json
from typing import Iterable, Dict, Hashable

from django.http import StreamingHttpResponse


def stream_json(data: Iterable[Dict[Hashable, any]]) -> StreamingHttpResponse:
	"""
	Stream all elements in `data` as JSON array using the StreamingHttpResponse class.

	Parameters
	----------
	data: Iterable[Dict[Hashable, any]]
		An Iterable of JSON-encodable elements.

	Returns
	-------
	StreamingHttpResponse
		A streaming HTTP response class with an iterator as content. Content-type = 'application/json'

	Notes
	-----
	The function is recommended to be used with a large set of transmitted data.
	"""

	assert isinstance(data, Iterable), "stream_json: data must be of iterable type"

	def _iter(ret):
		first = True
		yield '['

		for x in ret:
			if first:
				first = False
				yield json.dumps(x, ensure_ascii=False)
			else:
				yield ', '
				yield json.dumps(x, ensure_ascii=False)
		yield ']'

	return StreamingHttpResponse(
		_iter(data),
		content_type="application/json",
	)
