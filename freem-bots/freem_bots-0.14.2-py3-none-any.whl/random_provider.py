import random
from typing import List, TypeVar


class RandomProvider:
	def __init__(self) -> None:
		self.random = random.Random()

	def get_float(self) -> float:
		return self.random.random()

	def get_int(self, lower_bound: int, upper_bound: int) -> int:
		return self.random.randint(lower_bound, upper_bound)

	_tvE = TypeVar('_tvE')

	def choose_randomly(self, options: List[_tvE]) -> _tvE:
		return self.random.choice(options)
