
def setDict(dictionary,keys,value):
	dic = dictionary
	for i in range(len(keys)-1):
		if keys[i] not in dic:
			dic[keys[i]] = {}
		dic = dic[keys[i]]
	dic[keys[-1]] = value
	pass

def getDict(dictionary,*keys,**kwargs):
	dic = dictionary
	rtn = None
	if "default" in kwargs:
		rtn = kwargs["default"]
	for key in keys:
		try:
			dic = dic[key]
		except:
			return rtn
	
	return dic



if __name__ == '__main__':
	from IutyLib.coding.unittest import *
	a = {'a':11,'b':{"b0":112,"b1":"ascii"}}
	i0 = getDict(a,"a")
	assertEqual(i0,11)

	i1 = getDict(a,"b","b0")
	assertEqual(i1,112)

	i3 = getDict(a,"b","b1",1)
	assertEqual(i3,'s')

	i4 = getDict(a,"c")
	assertEqual(i4,None)

	i5 = getDict(a,"c",default="no data")
	assertEqual(i5,"no data")
