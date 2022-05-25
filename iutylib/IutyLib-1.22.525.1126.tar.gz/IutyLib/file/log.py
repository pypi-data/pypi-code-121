from IutyLib.file.files import StringFile
import os,datetime,threading

class Log(StringFile):
	def __init__(self,root = './/logs//',title = 'log'):
		if not os.path.exists(root):
			p = '.'
			ps = root.split('//')
			for i in range(1,len(ps)-1):
				
				p = p + '//' + ps[i]
				if not os.path.exists(p):
					os.makedirs(p)
		StringFile.__init__(self,root, title)
		pass
	
	def getkwargs(**kwargs):
		argmsg = ''
		for arg in kwargs:
			argmsg = argmsg + '@' + str(arg) + ':' + str(kwargs[arg]) + "; "
		return argmsg

	def appendLog(self,item,message,**kwargs):
		msg = datetime.datetime.now().strftime("%H:%M:%S.%f") + "[" + item + "]:" + message
		if len(kwargs) > 0:
			msg = msg + Log.getkwargs(**kwargs)
		self.append(msg)
		
		pass


class SimpleLog:
	def __init__(self,path = './/logs//',level = 1):
		#path => log dir
		#level:all,debug,warn,other/info,error
		#        0,    1,   2,         3,    4
		self.lock = threading.Lock()
		self.log = Log(path)
		pass

	def error(self,msg,**kwargs):
		self.lock.acquire()
		self.log.appendLog('error',msg,**kwargs)
		self.lock.release()

	def info(self,msg,**kwargs):
		self.lock.acquire()
		self.log.appendLog('info',msg,**kwargs)
		self.lock.release()

	def debug(self,msg,**kwargs):
		self.lock.acquire()
		self.log.appendLog('debug',msg,**kwargs)
		self.lock.release()

	def warn(self,msg,**kwargs):
		self.lock.acquire()
		self.log.appendLog('warn',msg,**kwargs)
		self.lock.release()

	def other(self,cmd,msg,**kwargs):
		self.lock.acquire()
		self.log.appendLog(cmd,msg,**kwargs)
		self.lock.release()

class LogManage:
	def __init__(self):
		log_d = SimpleLog()
		self.__logs__ = {'Default':log_d}
		pass

	def addLog(self,name,path='.//logs//',level = 1):
		if name in self.__logs__:
			return
		log_a = SimpleLog(path=path,level=level,title = name)
		self.__logs__[name] = log_a
		pass

	def getLog(self,name = 'Default'):
		if name in self.__logs__:
			return self.__logs__[name]
		else:
			return self.__logs__['Default']

log4py = LogManage()
