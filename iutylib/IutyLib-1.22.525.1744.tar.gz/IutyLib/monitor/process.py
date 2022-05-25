import threading
import datetime
class ProcessBar:
	_cur = 0
	_total = 0
	
	def __init__(self,name):
		self._name = name
		self._start = datetime.datetime.now()
		self._lock = threading.Lock()
		pass
	
	@property
	def Status(self):
		self._lock.acquire()
		rtn = {'Name':self._name,'Start':self._start,'Cur':self._cur,'Total':self._total}
		self._lock.release()
		return rtn
	
	def setCur(self,value):
		if type(value) != int:
			return
		self._lock.acquire()
		self._cur = value
		self._lock.release()
		pass
	
	def setTotal(self,value):
		if type(value) != int:
			return
		self._lock.acquire()
		self._total = value
		self._lock.release()
		pass