# 2022.4.10  realtime essay class  | docker run -p 6379:6379 redislabs/redisearch:latest |
import json,requests,hashlib,os,time,redis
from uvirun import * 
import en

rhost		= os.getenv("rhost", "127.0.0.1")
rport		= int(os.getenv('rport', 6379))
rdb			= int(os.getenv('rdb', 0))
redis.r		= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=True) 
redis.bs	= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=False) 
redis.ttl	= int (os.getenv("ttl", 7200) )
redis.timeout= int (os.getenv("timeout", 3) )
redis.dskhost= os.getenv("dskhost", "172.17.0.1:7095")
now			= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
md5text		= lambda text: hashlib.md5(text.strip().encode("utf-8")).hexdigest()
getdocs		= lambda snts:  [ ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt))[1] for snt in snts ]

@app.get('/realtime/init')
def realtime_init():
	''' snt=0:rid=100876:uid=1001  '''
	redis.r.execute_command("FT.CREATE ftsnt ON HASH PREFIX 1 snt: SCHEMA snt TEXT lems TAG trps TAG kps TAG cates TAG feedbacks TAG rid TAG uid TAG tags TAG")
	redis.r.execute_command("FT.CREATE ftessay ON HASH PREFIX 1 essay: SCHEMA rid TAG uid TAG tags TAG") # essay:{xid}

def index(rid, uid, snts, docs):
	''' snt:rid-100876:uid-1001={snt} '''
	for idx, snt, doc in enumerate( zip(snts, docs)): 
		lems = [ f"{t.pos_}_{t.lemma_}" for t in doc]
		trps = [ f"{t.dep_}_{t.head.pos_}_{t.pos_}:{t.head.lemma_} {t.lemma_}" for t in doc if t.pos_ not in ('PUNCT')]
		# index mkf 
		redis.r.hset(f"snt={idx}:rid={rid}:uid={uid}", "rid", rid, {"uid": uid, "snt": snt, "lems": ','.join(lems), "trps": ','.join(trps)} )

@app.post('/realtime/xadd')
def realtime_xadd(arr:dict={"rid":100876, "uid":1001, "tid":0, "type":"essay", "essay":"She has ready. It are ok."}, xname:str="xessay"):   #, "snts":"[\"She has ready.\", \"It are ok.\"]"
	''' xadd   {label = text, rid, uid,  tm , snts(json.dumps), tid, type='essay' }   -- xid  ''' 
	rid = arr.get('rid', '0')
	uid = arr.get('uid', '0')
	
	#rid=100876:uid_xid  hash    {uid: xid}    xid = 1649487647926-3,  a tm value , last updated, xid -> snts   |  NOT add duplicated items 
	latest = redis.r.hget(f"rid={rid}:uid_essaymd5", uid)
	essay = arr.get('essay','')
	essaymd5 = md5text(essay) 
	if latest is None  or  lastest != essaymd5: # changed a bit  #essay !=  redis.r.xrange(f"xrid-{rid}", min=latest_xid, max=latest_xid, count=1).get('label',''):
		xid = redis.r.xadd(xname, arr ) #f"xrid-{rid}"
		redis.r.hset(f"rid={rid}:uid_essaymd5", uid, essaymd5)

		snts = spacy.snts(essay)
		reids.r.hset(f"essay:{xid}", "snts", json.dumps(snts), arr ) # hash mirror of xrid-{rid}, ftessay
		redis.r.zadd(f"rid={rid}:zlogs", {f"{uid},{len(snts)}": float(xid.split('-')[0])}) #rid=100876:logs	 zadd    {f"{uid}-{action}": tm }
		[ redis.r.xadd('xsnt', {'snt':snt, 'uid':uid,'rid':rid}) for snt in snts ]
		docs = getdocs(snts) 

		# search old snts, and delete,  use ft.search , rid=, uid= 
		index(rid, uid, arr['snts'], docs) 

@app.get('/realtime/log')
def realtime_log(rid:str="100876", topk:int=20):
	''' snt=0:rid=100876:uid=1001  '''
	return redis.r.zrevrange(f"rid={rid}:zlogs",0, topk, True)
	#arr = redis.r.xinfo_stream(f"xrid-{rid}")
	#lastid = arr['last-generated-id']
	# got last 10 items , and output 

kvdic = lambda tup=['term', 'three', 'freq', '1']: dict(zip(tup[::2], tup[1::2])) # {'term': 'three', 'freq': '1'}

@app.get('/realtime/wordlist')
def realtime_wordlist(rid:str="100876", pos:str='LEM', topk:int=10):
	''' FT.SEARCH ftsnt '@rid:{100876}'  | snt=0:rid=100876:uid=1001  '''
	#arr = r.execute_command("FT.SEARCH ftsnt '@rid:{" + rid + "}'") #[2, 'snt=0', ['rid', '100876', 'snt', 'hello'], 'snt=1', ['rid', '100876', 'snt', 'good']]
	# FT.AGGREGATE ftsnt '@rid:{100876}' LOAD 1 @lems  APPLY split(@lems) as term GROUPBY 1 @term REDUCE COUNT 0 AS freq
	arr = r.execute_command("FT.AGGREGATE ftsnt '@rid:{"+rid+"}' LOAD 1 @lems  APPLY split(@lems) as term GROUPBY 1 @term REDUCE COUNT 0 AS freq")
	return (arr[0],  [ kvdic(ar) for ar in arr[1:][0:topk] ] )

def uvirun(port) : 
	''' python -m uvirun.realtime 16379 '''
	uvicorn.run(app, host='0.0.0.0', port=port)

if __name__ == '__main__':
	import fire
	fire.Fire(uvirun)

'''
>>> r.execute_command("FT.AGGREGATE ftsnt '@rid:{100876}' LOAD 1 @lems  APPLY split(@lems) as term GROUPBY 1 @term REDUCE COUNT 0 AS freq")
[4, ['term', 'two', 'freq', '2'], ['term', 'one', 'freq', '2'], ['term', 'three', 'freq', '1'], ['term', 'four', 'freq', '1']]

>>> r.xinfo_stream('xessay')
{'length': 356, 'radix-tree-keys': 203, 'radix-tree-nodes': 401, 'last-generated-id': '1649556821869-1', 'groups': 0, 'first-entry': ('1649556821752-0',

>>> r.execute_command("FT.SEARCH ftsnt '@rid:{100876}'")
[1, 'snt=0', ['rid', '100876', 'snt', 'hello']]

>>> r.execute_command("FT.SEARCH ftsnt '@rid:{100876}'")
[2, 'snt=0', ['rid', '100876', 'snt', 'hello'], 'snt=1', ['rid', '100876', 'snt', 'good']]

redis.r.xrange(f"xrid-{rid}", min=latest_xid, max=latest_xid, count=1).get('label',''):

127.0.0.1:6379> FT.SEARCH ftsnt '@rid:{100876}'
1) (integer) 1
2) "snt=0"
3) 1) "rid"
   2) "100876"
   3) "snt"
   4) "hello"

>>> l = range(10)
>>> l[::2]         # even  - start at the beginning at take every second item
[0, 2, 4, 6, 8]
>>> l[1::2]        # odd - start at second item and take every second item
[1, 3, 5, 7, 9]

FT.AGGREGATE ftsnt '@rid:{230537}' LOAD 1 @lems  APPLY split(@lems) as term GROUPBY 1 @term REDUCE COUNT 0 AS freq
FT.AGGREGATE ftsnt '@rid:{230537}' LOAD 1 @trps  APPLY split(@trps) as term GROUPBY 1 @term REDUCE COUNT 0 AS freq

FT.AGGREGATE ftsnt '@rid:{230537}' LOAD 1 @trps  APPLY split(@trps) as term GROUPBY 1 @term REDUCE COUNT 0 AS freq
startswith(@field, "company")  Return 1 if s2 is the prefix of s1, 0 otherwise.

FT.AGGREGATE ftsnt '@rid:{230537}' LOAD 1 @cates  APPLY split(@cates) as term GROUPBY 1 @term REDUCE COUNT 0 AS freq

https://redis.io/commands/ft.aggregate/
https://redis.io/docs/stack/search/reference/aggregations/

FT.search ftsnt '@trps:{dobj_VERB_NOUN\:open door}'
FT.SEARCH idx "@tags:{ hell* }"
FT.SEARCH idx "@tags:{ hello\\ w* }"
FT.SEARCH ftsnt "@trps:{dobj_VERB_NOUN\:open *}"

FT.AGGREGATE ftsnt '@rid:{230537}' LOAD 1 @lems  APPLY startswith(@lems, "VERB_") as ispos GROUPBY 1 @ispos REDUCE COUNT 0 AS freq

FT.CREATE idx SCHEMA name TEXT SORTABLE docid TAG SORTABLE NOINDEX
FT.AGGREGATE idx * GROUPBY 1 @name REDUCE TOLIST 1 @docid as docids
FT.AGGREGATE ftessay * GROUPBY 1 @uid REDUCE TOLIST 1 @rid as docids

FT.AGGREGATE idx * LOAD 1 @__key GROUPBY 1 @type REDUCE TOLIST 1 @__key as keys
FT.AGGREGATE ftessay * LOAD 1 @__key GROUPBY 1 @uid REDUCE TOLIST 1 @__key as keys

FT.AGGREGATE ftsnt * LOAD 1 @__key APPLY split(@lems) as term GROUPBY 1 @term REDUCE TOLIST 1 @__key as keys

FILTER "@name=='foo' && @age < 20"

FT.AGGREGATE ftsnt '@rid:{230537}' LOAD 1 @lems  APPLY split(@lems) as term GROUPBY 1 @term REDUCE COUNT 0 AS freq FILTER "@freq >  2"

FT.AGGREGATE ftsnt '@rid:{230537}' LOAD 1 @lems APPLY split(@lems) as term, startswith(@term, "VERB_") as ispos GROUPBY 2 @term @ispos REDUCE COUNT 0 AS freq

REDUCE FIRST_VALUE {nargs} {property} [BY {property} [ASC|DESC]]

FT.AGGREGATE idx "*" LOAD 1 @location FILTER "exists(@location)" APPLY "geodistance(@location,-117.824722,33.68590)" AS dist SORTBY 2 @dist DESC

https://pypi.org/project/redisearch/

RediSearch 2.4 introduces a new capability, Vector Similarity Search (VSS), which allows indexing and querying vector data stored (as BLOBs) in Redis hashes.
https://github.com/RediSearch/RediSearch/releases?after=v1.99.5

'''