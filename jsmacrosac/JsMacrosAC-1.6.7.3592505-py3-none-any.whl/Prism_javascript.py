from typing import overload
from typing import TypeVar

Prism4j_Grammar = TypeVar["io.noties.prism4j.Prism4j.Grammar"]

class Prism_javascript:
	"""This class is from Prism4j under the Apache-2.0 license I updated template-strings to match with the JS version again, which made them work better. other updates.
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def create(self, prism4j: Prism4j) -> Prism4j_Grammar:
		pass

	pass


