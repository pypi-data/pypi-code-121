import subprocess
import os, sys
import inspect

__version__ = '2.0'


PACKAGE_NAME = None
locked = False

class m1n1Exception(Exception):
	def __init__(self, err, caller):
		self.err = err
		self.caller = caller
		super().__init__(f"{PACKAGE_NAME} failed with m1n1Exception:\n[exception]:\nwhat={self.err}\nfile={self.caller}")

def set_package_name(name):
	global locked
	locked = True
	global PACKAGE_NAME
	PACKAGE_NAME = name

def detachret(cond, err, dir):
	if (PACKAGE_NAME is None) and (not locked):
		sys.exit('Internal error: PACKAGE_NAME was not set!')
	if not (cond):
		caller_frame = inspect.stack()[1]
		caller = os.path.basename(caller_frame.filename)
		subprocess.run(('hdiutil','detach',dir), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		raise m1n1Exception(err, caller)

def retassure(cond, err):
	if (PACKAGE_NAME is None) and (not locked):
		sys.exit('Internal error: PACKAGE_NAME was not set!')
	if not (cond):
		caller_frame = inspect.stack()[1]
		caller = os.path.basename(caller_frame.filename)
		raise m1n1Exception(err, caller)

def reterror(err):
	if (PACKAGE_NAME is None) and (not locked):
		sys.exit('Internal error: PACKAGE_NAME was not set!')
	caller_frame = inspect.stack()[1]
	caller = os.path.basename(caller_frame.filename)
	raise m1n1Exception(err, caller)