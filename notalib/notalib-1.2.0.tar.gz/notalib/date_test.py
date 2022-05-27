from .date import get_week_number

from arrow import get as arrow_get

import pytest


@pytest.mark.parametrize(
	"date, expected_week_number",
	[
		(arrow_get('2022-01-01'), 1),
		(arrow_get('2022-01-06'), 2),
		(arrow_get('2021-12-31'), 53),
		('', None),
		([1, 2, 3], None),
		(None, None),
	]
)
def test_get_week_number(date, expected_week_number):
	if not hasattr(date, 'strftime'):
		with pytest.raises(AttributeError):
			get_week_number(date)
	else:
		assert get_week_number(date) == expected_week_number
