from dataclasses import dataclass
from abc import ABC, abstractmethod
from prettytable import PrettyTable  # type: ignore[import]
from typing import TypeVar, Generic, Sequence, Dict, List, Optional

__all__ = (
	"CannotWalkException", "ListWalkerElement", "BaseListWalker", "ListWalker1D"
)
T = TypeVar("T")  # For [BaseListWalker.data] generic type
P = TypeVar("P")  # For [BaseListWalker.cursor] type


class CannotWalkException(Exception):
	"""
		Raised when the cursor failed to walk because blocked by an ignored element.
	"""


@dataclass(frozen=True)
class ListWalkerElement(Generic[T, P]):
	"""A data class for walker elements."""
	position: P
	value: T
	is_ignored: bool
	walker: "BaseListWalker[T, P]"


class BaseListWalker(ABC, Generic[T, P]):
	"""
		This object has a [cursor] to indicate
		the current position of this walker in the [data].
		
		Additionally, you can add [ignored_elements] to skip over
		when walking through the [data].
	"""
	
	@abstractmethod
	def __init__(self, data: Sequence[T]) -> None:
		...
	
	@property
	@abstractmethod
	def size(self) -> P:
		"""Get the size of the [data]."""
	
	@property
	@abstractmethod
	def cursor_element(self) -> ListWalkerElement[T, P]:
		"""Get the element at the [cursor] position."""
	
	@abstractmethod
	def is_ignored(self, position: P) -> bool:
		"""Check if the element at [position] is in [ignored_elements]."""
	
	@abstractmethod
	def print(self) -> None:
		"""
			Print the [data] in tabular format.
			This also indicates the current cursor position '> element <'
			and the ignored elements '(element)'.
		"""
	
	@abstractmethod
	def get(self, position: P) -> ListWalkerElement[T, P]:
		"""Get the element at [position]."""
	
	@abstractmethod
	def get_left(self) -> ListWalkerElement[T, P]:
		"""Get the previous element at the [cursor] position."""
	
	@abstractmethod
	def get_right(self) -> ListWalkerElement[T, P]:
		"""Get the next element at the [cursor] position."""
	
	@abstractmethod
	def get_neighbors(
		self, position: Optional[P] = None
	) -> Dict[str, ListWalkerElement[T, P]]:
		...
	
	@abstractmethod
	def walk_left(
		self, *, jump: bool = True, silent: bool = False
	) -> ListWalkerElement[T, P]:
		"""
			Move the [cursor] to the left with respect to [ignored_elements].
			If [jump] is `False`, the cursor cannot walk through an ignored element.
			
			[IndexError] or [CannotWalkException] may be raised unless [silent].
			In that case, the [cursor] will stay the same.
		"""
	
	@abstractmethod
	def walk_right(
		self, *, jump: bool = True, silent: bool = False
	) -> ListWalkerElement[T, P]:
		"""
			Move the [cursor] to the right with respect to [ignored_elements].
			If [jump] is `False`, the cursor cannot walk through an ignored element.
			
			[IndexError] or [CannotWalkException] may be raised unless [silent].
			In that case, the [cursor] will stay the same.
		"""


class ListWalker1D(BaseListWalker[T, int]):
	
	def __init__(self, data: Sequence[T]) -> None:
		self.data = data
		self.cursor = 0  # Index of the current element
		self.ignored_elements: List[int] = []  # Indices of the ignored elements
	
	@property
	def size(self) -> int:
		return len(self.data)
	
	@property
	def cursor_element(self) -> ListWalkerElement[T, int]:
		return self.get(self.cursor)
	
	def is_ignored(self, position: int) -> bool:
		return position in self.ignored_elements
	
	def print(self) -> None:
		t = PrettyTable(("Position", "Element"))
		
		for position, element in enumerate(self.data):
			element_str = str(element)
			
			if self.is_ignored(position):
				element_str = f"({element_str})"
			
			if position == self.cursor:
				element_str = f"> {element_str} <"
			
			t.add_row((position, element_str))
		
		print(t)
	
	def get(self, position: int) -> ListWalkerElement[T, int]:
		if position < 0 or position >= self.size:
			raise IndexError("list index out of range")
		
		return ListWalkerElement(
			position, self.data[position], self.is_ignored(position), self
		)
	
	def get_left(self) -> ListWalkerElement[T, int]:
		return self.get(self.cursor - 1)
	
	def get_right(self) -> ListWalkerElement[T, int]:
		return self.get(self.cursor + 1)
	
	def get_neighbors(
		self, position: Optional[int] = None
	) -> Dict[str, ListWalkerElement[T, int]]:
		"""
			Get the previous and next elements
			at the [cursor] position or optional [position].
		"""
		position = position or self.cursor
		neighbors = {}
		
		try:
			neighbors["left"] = self.get_left()
		except IndexError:
			pass
		
		try:
			neighbors["right"] = self.get_right()
		except IndexError:
			pass
		
		return neighbors
	
	def walk_left(
		self, *, jump: bool = True, silent: bool = False
	) -> ListWalkerElement[T, int]:
		position = self.cursor - 1
		element: ListWalkerElement[T, int]
		
		try:
			element = self.get(position)
		except IndexError as error:
			if silent:
				return self.cursor_element
			else:
				raise error
		
		if not jump and element.is_ignored:
			if silent:
				return self.cursor_element
			else:
				raise CannotWalkException()
		
		while element.is_ignored:
			try:
				position -= 1
				element = self.get(position)
			except IndexError as error:
				if silent:
					return self.cursor_element
				else:
					raise error
		
		self.cursor = position
		return element
	
	def walk_right(
		self, *, jump: bool = True, silent: bool = False
	) -> ListWalkerElement[T, int]:
		position = self.cursor + 1
		element: ListWalkerElement[T, int]
		
		try:
			element = self.get(position)
		except IndexError as error:
			if silent:
				return self.cursor_element
			else:
				raise error
		
		if not jump and element.is_ignored:
			if silent:
				return self.cursor_element
			else:
				raise CannotWalkException()
		
		while element.is_ignored:
			try:
				position += 1
				element = self.get(position)
			except IndexError as error:
				if silent:
					return self.cursor_element
				else:
					raise error
		
		self.cursor = position
		return element


class ListWalker2D(BaseListWalker[T, List[int]]):
	
	def __init__(self, data: Sequence[Sequence[T]]) -> None:
		self.data = data
		self.cursor = [0, 0]  # [rows, cols] of the current element
		self.ignored_elements: List[List[int]] = []
	
	@property
	def size(self) -> List[int]:
		rows = len(self.data)
		
		try:
			cols = len(self.data[0])
		except IndexError:
			cols = 0
		
		return [rows, cols]
	
	@property
	def cursor_element(self) -> ListWalkerElement[T, List[int]]:
		return self.get(self.cursor)
	
	def is_ignored(self, position: List[int]) -> bool:
		return position in self.ignored_elements
	
	def print(self) -> None:
		try:
			t = PrettyTable([""] + [str(i) for i, _ in enumerate(self.data[0])])
		except IndexError:
			t = PrettyTable(("", ))
		
		for rowpos, row_element in enumerate(self.data):
			rowelems = []
			
			for colpos, col_element in enumerate(row_element):
				col_element_str = str(col_element)
				position = [rowpos, colpos]
				
				if self.is_ignored(position):
					col_element_str = f"({col_element})"
				
				if position == self.cursor:
					col_element_str = f"> {col_element} <"
				
				rowelems.append(col_element_str)
			
			t.add_row((rowpos, *rowelems))
		
		print(t)
	
	def get(
		self, position: List[int]
	) -> ListWalkerElement[T, List[int]]:
		if position[0] < 0 or position[0] >= self.size[0]:
			raise IndexError("list index out of range")
		
		if position[1] < 0 or position[1] >= self.size[1]:
			raise IndexError("list index out of range")
		
		return ListWalkerElement(
			position, self.data[position[0]][position[1]],
			self.is_ignored(position), self
		)
	
	def get_up(self) -> ListWalkerElement[T, List[int]]:
		return self.get([self.cursor[0] - 1, self.cursor[1]])
	
	def get_right(self) -> ListWalkerElement[T, List[int]]:
		return self.get([self.cursor[0], self.cursor[1] + 1])
	
	def get_down(self) -> ListWalkerElement[T, List[int]]:
		return self.get([self.cursor[0] + 1, self.cursor[1]])
	
	def get_left(self) -> ListWalkerElement[T, List[int]]:
		return self.get([self.cursor[0], self.cursor[1] - 1])
	
	def get_neighbors(
		self, position: Optional[List[int]] = None
	) -> Dict[str, ListWalkerElement[T, List[int]]]:
		"""
			Get the above, next, below, and previous elements
			at the [cursor] position or optional [position].
		"""
		position = position or self.cursor
		neighbors = {}
		
		try:
			neighbors["up"] = self.get_up()
		except IndexError:
			pass
		
		try:
			neighbors["right"] = self.get_right()
		except IndexError:
			pass
		
		try:
			neighbors["down"] = self.get_down()
		except IndexError:
			pass
		
		try:
			neighbors["left"] = self.get_left()
		except IndexError:
			pass
		
		return neighbors
	
	def walk_up(
		self, *, jump: bool = True, silent: bool = False
	) -> ListWalkerElement[T, List[int]]:
		"""
			Move the [cursor] up with respect to [ignored_elements].
			If [jump] is `False`, the cursor cannot walk through an ignored element.
			
			[IndexError] or [CannotWalkException] may be raised unless [silent].
			In that case, the [cursor] will stay the same.
		"""
		position = [self.cursor[0] - 1, self.cursor[1]]
		element: ListWalkerElement[T, List[int]]
		
		try:
			element = self.get(position)
		except IndexError as error:
			if silent:
				return self.cursor_element
			else:
				raise error
		
		if not jump and element.is_ignored:
			if silent:
				return self.cursor_element
			else:
				raise CannotWalkException()
		
		while element.is_ignored:
			try:
				position[0] -= 1
				element = self.get(position)
			except IndexError as error:
				if silent:
					return self.cursor_element
				else:
					raise error
		
		self.cursor = position
		return element
	
	def walk_right(
		self, *, jump: bool = True, silent: bool = False
	) -> ListWalkerElement[T, List[int]]:
		position = [self.cursor[0], self.cursor[1] + 1]
		element: ListWalkerElement[T, List[int]]
		
		try:
			element = self.get(position)
		except IndexError as error:
			if silent:
				return self.cursor_element
			else:
				raise error
		
		if not jump and element.is_ignored:
			if silent:
				return self.cursor_element
			else:
				raise CannotWalkException()
		
		while element.is_ignored:
			try:
				position[1] += 1
				element = self.get(position)
			except IndexError as error:
				if silent:
					return self.cursor_element
				else:
					raise error
		
		self.cursor = position
		return element
	
	def walk_down(
		self, *, jump: bool = True, silent: bool = False
	) -> ListWalkerElement[T, List[int]]:
		"""
			Move the [cursor] down with respect to [ignored_elements].
			If [jump] is `False`, the cursor cannot walk through an ignored element.
			
			[IndexError] or [CannotWalkException] may be raised unless [silent].
			In that case, the [cursor] will stay the same.
		"""
		position = [self.cursor[0] + 1, self.cursor[1]]
		element: ListWalkerElement[T, List[int]]
		
		try:
			element = self.get(position)
		except IndexError as error:
			if silent:
				return self.cursor_element
			else:
				raise error
		
		if not jump and element.is_ignored:
			if silent:
				return self.cursor_element
			else:
				raise CannotWalkException()
		
		while element.is_ignored:
			try:
				position[0] += 1
				element = self.get(position)
			except IndexError as error:
				if silent:
					return self.cursor_element
				else:
					raise error
		
		self.cursor = position
		return element
	
	def walk_left(
		self, *, jump: bool = True, silent: bool = False
	) -> ListWalkerElement[T, List[int]]:
		position = [self.cursor[0], self.cursor[1] - 1]
		element: ListWalkerElement[T, List[int]]
		
		try:
			element = self.get(position)
		except IndexError as error:
			if silent:
				return self.cursor_element
			else:
				raise error
		
		if not jump and element.is_ignored:
			if silent:
				return self.cursor_element
			else:
				raise CannotWalkException()
		
		while element.is_ignored:
			try:
				position[1] -= 1
				element = self.get(position)
			except IndexError as error:
				if silent:
					return self.cursor_element
				else:
					raise error
		
		self.cursor = position
		return element
