import datetime
def getSerialItem(serial,index,key=0,asIndex = False):
	if len(serial) == 0:
		return None
		
	start = 0
	end = len(serial)
	
	while True:
		
		cur = (end-start)//2 + start
		
		if serial[cur][key] == index:
			if asIndex:
				return cur
			else:
				return serial[cur]
		if (end == start) | (end == (start+1)):
			return None
		if serial[cur][key] < index:
			start = cur
		
		else:
			end = cur
		#print('{},{}-{}'.format(start,end,index))
	pass
	