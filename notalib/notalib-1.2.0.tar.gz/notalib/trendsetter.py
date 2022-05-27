class Unit:
	def execute(self, name, deps, options): raise NotImplementedError


class SimpleUnit(Unit):
	def __init__(self, execute_fn):
		self.execute_fn = execute_fn

	def execute(self, *args):
		return self.execute_fn(*args)


def to_unit(fn):
	return SimpleUnit(fn)


class Trendsetter:
	"""
	Trendsetter deals with your complicated dependency tree where every
	interface has several implementations, chosen at runtime,
	with not-so-easy instantiation process for each - and does it lazily,
	and with caching (which doesn't prevent you from having several
	dependency trees, each one cached independently).
	"""
	def __init__(self, options={}):
		self.units = {}
		self.unit_deps = {}
		self.options = options
		self.cache = {}

	def register(self, name: str, unit: Unit, deps=[]):
		self.units[name] = unit
		self.unit_deps[name] = deps

	def get(self, name):
		if name in self.cache:
			return self.cache[name]

		deps = {}
		for i in self.unit_deps[name]:
			deps[i] = self.get(i)

		ret = self.units[name].execute(name, deps, self.options)
		self.cache[name] = ret
		return ret


if __name__ == '__main__':
	class Adder:
		def add(self, a, b): raise NotImplementedError

	class AdderImpl(Adder):
		def add(self, a, b):
			return a + b

	class ExperimentalAdderImpl(Adder):
		def add(self, a, b):
			return a  # TODO

	class AdderUnit(Unit):
		def execute(self, name, deps, options):
			if options['use_experimental_adder']:
				return ExperimentalAdderImpl()
			else:
				return AdderImpl()

	ts = Trendsetter({
		# No assumptions what your options look like.
		'use_experimental_adder': False
	})
	ts.register('Adder', AdderUnit())

	class Fibonacci:
		def __init__(self, adder):
			self.adder = adder

		def compute(self, n):
			if n <= 2:
				return 1
			else:
				return self.adder.add(self.compute(n-1), self.compute(n-2))

	ts.register(
		'Fibonacci',
		# Simplified interface for more straightforward cases
		to_unit(lambda name, deps, options: Fibonacci(deps['Adder'])),
		# List of dependencies - they will be instantiated first
		['Adder'],
	)

	assert ts.get('Adder').add(2, 2) == 4
	assert ts.get('Fibonacci').compute(6) == 8
	print('6th Fibonacci number is:', ts.get('Fibonacci').compute(6))
