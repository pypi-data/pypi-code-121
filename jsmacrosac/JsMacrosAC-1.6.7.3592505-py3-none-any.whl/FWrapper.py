from typing import overload
from typing import TypeVar
from .IFWrapper import IFWrapper
from .PerExecLanguageLibrary import PerExecLanguageLibrary
from .BaseScriptContext import BaseScriptContext
from .MethodWrapper import MethodWrapper

Function = TypeVar["java.util.function.Function_java.lang.Object[],java.lang.Object_"]
LinkedBlockingQueue = TypeVar["java.util.concurrent.LinkedBlockingQueue_xyz.wagyourtail.jsmacros.core.library.impl.FWrapper.WrappedThread_"]

class FWrapper(IFWrapper, PerExecLanguageLibrary):
	"""FunctionalInterface implementation for wrapping methods to match the language spec.

An instance of this class is passed to scripts as the 'JavaWrapper' variable.

Javascript:
language spec requires that only one thread can hold an instance of the language at a time,
so this implementation uses a non-preemptive queue for the threads that call the resulting MethodWrapper .

JEP:
language spec requires everything to be on the same thread, on the java end, so all calls to MethodWrapper call back to JEP's starting thread and wait for the call to complete. This means that JEP can sometimes have trouble
closing properly, so if you use any MethodWrapper , be sure to call FConsumer#stop(), to close
the process,
otherwise it's a memory leak.

Jython:
no limitations

LUA:
no limitations\n
	Since: 1.2.5, re-named from 'consumer' in 1.4.0 
	"""
	tasks: LinkedBlockingQueue

	@overload
	def __init__(self, ctx: BaseScriptContext, language: Class) -> None:
		pass

	@overload
	def methodToJava(self, c: Function) -> MethodWrapper:
		"""
		Since: 1.3.2 

		Args:
			c: 

		Returns:
			a new MethodWrapper 
		"""
		pass

	@overload
	def methodToJavaAsync(self, c: Function) -> MethodWrapper:
		"""
		Since: 1.3.2 

		Args:
			c: 

		Returns:
			a new MethodWrapper 
		"""
		pass

	@overload
	def deferCurrentTask(self) -> None:
		"""JS only, puts current task at end of queue.
use with caution, don't accidentally cause circular waiting.
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


