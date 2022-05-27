def row_to_dict(d, key_as=None):
	key, value = d
	ret = value.to_dict()
	if key_as is not None:
		ret[key_as] = key
	return ret
