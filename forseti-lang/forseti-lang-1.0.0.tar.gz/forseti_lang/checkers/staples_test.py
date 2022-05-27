from ..exceptions import ForsetiSyntaxError
from .staples import check_staples

import pytest


@pytest.mark.parametrize(
	"condition",
	[
		"((True)",
		"(True))",
	]
)
def test_check_staples_errors(condition):
	with pytest.raises(ForsetiSyntaxError):
		check_staples(condition)


@pytest.mark.parametrize(
	"condition",
	[
		"(True)",
		"((True))",
		"True",
		"(True OR False) AND (False AND True)",
	]
)
def test_check_staples_results(condition):
	assert check_staples(condition) is None
