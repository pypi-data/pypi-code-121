from IutyLib.stock.files import BlockFile,VLevelFile,DailyFile
from IutyLib.stock.qualification import VLs,VHs

class Block:
	from abc  import abstractmethod
	def __init__(self,code,cqcx = False):
		self.qfile = BlockFile(code,cqcx)
		if cqcx:
			self.dfile = CqcxDailyFile(code)
		else:
			self.dfile = DailyFile(code)
		self.d_data = self.dfile.getData()
		self.code = code
		q_data = self.qfile.getData()
		self.q_data = {}
		self.blockvalue = None
		if len(q_data) == 0:
			return
		for q in q_data:
			self.q_data[q[0]] = q[1] 
			
		pass
	
	def getNextIndex(self):
		if len(self.q_data) == 0:
			return 0
		sum = 0
		for v in self.q_data:
			sum += self.q_data[v]
		times = sum/2
		if times == len(self.d_data):
			return -1
		else:
			return int(times)
		
		
	def calcAppends(self):
		last = self.getNextIndex()
		if last == -1:
			return last
		d_data = self.d_data
		q_data = self.q_data
		
		for i in range(last,len(d_data)):
			lv = d_data[i][2]
			hv = d_data[i][3]
			if not lv in q_data:
				q_data[lv] = 0
			if not hv in q_data:
				q_data[hv] = 0
			q_data[lv] += 1
			q_data[hv] += 1
		return last
	
	def writeAppends(self):
		last = self.calcAppends()
		if last == -1:
			return
		
		appends = []
		for q in self.q_data:
			appends.append((q,self.q_data[q]))
		self.qfile.appendData(appends)
		pass
	
	def getBlockValues(self):
		sortedkeys = sorted(self.q_data.keys())
		sorteddict = {}
		for key in sortedkeys:
			sorteddict[key] = 0
			for key0 in self.q_data:
				if (abs(key0 - key))/key < 0.005:
					sorteddict[key] += self.q_data[key0]
		
		mainvalue = 0
		mainkey = None
		for key in sorteddict:
			if sorteddict[key] > mainvalue:
				mainvalue = sorteddict[key]
				mainkey = key
		
		v_max = max(list(sorteddict.keys()))
		v_min = min(list(sorteddict.keys()))
		valuedict = {}
		for i in range(0,100):
			up0 = 1.05**i
			up1 = 1.05**(i+1)
			down0 = 0.95**i
			down1 = 0.95**(i+1)
			upvalue = None
			upcount = 0
			downvalue = None
			downcount = 0
			for key in sorteddict:
				if (key>=mainkey*up0) & (key<mainkey*up1):
					if sorteddict[key] > upcount:
						upvalue = key
						upcount = sorteddict[key]
				if (key<=mainkey*down0) & (key>mainkey*down1):
					if sorteddict[key] > downcount:
						downvalue = key
						downcount = sorteddict[key]
			if upvalue!= None:
				valuedict[upvalue] = upcount
			if downvalue != None:
				valuedict[downvalue] = downcount
		
		sortedblockkeys = sorted(valuedict.keys())
		sortedblockvalues = {}
		for key in sortedblockkeys:
			sortedblockvalues[key] = valuedict[key]
		return sortedblockvalues
	
	def getValues(self):
		if self.blockvalue == None:
			self.blockvalue = self.getBlockValues()
		return self.blockvalue
	
class VLevel:
	from abc  import abstractmethod
	def __init__(self,code,cqcx = False):
		self.qfile = VLevelFile(code,cqcx)
		if cqcx:
			self.dfile = CqcxDailyFile(code)
		else:
			self.dfile = DailyFile(code)
		self.d_data = self.dfile.getData()
		self.code = code
		q_data = self.qfile.getData()
		self.q_data = {}
		self.blockvalue = None
		if len(q_data) == 0:
			return
		for q in q_data:
			self.q_data[q[0]] = (q[1],q[2])
			
		pass
	
	def getDataFromDaily(self,item):
		dict_rtn = {}
		last = len(self.d_data)-1
		if last == 0:
			return dict_rtn
		d_data = self.d_data
		level = 1
		while 1:
			if item == 3:
				vs = VLs(self.d_data,last,3,level)
			else:
				vs = VHs(self.d_data,last,2,level)
				#print(vs)
			if len(vs) == 0:
				#no value
				break
			else:
				#value set
				for v in vs:
					#print(v)
					if not v[item] in dict_rtn:
						dict_rtn[v[item]] = (1,0)
						
					dict_rtn[v[item]] = (dict_rtn[v[item]][0],dict_rtn[v[item]][1]+1)
					if dict_rtn[v[item]][0] < level:
						print('rrrr')
						dict_rtn[v[item]] = (level,dict_rtn[v[item]][1])
			level += 1
		return dict_rtn
	
	def mergeUnilateral(self,dict0,range = 0.005):
		for item in dict0:
			itemvalue = dict0[item]
			for item1 in dict0:
				if item1 != item:
					item1value = dict0[item1]
					if (item1value[0] < itemvalue[0]) & (item1 > item * 1-range) & (item1 < item * 1+range):
						dict0[item] = (dict0[item][0],itemvalue[1] + item1value[1])
		pass
	
	def calcAppends(self):
		
		vls = self.getDataFromDaily(3)
		#print(vls)
		vhs = self.getDataFromDaily(2)
		print(vhs)
		
		self.mergeUnilateral(vls)
		self.mergeUnilateral(vhs)
		
		vs = {}
		for item in vls:
			vs[item] = vls[item]
		for item in vhs:
			if item in vs:
				vs[item] = (vs[item][0]+vhs[item][0])
			else:
				vs[item] = (vhs[item][0],0)
			print('ttt')
			print(vs[item])
			vs[item] = (vs[item][0],vs[item][1] + vhs[item][1])
		self.mergeUnilateral(vs)
		self.q_data = vs
		#print(len(self.q_data))
		
	
	def writeAppends(self):
		self.calcAppends()
		
		appends = []
		for q in self.q_data:
			appends.append((q,self.q_data[q][0],self.q_data[q][1]))
		self.qfile.appendData(appends)
		pass
	
	def getLValues(self):
		sortedkeys = sorted(self.q_data.keys())
		sorteddict = {}
		#print(len(sortedkeys))
		for key in sortedkeys:
			b_select = True
			for key0 in self.q_data:
				if key != key0:
					if (key0 < key * 1.05) & (key0 > key * 0.95):
						if self.q_data[key][1] * self.q_data[key][2] < self.q_data[key0][1] * self.q_data[key0][2]:
							b_select = false
							break
			if b_select:
				sorteddict[key] = self.q_data[key]
		return sorteddict
	
	def getValues(self):
		if self.blockvalue == None:
			self.blockvalue = self.getBlockValues()
		return self.blockvalue
