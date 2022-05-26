from typing import overload
from typing import TypeVar
from typing import Generic

C = TypeVar("C")
Predicate = TypeVar["java.util.function.Predicate_T_"]
Comparator = TypeVar["java.util.Comparator_T_"]
Thread = TypeVar["java.lang.Thread"]
Function = TypeVar["java.util.function.Function_T,R_"]
R = TypeVar("R")
T = TypeVar("T")
Consumer = TypeVar["java.util.function.Consumer_T_"]
U = TypeVar("U")
BiFunction = TypeVar["java.util.function.BiFunction_T,U,R_"]
Runnable = TypeVar["java.lang.Runnable"]
Supplier = TypeVar["java.util.function.Supplier_R_"]
BiConsumer = TypeVar["java.util.function.BiConsumer_T,U_"]
BiPredicate = TypeVar["java.util.function.BiPredicate_T,U_"]

class MethodWrapper(Consumer, BiConsumer, Function, BiFunction, Predicate, BiPredicate, Runnable, Supplier, Comparator, Generic[T, U, R, C]):
	"""Wraps most of the important functional interfaces.
	"""

	@overload
	def __init__(self, containingContext: C) -> None:
		pass

	@overload
	def getCtx(self) -> C:
		pass

	@overload
	def accept(self, t: T) -> None:
		pass

	@overload
	def accept(self, t: T, u: U) -> None:
		pass

	@overload
	def apply(self, t: T) -> R:
		pass

	@overload
	def apply(self, t: T, u: U) -> R:
		pass

	@overload
	def test(self, t: T) -> bool:
		pass

	@overload
	def test(self, t: T, u: U) -> bool:
		pass

	@overload
	def preventSameThreadJoin(self) -> bool:
		"""override to return true if the method can't join to the thread it was wrapped/created in, ie for languages that don't allow multithreading.
		"""
		pass

	@overload
	def overrideThread(self) -> Thread:
		"""make return something to override the thread set in FJsMacros#on(java.lang.String,xyz.wagyourtail.jsmacros.core.MethodWrapper<xyz.wagyourtail.jsmacros.core.event.BaseEvent,xyz.wagyourtail.jsmacros.core.language.EventContainer<?>,java.lang.Object,?>) (hi jep)
		"""
		pass

	@overload
	def andThen(self, after: Function) -> "MethodWrapper":
		"""Makes Function and BiFunction work together.
Extended so it's called on every type not just those 2.

		Args:
			after: put a MethodWrapper here when using in scripts. 
		"""
		pass

	@overload
	def negate(self) -> "MethodWrapper":
		"""Makes Predicate and BiPredicate work together
		"""
		pass

	pass


