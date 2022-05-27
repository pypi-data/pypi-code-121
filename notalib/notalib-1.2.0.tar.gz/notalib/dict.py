from typing import Sequence, Hashable


def find_field(d, candidates):
	"""
	Given a dict and a list of possible keys, find the first key
	which is included into this dict. Throws ValueError if not found.
	"""
	for c in candidates:
		if c in d:
			return c
	raise ValueError(f"Can't find any of: {candidates}")

def find_value(d, candidates):
	"""
	Given a dict and a list of possible keys, find the first key
	which is included into this dict and return its value.
	Throws ValueError if not found.
	"""
	fieldname = find_field(d, candidates)
	return d[fieldname]

def normalize_dict(source, replacements, allow_original_key=True):
	"""
	Given a dict and a map: reference key -> [] possible replacements,
	return a new dict where all keys are guaranteed to be reference keys
	with values taken from any of replacement keys.

	Typically used to normalize a dataset where the same info can be listed
	under different names.

	Example map:
	{
		"artist": ["Artist", "ARTIST"],
		"year": ["Year", "yr", "yob"],
	}
	"""
	ret = {}
	for key in replacements:
		candidates = replacements[key]
		if allow_original_key:
			candidates += (key,)
		value = find_value(source, candidates)
		ret[key] = value
	return ret


def filter_dict(src: dict, keys_to_filter: Sequence[Hashable]) -> dict:
	"""
	Filters dictionary by keys_to_filter set.

	Parameters
	----------
	src: dict
		Source dictionary.
	keys_to_filter: Sequence[Hashable]
		Set of keys that should be in the final dictionary.

	Returns
	-------
	dict
		Filtered source dictionary.
	"""

	return {key: value for key, value in src.items() if key in keys_to_filter}
