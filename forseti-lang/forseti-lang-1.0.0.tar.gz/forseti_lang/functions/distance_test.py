from .distance import Distance
from ..exceptions import ForsetiFunctionSyntaxError

import pytest


@pytest.mark.parametrize(
	"condition, text",
	[
		("|wN", ""),
		("|cN", ""),
		("|w5 world", ""),
		("hello |c5", ""),
		("hello |w-1 world", ""),
		("", ""),
	]
)
def test_distance_function_exceptions(condition, text):
	with pytest.raises(ForsetiFunctionSyntaxError):
		Distance(condition, text)


@pytest.mark.parametrize(
	"condition, text, expected_result",
	[
		("Hugin |w5 Munin", "Odin had two ravens Hugin and Munin", True),
		("Hugin |c5 Munin", "Odin had two ravens Hugin and Munin", True),
		("Hugin |w15 Munin", "", False),
		("Hugin |c15 Munin", "", False),
		("Munin |w0 Hugin", "Munin Hugin", True),
		("Munin |w0 Hugin", "Munin and Hugin", False),
		("T |c0 wo", "Two", True),
	]
)
def test_distance_function_results(condition, text, expected_result):
	assert Distance(condition, text).res == expected_result
