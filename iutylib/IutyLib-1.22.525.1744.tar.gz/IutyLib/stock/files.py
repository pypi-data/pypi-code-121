from IutyLib.file.files import ByteFile
import os,datetime

stockroot = os.environ['STOCKSERVICEPATH'] + '//db//'

class DailyFile(ByteFile):
	def __init__(self,title):
		root = stockroot
		ByteFile.__init__(self,title,['common','daily'],'day',root)
		pass

class MinuteFile(ByteFile):
	def __init__(self,title,date):
		root = stockroot
		ByteFile.__init__(self,date.strftime('%Y%m%d'),['common','minute',title],'min',root)
		pass

class HourFile(ByteFile):
	def __init__(self,title):
		root = stockroot
		ByteFile.__init__(self,title,['common','hour'],'hor',root)
		pass

class QuarterFile(ByteFile):
	def __init__(self,title):
		root = stockroot
		ByteFile.__init__(self,title,['common','quarter'],'qut',root)
		pass

class StackFile(ByteFile):
	def __init__(self,title):
		root = stockroot
		ByteFile.__init__(self,title,['common','stack'],'stk',root)
		pass

class TransFile(ByteFile):
	def __init__(self,title,date):
		root = stockroot
		ByteFile.__init__(self,date.strftime('%Y%m%d'),['trans',title],'trs',root)
		pass

class CqcxDailyFile(ByteFile):
	def __init__(self,title):
		root = stockroot
		path = ['cqcx','daily']
		ByteFile.__init__(self,title,path,'cdy',root)
		self.daily = DailyFile(title)
		self.cqcxinfo = CqcxFile(title)
	
	def getLastCqcxDate(self):
		cqcxinfo = self.cqcxinfo.getData()
		if len(cqcxinfo) == 0:
			return datetime.date.max
		return cqcxinfo[-1][0]
	
	def write(self):
		dailydata = self.daily.getData()
		if len(dailydata) == len(self.getData()):
			return
		
		cqcxinfo = self.cqcxinfo.getData()
		needrewrite = False
		appends = []
		
		for i in range(0,len(dailydata)):
			if len(cqcxinfo) != 0:
				for cqcx in cqcxinfo:
					if dailydata[i][0] == cqcx[0]:
						ratio = (dailydata[i-1][4] - cqcx[1]/10.0 + cqcx[2] * cqcx[4] / 10.0) / (1.0 + (cqcx[4] + cqcx[3]) / 10.0) / dailydata[i-1][4]
						volratio = 1.0 + (cqcx[4] + cqcx[3]) / 10.0
						needrewrite = True
						for apindex in range(len(appends)):
							appenditem = appends[apindex]
							appendEx = (appenditem[0], appenditem[1]*ratio, appenditem[2]*ratio, appenditem[3]*ratio, appenditem[4]*ratio, appenditem[5], appenditem[6] * volratio)
							appends[apindex] = appendEx
						break
			appends.append(dailydata[i])
		
		if needrewrite:
			self.delete()
			self.getData(True)

		self.appendData(appends)
		
		
class QualifyFile(ByteFile):
	def __init__(self,title,qualify,cqcx = False):
		root = stockroot
		if cqcx:
			path = ['cqcx','qualification',qualify]
			ByteFile.__init__(self,title,path,'qlf',root)
		else:
			path = ['common','qualification',qualify]
			ByteFile.__init__(self,title,path,'qlf',root)

class BlockFile(ByteFile):
	def __init__(self,title,cqcx = False):
		root = stockroot
		if cqcx:
			path = ['cqcx','block']
		else:
			path = ['common','block']
		ByteFile.__init__(self,title,path,'blk',root,isserial = False)

class VLevelFile(ByteFile):
	def __init__(self,title,cqcx = False):
		root = stockroot
		if cqcx:
			path = ['cqcx','vlevel']
		else:
			path = ['common','vlevel']
		ByteFile.__init__(self,title,path,'vlv',root,isserial = False)

class CqcxFile(ByteFile):
	def __init__(self,title):
		root = stockroot
		path = ['cqcx','info']
		ByteFile.__init__(self,title,path,'cqx',root)

class WeeklyFile(ByteFile):
	def __init__(self,title,cqcx = False):
		root = stockroot
		self.needrewrite = False
		if cqcx:
			ByteFile.__init__(self,title,['cqcx','weekly',],'wkl',root)
			self.daily = CqcxDailyFile(title)
			if self.getLastIndex() > 0:
				if self.getData()[-1][0] < self.daily.getLastCqcxDate():
					pass
			self.needrewrite = True
		else:
			ByteFile.__init__(self,title,['common','weekly',],'wkl',root)
			self.daily = DailyFile(title)
	
	def getLastIndex(self):
		data = self.getData()
		dailydata = self.daily.getData()
		if len(dailydata) == 0:
			return 0
		if len(data) > 0:
			if data[-1][0] == dailydata[-1][0]:
				
				return -1
			for i in range(len(data),len(dailydata)):
				if data[-1][0] < dailydata[i][0]:
					return i
			return -1
		else:
			return 0
	
	def getWeeklyData(self,date):
		dailydata = self.daily.getData(False)
		d_index = -1
		for i in range(0,len(dailydata)):
			if dailydata[i][0] == date:
				d_index = i
		if d_index > -1:
			wiy = dailydata[d_index][0].strftime('%W')
			w = list(dailydata[d_index])
			for i in range(d_index-1,-1,-1):
				wiy0 = dailydata[i][0].strftime('%W')
				if wiy != wiy0:
					break
				else:
					w[1] = dailydata[i][1]
					if dailydata[i][2] > w[2]:
						w[2] = dailydata[i][2]
					if dailydata[i][3] < w[3]:
						w[3] = dailydata[i][3]
					w[5] += dailydata[i][5]
					w[6] += dailydata[i][6]
			w[6] = w[6]//10
			return tuple(w)
		return None
	
	def write(self):
		lastindex = self.getLastIndex()
		if lastindex == -1:
			return
		dailydata = self.daily.getData()
		appends = []
		
		for i in range(lastindex,len(dailydata)):
			week = self.getWeeklyData(dailydata[i][0])
			if week != None:
				appends.append(week)
				
		if self.needrewrite:
			self.delete()
			self.getData(True)
		self.appendData(appends)
		
class MonthFile(ByteFile):
	def __init__(self,title,cqcx = False):
		root = stockroot
		self.needrewrite = False
		if cqcx:
			ByteFile.__init__(self,title,['cqcx','month',],'mth',root)
			self.daily = CqcxDailyFile(title)
			if self.getLastIndex() > 0:
				if self.getData()[-1][0] < self.daily.getLastCqcxDate():
					pass
			self.needrewrite = True
		else:
			ByteFile.__init__(self,title,['common','month',],'mth',root)
			self.daily = DailyFile(title)
	
	def getLastIndex(self):
		data = self.getData()
		dailydata = self.daily.getData()
		if len(data) > 0:
			if data[-1][0] == dailydata[-1][0]:
				
				return -1
			for i in range(len(data),len(dailydata)):
				if data[-1][0] < dailydata[i][0]:
					return i
			return -1
		else:
			return 0
	
	def getMonthData(self,date):
		dailydata = self.daily.getData(False)
		d_index = -1
		for i in range(0,len(dailydata)):
			if dailydata[i][0] == date:
				d_index = i
		if d_index > -1:
			wiy = dailydata[d_index][0].strftime('%M')
			w = list(dailydata[d_index])
			for i in range(d_index-1,-1,-1):
				wiy0 = dailydata[i][0].strftime('%M')
				if wiy != wiy0:
					break
				else:
					w[1] = dailydata[i][1]
					if dailydata[i][2] > w[2]:
						w[2] = dailydata[i][2]
					if dailydata[i][3] < w[3]:
						w[3] = dailydata[i][3]
					w[5] += dailydata[i][5]
					w[6] += dailydata[i][6]
			w[6] = w[6]//300
			return tuple(w)
		return None
	
	def write(self):
		lastindex = self.getLastIndex()
		if lastindex == -1:
			return
		dailydata = self.daily.getData()
		appends = []
		
		for i in range(lastindex,len(dailydata)):
			week = self.getMonthData(dailydata[i][0])
			if week != None:
				appends.append(week)
				
		if self.needrewrite:
			self.delete()
			self.getData(True)
		self.appendData(appends)

class AccountFile(ByteFile):
	def __init__(self,title):
		root = stockroot
		ByteFile.__init__(self,title,['account'],'act',root)
		pass
	
class SimTradeFile(ByteFile):
	def __init__(self,title,method = 'default'):
		root = stockroot
		ByteFile.__init__(self,title,['sim',method],'std',root,isserial = False)