from typing import overload
from typing import TypeVar

Thread = TypeVar["java.lang.Thread"]

class FWrapper_WrappedThread:
	thread: Thread
	notDone: bool

	@overload
	def __init__(self, thread: Thread, notDone: bool) -> None:
		pass

	@overload
	def waitFor(self) -> None:
		pass

	@overload
	def release(self) -> None:
		pass

	pass


