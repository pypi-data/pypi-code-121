class Timing(object):
	"""
	Measures time that an operation took to complete.

		timing = Timing(auto_print=True)
		with timing:
			do_something()

		timing = Timing()
		with timing:
			do_something()
		print(timing.result)
	"""
	def __init__(self, auto_print=False):
		super(Timing, self).__init__()
		self.result = None
		self._start = None
		self.auto_print = auto_print

	def __enter__(self):
		import arrow
		self._start = arrow.now()

	def __exit__(self, exc_type, exc_value, traceback):
		import arrow
		self.result = arrow.now() - self._start
		if self.auto_print:
			print('time:', self.result)
