from typing import overload
from typing import TypeVar
from .MethodWrapper import MethodWrapper

T = TypeVar("T")

class IFWrapper:
	"""FunctionalInterface implementation for wrapping methods to match the language spec.

An instance of this class is passed to scripts as the 'consumer' variable.

Javascript:
language spec requires that only one thread can hold an instance of the language at a time,
so this implementation uses a non-preemptive queue for the threads that call the resulting MethodWrapper .

JEP:
language spec requires everything to be on the same thread, on the java end, so all calls to MethodWrapper call back to JEP's starting thread and wait for the call to complete. This means that JEP can sometimes have trouble
closing properly, so if you use any MethodWrapper , be sure to call FConsumer#stop(), to close the process,
otherwise it's a memory leak.

Jython:
no limitations

LUA:
no limitations\n
	Since: 1.2.5, re-named from 'consumer' in 1.3.2 
	"""

	@overload
	def methodToJava(self, c: T) -> MethodWrapper:
		"""
		Since: 1.4.0 

		Args:
			c: 

		Returns:
			a new MethodWrapper 
		"""
		pass

	@overload
	def methodToJavaAsync(self, c: T) -> MethodWrapper:
		"""
		Since: 1.4.0 

		Args:
			c: 

		Returns:
			a new MethodWrapper 
		"""
		pass

	@overload
	def stop(self) -> None:
		"""Close the current context, more important in JEP as they won't close themselves if you use other functions in
this class\n
		Since: 1.2.2 
		"""
		pass

	pass


