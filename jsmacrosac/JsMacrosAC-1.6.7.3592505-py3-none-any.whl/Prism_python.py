from typing import overload
from typing import TypeVar

Prism4j_Grammar = TypeVar["io.noties.prism4j.Prism4j.Grammar"]

class Prism_python:
	"""This class is from Prism4j under the Apache-2.0 license updated for format strings and other stuff from upstream
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def create(self, prism4j: Prism4j) -> Prism4j_Grammar:
		pass

	pass


