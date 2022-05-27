from .execute import execute_condition

import pytest


@pytest.mark.parametrize(
	"condition, text, expected_result",
	[
		("odin |w5 great warrior", "many peoples think that odin was a great warrior", True),
	]
)
def test_execute_condition(condition, text, expected_result):
	assert execute_condition(condition, text) == expected_result
