#!/usr/bin/env python
import redis ,fire,json, fileinput #ln -s /home/cikuu/cikuu/bin/redisdl.py redisdl

def readline(infile, sepa=None):
	with open(infile, 'r') as fp: #, encoding='utf-8'
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

class util(object):
	def __init__(self, host = '127.0.0.1', port=6666, db=0, password=None):
		self.r = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True) if password else redis.Redis(host=host, port=port, db=db, decode_responses=True)


	def dump(self, outfile, pattern=None):
		''' dump to db-0.ktv, (key, type, value) '''
		with open(outfile, 'w') as fw:
			for k in self.r.scan_iter() if not pattern else r.keys(pattern): 
				try:
					type =  self.r.type(k)
					if type == 'hash': 
						fw.write(f"{k}\t{type}\t" + json.dumps(self.r.hgetall(k)) + "\n")
					elif type == 'zset': 
						fw.write(f"{k}\t{type}\t" + json.dumps( dict(self.r.zrevrange(k, 0,-1, True) )) + "\n")
					elif type == 'list': 
						fw.write(f"{k}\t{type}\t" + json.dumps( self.r.lrange(k, 0,-1) ) + "\n")
					elif type == 'set': 
						fw.write(f"{k}\t{type}\t" + json.dumps( self.r.smembers(k)) + "\n")
					elif type == 'string': 
						fw.write(f"{k}\t{type}\t" + json.dumps(self.r.get(k)) + "\n")
				except Exception as e: 
					print ( "ex:" , e, k ) 
		print ("finished dumping:", outfile, self.r)

	def keys(self, pattern, type='string'):
		''' dump keys of pattern with the given type, 2021.9.27 '''
		for k in self.r.keys(pattern): 
			if type == self.r.type(k): 
				print(k)

	def loadstr(self, infile):
		''' load k,v to r.set (string type), 2022.3.13 '''
		print ("start to load", infile, self.r, flush=True)
		for line in readline(infile):
			try:
				k,v = line.strip().split("\t")[0:2]
				self.r.set(k,v) 
			except Exception as e: 
				print ("ex:", e, "\t|",  line) 
		print ("finished loading:", infile, self.r)

	def restore(self, infile):
		r = self.r
		for line in readline(infile):
			try:
				k,type,v = line.strip().split("\t")
				if type == 'hash': 
					r.hmset(k, json.loads(v))
				elif type == 'zset': 
					r.zadd(k, json.loads(v))
				elif type == 'list': 
					for s in json.loads(v):
						r.rpush(k, s)
				elif type == 'set': 
					for s in json.loads(v):
						r.sadd(k, s)
				elif type == 'string': 
					r.set(k, json.loads(v)) ## \n included 
			except Exception as e: 
				print ("ex:", e, "\t|",  line) 
		print ("finished loading:", infile, r)

def delkeys(pattern, host = 'localhost',port=6379,  db=0):
	''' delete keys by pattern '''
	r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
	print (r, pattern , flush=True)
	for k in r.keys(pattern): 
		r.delete(k)
	print ("finished deleting:", pattern, r)

def tokv(infile, host='127.0.0.1', port=6379, db=0):
	''' submit a.tsv to redis str '''
	r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
	for line in fileinput.input(infile):
		arr = line.strip().split("\t")
		if len(arr) >= 2 : 
			r.setnx(arr[0].strip(), arr[1].strip())
	print("finished:", infile)

def tsv_to_hash(infile, hkey, host='127.0.0.1', port=6379, db=0):
	''' submit a.tsv to redis hash, added 2021.10.6 '''
	r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
	for line in fileinput.input(infile):
		arr = line.strip().split("\t")
		if len(arr) >= 2 : 
			r.hset(hkey, arr[0].strip(), arr[1].strip())
	print("finished:", infile, hkey)

def line_to_list(infile, lkey, host='127.0.0.1', port=6379, db=0):
	''' submit a.tsv to redis list, ie: csxx , added 2021.10.7 '''
	r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
	r.delete(lkey)
	for line in fileinput.input(infile):
		line = line.strip()
		if line: 
			r.rpush(lkey, line)
	print("finished:", infile, lkey)

if __name__ == '__main__':
	fire.Fire(util)

'''
move 248 page data to 114:

1. log in 248 , dump data
python3 redisdl.py dump page-248.ktv --patern "page:*"

2. copy  page-248.ktv to 124 

3. log in 114, load data into redis 
python3 redisdl.py load page-248.ktv 
'''