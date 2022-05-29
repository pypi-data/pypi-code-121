#2022.4.13
import json,os,time,redis, fire, socket

class util(object): 

	def __init__(self,  host='127.0.0.1', port=6379, db=0): 
		self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True) 

	def dump(self, name, ibeg="-", iend="+"): 
		for ar in self.r.xrange(name, ibeg, iend): 
			print (ar) 

if __name__ == '__main__':
	fire.Fire(util)