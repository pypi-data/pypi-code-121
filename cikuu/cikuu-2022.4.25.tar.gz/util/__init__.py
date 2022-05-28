# 2022.3.10
import requests 
from collections import	Counter, defaultdict

import hashlib
sntmd5	= lambda sntarr: " ".join([hashlib.md5(snt.strip().lower().encode("utf-8")).hexdigest() for snt in sntarr if len(snt) > 1])
md5text	= lambda text: hashlib.md5(text.strip().encode("utf-8")).hexdigest()

from math import log as ln
def likelihood(a,b,c,d, minus=None):  #from: http://ucrel.lancs.ac.uk/llwizard.html
	try:
		if a is None or a <= 0 : a = 0.000001
		if b is None or b <= 0 : b = 0.000001
		E1 = c * (a + b) / (c + d)
		E2 = d * (a + b) / (c + d)
		G2 = round(2 * ((a * ln(a / E1)) + (b * ln(b / E2))), 2)
		if minus or  (minus is None and a/c < b/d): G2 = 0 - G2
		return G2
	except Exception as e:
		print ("likelihood ex:",e, a,b,c,d)
		return 0

def xblpop(r, name, arr, timeout=10, suc_prefix='suc:', err_prefix="err:"):
	''' name:xsnt/xsnts, arr: {"snt": "hello"}  added 2022.4.4 '''
	id  = r.xadd(name, arr)
	return r.blpop([f"{suc_prefix}{id}",f"{err_prefix}{id}"], timeout=timeout)

def getlog(logfile='daily.log'):
	import logging
	from logging.handlers import TimedRotatingFileHandler
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)
	handler = TimedRotatingFileHandler(logfile, when="midnight", interval=1)
	handler.suffix = "%Y%m%d"
	logger.addHandler(handler)
	handler.setLevel(logging.INFO) 
	handler.setFormatter(logging.Formatter("%(message)s"))
	logger.addHandler(handler)
	return logger

def readline(infile, sepa=None):
	with open(infile, 'r', encoding='utf-8') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def process(infile, outfile, asjson=True, func = lambda x: x):
	''' line processor, added 2022.3.20  '''
	print ("process started:", infile, outfile, flush=True)
	with open(outfile, 'w') as fw: 
		for line in readline(infile):
			try:
				fw.write( func( json.loads(line.strip(), strict=False) if asjson else line.strip())  + "\n")
			except Exception as ex:
				print ("process ex:", ex, line) 
	print ('process finished:', infile) 

def hset_if_greater(r, key, eid, ver ): 
	res = r.hget(key, eid)
	try: 
		if not res :
			r.hset(key, eid, ver)
		else: 
			if int(ver) > int(res) : r.hset(key, eid, ver)
	except Exception as e:
		print("ex:", e, eid)

if __name__ == '__main__': 
	pass 
	#logger = getlog()
	#print (logger) 