def as_chunks(l, n):
	"""
	Yield successive n-sized chunks from l.
	"""
	assert n >= 1
	for i in range(0, len(l), n):
		yield l[i:i + n]


def ensure_iterable(x):
	if isinstance(x, list): return x
	if isinstance(x, tuple): return x
	# TODO other cases
	return (x,)
