from .dict import filter_dict

import pytest


FIRST_SRC_DICT = {
	'Some...': "BODY",
	'once': "told me",
	'the world': "is gonna roll me",
}
SECOND_SRC_DICT = {
	("Some", "body"): ["once", "told me"],
	("The world", "is gonna"): ["roll", "me"],
	("I ain't the", "sharpest tool"): ["in the shed"],
}


@pytest.mark.parametrize(
	"src, leave_only, expected_keys, expected_values",
	[
		(FIRST_SRC_DICT, ["Some...", "once"], ("Some...", "once"), ("BODY", "told me")),
		(FIRST_SRC_DICT, (), (), ()),
		(SECOND_SRC_DICT, [("Some", "body")], (("Some", "body"), ), (["once", "told me"], )),
		(SECOND_SRC_DICT, (), (), ()),
		({}, ("SOME", "BODY"), (), ()),
		(SECOND_SRC_DICT, ("Some...", ), (), ()),
		([], ("SOME", "BODY"), None, None)
	]
)
def test_filter_dict(src, leave_only, expected_keys, expected_values):
	if isinstance(src, dict):
		filtered_dict = filter_dict(src, leave_only)

		assert tuple(filtered_dict.keys()) == expected_keys
		assert tuple(filtered_dict.values()) == expected_values

	else:
		with pytest.raises(AttributeError, match=".* object has no attribute 'items'"):
			filter_dict(src, leave_only)
