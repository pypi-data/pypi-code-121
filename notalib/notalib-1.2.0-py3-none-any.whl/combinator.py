class Combinator:
	"""
	Combines multiple data sets into a set of their combinations.
	Say, our datasets are [1,2], [3,4], [5,6].
	Then, our combinations would be:
	with 1 dataset:  [[1], [2]]
	with 2 datasets: [[1,3], [1,4], [2,3], [2,4]]
	with 3 datasets: [[1,3,5], [1,3,6], [1,4,5], [1,4,6], [2,3,5], [2,3,6], [2,4,5], [2,4,6]]
	"""
	result = []

	def __init__(self):
		self.result = []

	def combine(self, new_set):
		#print("Current result", self.result)
		#print("Combining set", new_set)

		if len(new_set) == 0:
			raise Exception("Combinator cannot combine with empty set")

		if len(self.result) == 0:
			for i in new_set:
				self.result += [[i]]
		else:
			newresult = []
			for tuple in self.result:
				for i in new_set:
					newresult += [tuple + [i]]
			self.result = newresult
		#print("New result", self.result)

	def get_result(self):
		return self.result
