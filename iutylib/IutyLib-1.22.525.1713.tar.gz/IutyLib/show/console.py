import datetime
class Process:
	def __init__(self,title,tasks):
		self.starttime = datetime.datetime.now()
		self.title = title
		self.total = len(tasks)

	def showInConsole(self,remain,**kwargs):
		if self.total == 0:
			print('show process error,tasks must not zero')
		process = round(100.0 * (self.total-remain)/self.total,2)
		str_args = ''
		if len(kwargs)>0:
			for arg in kwargs:
				str_args = str_args + "\t@" + arg + ':{0}'.format(kwargs[arg])
		if process > 0:
			endtime = self.starttime + (datetime.datetime.now() - self.starttime)/(process/100.0)
			endstr = endtime.strftime('%Y-%m-%d %H:%M:%S')
		else:
			endstr = '-'
		print('\r'+' '*len(str_args)*2,end='')
		print('\r{0} process -> {1}% will end - > {2} {3}'.format(self.title,process,endstr,str_args),end='')
		if remain == 0:
			print('')
			
def showProcessInConsole(title,starts,remain,total,**kwargs):
	if total == 0:
		print('show process error,tasks must not zero')
	process = round(100.0 * (total - remain)/total,2)
	str_args = ''
	if len(kwargs) > 0:
		for arg in kwargs:
			str_args = str_args + "\t@" + arg + ':{0}'.format(kwargs[arg])
	if process > 0:
		endtime = starts + (datetime.datetime.now() - starts)/(process/100.0)
		endstr = endtime.strftime('%Y-%m-%d %H:%M:%S')
	else:
		endstr = '-'
	print('\r'+' '*50,end='')
	print('\r{0} process -> {1}% will end - > {2} {3}'.format(title,process,endstr,str_args),end='')
	if remain == 0:
		print('')


def showDict(dictionary,index = 0):
	if type(dictionary) != dict:
		print('\t'*(index+1),end='')
		print(dictionary)
		return
	print('\t'*index + '{')
	for dic in dictionary:
		print('\t'*(index+1),end='')
		print(dic,end='')
		print(':')
		showDict(dictionary[dic],index+1)
	print('\t'*index + '}')
	pass

def showTime():
	print('\r'+' '*60,end='')
	print('\r'+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),end='')

def testShowDict():
	dic = {'root':{'item1':{'item11':11,'item12':12},'item2':0}}
	showDict(dic)
	pass

def showInOneLine(text):
	print("\r" + " "*int(1.1*len(text)),end='')
	print("\r"+text,end='')
	pass

if __name__ == '__main__':
	testShowDict()
	
		

