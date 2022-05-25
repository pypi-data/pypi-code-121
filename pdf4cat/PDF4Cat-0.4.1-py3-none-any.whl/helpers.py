import functools
import multiprocessing as mp
from queue import Empty

def run_in_subprocess(func):
	"""A decorator adding a kwarg to a function that makes it run in a subprocess.
	This can be useful when you have a function that may segfault.
	"""
	# This functools.wraps command makes this whole thing work
	# as a well-behaved decorator, maintaining the original function
	# name and docstring.
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		# Two extra kwargs, one public, are used for implementation.
		# One indicates that the user wants to run in a subprocess, the other
		# that the functtion is being called in the subprocess alreay.
		# The latter is the queue where the result gets posted to.
		run_in_subprocess = kwargs.pop('run_in_subprocess', True)
		subprocess_timeout = kwargs.pop('subprocess_timeout', None)
		queue = kwargs.pop('__queue', None)

		# create the machinery python uses to fork a subprocess
		# and run a function in it.
		if run_in_subprocess:
			q = mp.Queue()
			p = mp.Process(target=wrapper, args=args, kwargs={"run_in_subprocess":False, "__queue":q, **kwargs})
			# Because the use of this is avoiding crashes, rather than performance / parallelization
			# we wait for the subproces result immediately.
			p.start()
			try:
				result = q.get(timeout=subprocess_timeout)
				p.join()
			except Empty:
				p.terminate()
				raise TimeoutError("Function {} timed out with args: {}, {}".format(func, args, kwargs))
			# Pass on any exception raised in the subprocess
			if isinstance(result, BaseException):
				raise result
			return result
		else:
			# Run the function.  Eiher we are in the subprocess already or the user
			# does not want to run in the subproc.
			try:
				result = func(*args, **kwargs)
			except BaseException as error:
				# If running in standard mode just raise exceptions
				# as normal
				if queue is None:
					raise
				# Otherwise we pass the exception back to the caller
				# in place of the result
				result = error

			# This is optional, so the function can still just be called
			# normally with no effect.
			if queue is not None:
				queue.put(result)

			return result
	return wrapper

# need decorator for check args