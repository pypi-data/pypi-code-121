from abc import abstractmethod
import datetime,os,shutil
import IutyLib.commonutil.config as config
import IutyLib.commonutil.dict
from IutyLib.file.log import SimpleLog
from IutyLib.show.console import Process as ShowProcess


def initPath(file):
	envpath = os.path.dirname(file)
	if not envpath in os.sys.path:
		os.sys.path.append(envpath)


class ProxyBase:
	def __init__(self,name = None):
		configpath = ".//config//"
		if name == None:
			self.name = self.__class__.__name__
			self.__configpath__ = configpath + self.__class__.__name__ + ".pkl"
		else:
			self.name = name
			self.__configpath__ = configpath + name + ".pkl"
				
		if not os.path.exists(self.__configpath__):
			self.__config__ = {}
			self.initConfig()
		self.__config__ = config.getPickleData(self.__configpath__)


		if "logpath" in self.__config__:
			self.log = SimpleLog(self.__config__["logpath"])
		else:
			self.log = SimpleLog()

		self.__cmds__ = {}

		self.initResource()

		pass

	@abstractmethod
	def initConfig(self):
		#user should set default config here
		pass

	def setConfig(self,keys,value):
		commonutil.setDict(self.__config__,keys,value)
		self.saveConfig()
		
	def saveConfig(self):
		config.savePickleData(self.__configpath__,self.__config__)

	@abstractmethod
	def initResource(self):
		#init class resource here
		pass

	@abstractmethod
	def initCmd(self):
		#regedit cmd here
		pass

	def excuteCmd(self,keyword,**kwargs):
		if keyword in self.__cmds__:
			return self.__cmds__[keyword].__call__(**kwargs)
		return None

class TaskProxy(ProxyBase):
	def __init__(self,name = None):
		ProxyBase.__init__(self,name)
		self.__taskname__ = None
		self.__tasks__ = []
		self.OnTaskFinished = None
		
	@property
	def Finish(self):
		return len(self.__tasks__) == 0
	
	@property
	def TaskName(self):
		return self.__taskname__
	
	def getTaskStatus(self,title):
		return self.__config__['tasks'][title]
	
	def setTaskFinishStatus(self,value):
		self.setConfig(['tasks',self.taskname],value)
		self.taskname = None
	
	def initTask(self,title,tasks):
		self.taskname = title
		self.__tasks__ += tasks
		self.setConfig(['tasks',title],datetime.datetime.now())
		self.p_show = ShowProcess(title,self.__tasks__)
	
	@abstractmethod
	def runTask(self,arg):
		#ruturn the param of task
		pass

	def excuteTask(self):
		if len(self.__tasks__) == 0:
			return
		task = self.__tasks__.pop(0)
		
		kwargs = self.runTask(task)
		
		if kwargs == None:
			kwargs = {}
		self.p_show.showInConsole(len(self.__tasks__),**kwargs)

#abort
class ServiceCommand:
	def __init__(self):
		self.__cmds__ = {}
		self.__subobj__ = []
		
		self.initCmd()
		
	@abstractmethod
	def initCmd(self):
		#init cmd format here
		pass
	
	def excuteCmd(self,keyword,**kwargs):
		if keyword in self.__cmds__:
			print('service excute command [{0}]...,'.format(keyword))
			return self.__cmds__[keyword].__call__(**kwargs)
		else:
			for sub in self.__subobj__:
				result = sub.excuteCmd(keyword,**kwargs)
				if result != None:
					print('{0} excute command [{1}]...'.format(keyword))
					return result
		return None

	def invokeCmd(self,cmdstring):
		rtn = {'success': False}
		temp0 = cmdstring.split(',')
		keyword = temp0[0]
		kwargs = {}
		if len(temp0) > 0:
			
			for i in range(1,len(temp0)):
				print(temp0)
				temp1 = temp0[i].split('=')
				if len(temp1) != 2:
					print('kwarg error in [{0}]'.format(temp0[i]))
					return rtn
				kwargs[temp1[0]] = temp1[1]
		print('receive command [{0}]...,'.format(cmdstring))
		rtn['success'] = True
		result = self.excuteCmd(keyword,**kwargs)
		if result is None:
			print('service have no result...')
		else:
			print('result here...:')
			for r in result:
				print('\t{0}->{1}'.format(r,result[r]))
			print('result print finished...')
		rtn['data'] = result
		return rtn
	
	def cmd(func):
		self.__cmds__[func.__name__] = func



	
	
		
'''

'''
class ServiceFunc:
	def __init__(self):
		self.__cmds__ = {}
		self.__blls__ = {}
		pass
		
	
	def cmd(func):
		servicefunc.__cmds__[func.__name__.lower()] = func
		return func

	def invokeCmd(obj,cmdstring):
		rtn = {'success': False}
		cmdstring = cmdstring.lower()
		temp0 = cmdstring.split(',')
		keyword = temp0[0]
		kwargs = {}
		if len(temp0) > 0:
			for i in range(1,len(temp0)):
				#print(temp0)
				temp1 = temp0[i].split('=')
				if len(temp1) != 2:
					print('kwarg error in [{0}]'.format(temp0[i]))
					return rtn
				kwargs[temp1[0]] = temp1[1]
		print('receive command [{0}]...,'.format(cmdstring))
		rtn['success'] = True
		
		if keyword == 'getcmds':
			rtn['result'] = list(servicefunc.__cmds__.keys())
			print(rtn)
			return rtn
		
		result = None
		if keyword in servicefunc.__cmds__:
			result = servicefunc.__cmds__[keyword].__call__(obj,**kwargs)
		
		print(result)
		print('result print finished...')
		rtn['result'] = result
		return rtn
	
	def bll(func):
		servicefunc.__blls__[func.__name__.lower()] = func
		return func
	
	def invokeBll(obj,**kwargs):
		rtn = {'success':False,'err':'service has no this func'}
		funcname = kwargs['func'].lower()
		if not funcname in servicefunc.__blls__:
			return rtn
		kwargs.pop('func')
		result = servicefunc.__blls__[funcname].__call__(obj,**kwargs)
		return result

class WebServiceFunc:
	def __init__(self):
		self.__blls__ = {}
		self._servicetype = 'WebService'
		pass
	
	
	def bll(func):
		servicefunc.__blls__[func.__name__.lower()] = func
		return func
	
	def invokeBll(obj,**kwargs):
		rtn = {'success':False,'err':'service has no this func'}
		funcname = kwargs['func'].lower()
		if not funcname in servicefunc.__blls__:
			return rtn
		kwargs.pop('func')
		result = servicefunc.__blls__[funcname].__call__(obj,**kwargs)
		return result

servicefunc = ServiceFunc()
webservicefunc = WebServiceFunc()

class ServiceBase:
	def __init__(self):
		self.__configpath__ = './/config//config.pkl'
		if os.path.exists(self.__configpath__):
			self.config = {}
			self.initConfig()
		self._servicetype = 'Service'
		self._run = False
		self.config = config.getPickleData(self.__configpath__)

		self.log = SimpleLog('.//logs//HostInfo//')
		
		self.initResource()
		
		pass

	@abstractmethod
	def initConfig(self):
		#set config default value here
		pass

	def setConfig(self,keys,value):
		commonutil.setDict(self.config,keys,value)
		config.savePickleData(self.__configpath__,self.config)

	@abstractmethod
	def initResource(self):
		#init Proxy Resource here
		pass
	
	@abstractmethod
	def start(self,**kwargs):
		return True
	
	@ServiceFunc.cmd
	def doStart(self,**kwargs):
		self._run = self.start(**kwargs)
		return {'run':self._run}
		
	
	@abstractmethod
	def stop(self,**kwargs):
		return False
	
	@ServiceFunc.cmd
	def doStop(self,**kwargs):
		self._run = self.stop(**kwargs)
		return {'run':self._run}
		
	@ServiceFunc.cmd
	def getStatus(self,**kwargs):
		return {'run':self._run}
	
	pass

class InitHelper:
	def __init__(self):
		self.basepath = './/'
		
		self.servicepath = self.basepath + 'Service//'
		self.proxypath = self.servicepath + 'Proxys//'
		self.logpath = self.servicepath + 'Logs//'
		self.configpath = self.servicepath + 'Config//'
		
		self.testpath = self.basepath + 'Test//'
		self.testproxypath = self.testpath + 'Proxys//'
		self.testlogpath = self.testpath + 'Logs//'
		self.testconfigpath = self.testpath + 'Config//'
		self.testresultpath = self.testpath + 'Result//'
		
		self.templatepath = os.environ['PythonPath'] + '//template//'
	
	def initFrameWork(self):
		if not os.path.exists(self.basepath):
			os.mkdir(self.basepath)
		
		if not os.path.exists(self.servicepath):
			os.mkdir(self.servicepath)
		
		if not os.path.exists(self.proxypath):
			os.mkdir(self.proxypath)
		
		if not os.path.exists(self.logpath):
			os.mkdir(self.logpath)
		
		if not os.path.exists(self.configpath):
			os.mkdir(self.configpath)
		
		if not os.path.exists(self.testpath):
			os.mkdir(self.testpath)
		
		if not os.path.exists(self.testproxypath):
			os.mkdir(self.testproxypath)
		
		if not os.path.exists(self.testlogpath):
			os.mkdir(self.testlogpath)
		
		if not os.path.exists(self.testconfigpath):
			os.mkdir(self.testconfigpath)
		
		if not os.path.exists(self.testresultpath):
			os.mkdir(self.testresultpath)
		
		if not os.path.exists(self.servicepath + 'Service.py'):
			if os.path.exists(self.templatepath+'Service.py'):
				shutil.copy(self.templatepath+'Service.py',self.servicepath + 'Service.py')
			else:
				print('Warning:Service template not exists')
		
		if not os.path.exists(self.servicepath + '__run__.py'):
			if os.path.exists(self.templatepath+'__run__.py'):
				shutil.copy(self.templatepath+'__run__.py',self.servicepath + '__run__.py')
			else:
				print('Warning:__run__ template not exists')