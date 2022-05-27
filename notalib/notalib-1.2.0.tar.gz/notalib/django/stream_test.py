from .stream import stream_json

from typing import Iterable

import pytest
from django.http import StreamingHttpResponse


@pytest.mark.parametrize(
	"data, expected_data",
	[
		([{'1': '2'}, {'1': '3'}], b'[{"1": "2"}, {"1": "3"}]'),
		(({'1': '2'}, {'1': '3'}), b'[{"1": "2"}, {"1": "3"}]'),
		(map(lambda x: x, [{'1': '2'}, {'1': '3'}]), b'[{"1": "2"}, {"1": "3"}]'),
		('HelloWorld!', b'["H", "e", "l", "l", "o", "W", "o", "r", "l", "d", "!"]'),
		(1511, None),
		([], b'[]'),
		((), b'[]'),
	]
)
def test_stream_json(data, expected_data):
	if isinstance(data, Iterable):
		res = stream_json(data)
		assert isinstance(res, StreamingHttpResponse)
		assert res.getvalue() == expected_data
	else:
		with pytest.raises(AssertionError, match="stream_json: data must be of iterable type"):
			stream_json(data)
