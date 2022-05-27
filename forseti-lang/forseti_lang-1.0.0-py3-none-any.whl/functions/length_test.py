from .length import Length
from ..exceptions import ForsetiFunctionSyntaxError

import pytest


@pytest.mark.parametrize(
	"condition, text",
	[
		("|lm", ""),
		("|lg", ""),
		("|ll", ""),
		("ll", ""),
		("|lgN", ""),
		("", ""),
	]
)
def test_length_function_exceptions(condition, text):
	with pytest.raises(ForsetiFunctionSyntaxError):
		Length(condition, text)


@pytest.mark.parametrize(
	"condition, text, expected_result",
	[
		("|ll5", "Odin had two ravens Hugin and Munin", False),
		("|lg5", "Odin had two ravens Hugin and Munin", True),
		("|ll15", "Hugin or Munin", True),
		("|lg15", "Hugin or Munin", False),
	]
)
def test_length_function_results(condition, text, expected_result):
	assert Length(condition, text).res == expected_result
