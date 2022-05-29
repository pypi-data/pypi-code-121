# 2022-2-17  
import json,fire,sys, os 
from dic import * 

class util(object):

	def __init__(self):  pass

	def snt(self, name): 
		''' gzjc/clec/gaokao '''
		lines = readzip(name)
		[ print(line.strip()) for line in lines ]


if __name__ == '__main__':
	fire.Fire(util)