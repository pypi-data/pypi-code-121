from IutyLib.stock.files import SimTradeFile,CqcxFile
import datetime

class SimuTrader:
	def __init__(self,code,methodmark,dismark):
		self._trade = []
		self._data = []
		self._method = methodmark
		self._dis = dismark
		self._file = SimTradeFile(code,"{}_{}".format(methodmark,dismark))
		self._cqcxdata = CqcxFile(code).getData()
		self._code = code
		pass
	
	@property
	def Empty(self):
		return len(self._trade) == 0
	
	@property
	def Hold(self):
		return len(self._trade) == 2

	@property
	def Fin(self):
		return len(self._trade) == 4
	
	

	def simuBuy(self,price,daily,tex = 1.0003):
		if self.Hold:
			return
		else:
			if price == daily[2]:
				return
			if price < daily[3]:
				return
			if price > daily[2]:
				price = daily[2]
			self._trade.append(daily[0])
			self._trade.append(price*tex)
		pass

	def simuSell(self,price,daily,tex = 0.9987):
		if not self.Hold:
			return
		else:
			if price == daily[3]:
				return
			if price > daily[2]:
				return
			if price < daily[3]:
				price = daily[3]
			self._trade.append(daily[0])
			self._trade.append(price*tex)
		pass

	def setParams(self,reason,params,holdlimit = 270):
		if self.Fin:
			self._trade.append(reason)
			self._trade+=params
			if (not self.delCqcx()) & (not self.delLongHold(holdlimit)):
				self._data.append(tuple(self._trade))
			self._trade = []
		pass
	
	def delLongHold(self,holdlimit):
		if len(self._trade) >= 4:
			if (self._trade[2] - self._trade[0]).days > holdlimit:
				#print(' ')
				#print(self._trade)
				return True
		return False

	def delCqcx(self):
		if len(self._trade) >= 4:
			for cqcx in self._cqcxdata:
				if (cqcx[0] >= self._trade[0]) & (cqcx[0] <= self._trade[2]):
					#print('del cqcx code:{},date:{}'.format(self._code,cqcx[0]))
					return True
		return False

	def simuFinish(self):
		if len(self._data) > 0:
			self._file.appendData(self._data)
		pass
	
	def deleteFiles(self):
		s_file = SimTradeFile(' ',"{}_{}".format(self._method,self._dis))
		s_file.removeFiles()

