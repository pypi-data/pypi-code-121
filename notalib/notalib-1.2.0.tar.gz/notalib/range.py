class Range(object):
	"""
	Unlike most libraries (and the standard library), this one works with most
	generic definition of range. Range is defined as just anything that
	has start and end. The only requirement is for these values to be comparable.
	So, this works with ints, timestamps, tuples, whatever.

	https://stackoverflow.com/a/48265052
	"""
	def __init__(self, start, end):
		self.start = start
		self.end = end
		# self.duration = self.end - self.start

	def is_overlapped(self, other_range):
		if max(self.start, other_range.start) < min(self.end, other_range.end):
			return True
		else:
			return False

	def get_overlapped_range(self, other_range):
		if not self.is_overlapped(other_range): return
		if other_range.start >= self.start:
			if self.end >= other_range.end:
				return Range(other_range.start, other_range.end)
			else:
				return Range(other_range.start, self.end)
		elif other_range.start < self.start:
			if other_range.end >= self.end:
				return Range(self.start, self.end)
			else:
				return Range(self.start, other_range.end)

	# def __repr__(self):
	# 	return '{0} ------> {1}'.format(*[time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(d))
	# 		for d in [self.start, self.end]])
