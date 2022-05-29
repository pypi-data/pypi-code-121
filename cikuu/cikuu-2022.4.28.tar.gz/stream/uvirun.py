# 2022.4.26  nohup uvicorn uvirun:app --host 0.0.0.0 --port 16379 --reload & 
import json,requests,hashlib,os,time,redis,fastapi, uvicorn ,en, random
from collections import Counter
from datetime import datetime
import asyncio
from fastapi import FastAPI,BackgroundTasks #https://fastapi.tiangolo.com/tutorial/background-tasks/
from fastapi.responses import HTMLResponse, StreamingResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request #request.query_params['rid']
from fastapi.templating import Jinja2Templates
from typing import Iterator

app	 = fastapi.FastAPI() 
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/front", StaticFiles(directory="front"), name="front")
templates = Jinja2Templates(directory="front")
#@app.get("/", response_class=HTMLResponse)
#async def index(request: Request) -> templates.TemplateResponse:
#	return templates.TemplateResponse("index.html", {"request": request})

rhost		= os.getenv("rhost", "172.17.0.1")
rport		= int(os.getenv('rport', 6379))
rdb			= int(os.getenv('rdb', 0))
redis.r		= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=True) 
redis.bs	= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=False) 
redis.ttl	= int (os.getenv("ttl", 17200) )
redis.timeout= int (os.getenv("timeout", 3) )
#redis.dskhost= os.getenv("dskhost", "172.17.0.1:7095")
now			= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
getdocs		= lambda snts:  [ ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt))[1] for snt in snts ]
zsum		= lambda key='rid-230537:essay_wordnum',ibeg=0, iend=-1: sum([v for k,v in redis.r.zrevrange(key, ibeg, iend, True)])

mapf = { 
"eo.dic"	: lambda arr: dict(zip(arr[::2], arr[1::2])), # even : odd 
"eo.pair"	: lambda arr: list(zip(arr[::2], arr[1::2])), # keep the order
"rg.kv"		: lambda res: {ar['key']:ar['value'] for ar in [ eval(line) for line in res[0] ] if ar['key'] } , #"{'key': '2', 'value': 32}"
"rg.kvarr"	: lambda res: [ (ar['key'],ar['value']) for ar in [ eval(line) for line in res[0] ] if ar['key'] ] ,
"rg.eval"	: lambda res: [ eval(line) for line in res[0] ] , #JSONEachRow [{"key": "642887", "value": 1},{}]
"rg.eodic"	: lambda res: [ ( ar := eval(line), dict(zip(ar[::2], ar[1::2])))[-1] for line in res[0] ] , # added 2022.5.5 GB().map(lambda x:execute('hgetall', x['key'])).run('rid-2642549:config:tid-*')
"rg.kvdic"	: lambda res: [ ( ar := eval(line), {ar[0] : dict(zip(ar[1][::2], ar[1][1::2])) })[-1] for line in res[0] ] , #GB().map(lambda x:(x['key'].split(':')[-1], execute('hgetall', x['key']))).run('rid-2642549:config:tid-*')
"rg.si"		: lambda res: Counter({ar['key']:ar['value'] for ar in [ eval(line) for line in res[0] ] if ar['key'] }).most_common() ,
"rg.si20"	: lambda res: Counter({ar['key']:ar['value'] for ar in [ eval(line) for line in res[0] ] if ar['key'] }).most_common(20) ,
"rg.float"	: lambda res: float(res[0][0]) , 
"rg.0"		: lambda res: res[0] , 
}

@app.get('/redis/rg_pyexecute')
def rg_pyexecute(cmd:str="GB().flatmap(lambda x: execute('hvals', x['key']) ).countby().run('rid-230537:tid-1:uid-*')", name:str = 'rg.eval'):
	''' name: eo.dic,eo.pair,rg.kv, rg.float
	# GB().map(lambda x: x['value']).flatmap(lambda x: x.split()).countby().run('sent:*')
	# GB().count().run('rid-230537:tid-3:uid-*')
	# GB().flatmap(lambda x: execute('hvals', x['key']) ).countby().run('rid-230537:tid-3:uid-*')
	# GB().filter(lambda x: x['value'].get('latest','0') == '1' ).count().run('essay:rid-230537:*')
	'''
	return mapf.get(name, lambda x: x)(redis.r.execute_command(*["RG.PYEXECUTE",cmd if cmd.startswith("GB().") else f"GB().{cmd}"]))

@app.get('/redis/rgexec') 
async def rg_pyexec(request: Request)-> StreamingResponse:
	''' sse version rg_pyexecute, added 2022.4.28 '''
	async def getdata(request: Request) -> Iterator[str]:
		cmd = request.query_params.get('cmd',"GB().flatmap(lambda x: execute('hvals', x['key']) ).count().run('rid-230537:tid-1:uid-*')")
		name = request.query_params.get('name','rg.float')
		span = int(request.query_params.get('span','2'))
		while True:
			if not await request.is_disconnected()==True:
				json_data = json.dumps( mapf.get(name, lambda x: x)(redis.r.execute_command(*["RG.PYEXECUTE",cmd if cmd.startswith("GB().") else f"GB().{cmd}"])) )
				yield f"data:{json_data}\n\n"
			await asyncio.sleep(span)
	return StreamingResponse(getdata(request), media_type="text/event-stream", headers={"Cache-Control": "no-cache","X-Accel-Buffering": "no"})

@app.post('/redis/mexec')
def command_execute_mul(cmds:dict={"test1":["get","hello"], 
	"snt-search": "FT.SEARCH ftsnt '@cola:[0.5,0.9]' limit 0 2".split(),  #FT.SEARCH ftsnt "@rid:{230537} @borntm:[0,2649759864]" limit 0 2 return 1 trps 
	"hget-uid": ["hgetall","rid-230537:tid-1:uid-595800"], 
	"eo.pair:essay_score": ["zrevrange","rid-230537:essay_score", "0", "10", "withscores"], 
	"rg.0:essay_latest": ["RG.PYEXECUTE","GB().filter(lambda x: x['value'].get('latest','0') == '1' ).count().run('essay:rid-230537:*')"], 
	"rg.0:essay_score": ["RG.PYEXECUTE","GB().filter(lambda x: x['value'].get('latest','0') == '1' ).map(lambda x: (x['value']['uid'], x['value']['score']) ).run('essay:rid-230537:*')"],
	"rg.kv:word-cnt":["RG.PYEXECUTE", "GB().map(lambda x: x['value']).flatmap(lambda x: x.split()).countby().run('sent:*')"],
	"rg.kv:zsum":["RG.PYEXECUTE", "GB().map(lambda x: sum([ float(score) for score in execute('zrange', x['key'], '0', '-1','withscores')[1::2] ]) ).run('rid-230537:essay_score')"],
	"rg.kv:catetop":["RG.PYEXECUTE", "GB().flatmap(lambda x: execute('hget', x['key'],'cates').split(',') ).map(lambda x:x.split('.')[0]).countby().run('snt:rid-230537:uid-*')"],
	"rg.kv:cate.snt-countby":["RG.PYEXECUTE", "GB().flatmap(lambda x: execute('hget', x['key'],'cates').split(',') ).filter(lambda x: x.startswith('snt.')).countby().run('snt:rid-230537:uid-*')"],
	"rg.kv:gongping-score":["RG.PYEXECUTE", "GB().map(lambda x: execute('hget', x['key'],'score') ).countby().run('rid-230537:tid-1:uid-*')"],
	"rg.kv:score-range":["RG.PYEXECUTE", "GB().map(lambda x: int(float(execute('hget', x['key'],'score'))/10) ).countby().run('rid-230537:tid-1:uid-*')"],
	"rg.kv:word-chosen":["RG.PYEXECUTE","GB().flatmap(lambda x: execute('hkeys', x['key']) ).countby().run('rid-230537:tid-2:uid-*')"], 
	"rg.kv:sent-rewritten":["RG.PYEXECUTE","GB().flatmap(lambda x: execute('hvals', x['key']) ).countby().run('rid-230537:tid-3:uid-*')"], 
	"rg.kv:sent-rewritten-one":["RG.PYEXECUTE","GB().map(lambda x: execute('hget', x['key'],'snt-1') ).countby().run('rid-230537:tid-3:uid-*')"], 
	"rg.float:zavg":["RG.PYEXECUTE", "GB().flatmap(lambda x: execute('zrange', x['key'], '0', '-1','withscores')[1::2] ).avg().run('rid-230537:essay_score')"],
	"rg.float:cola-avg":["RG.PYEXECUTE", "GB().map(lambda x: float(execute('hget', x['key'],'cola')) ).avg().run('snt:rid-230537:uid-*')"],
	"rg.float:sum-cate":["RG.PYEXECUTE", "GB().flatmap(lambda x:x['value']['cates'].split(',')).countby().accumulate(lambda a, r: (a if a else 0) + float(r['value']) if r['key'] else 0).run('snt:rid-230537:uid-*')"],
	}):
	''' execute sql-like-scripts over redis '''
	res = {} # "GB().filter(lambda x: x['value'].get('latest','0') == '1' ).count().run('essay:rid-230537:*')"
	for name, args in cmds.items():
		try:
			args = args if isinstance(args, list) else args.split()
			res[name] = mapf.get(name.split(":")[0], lambda x: x)(redis.r.execute_command(*args))
		except Exception as e:
			res[name] = str(e)
	return res 

@app.get('/redis/hgetall')
def redis_hgetall(key:str='rid-230537:tid-1', JSONEachRow:bool=False): 
	return redis.r.hgetall(key) if not JSONEachRow else [{"key":k, "value":v} for k,v in redis.r.hgetall(key).items()]

@app.get('/redis/hgetalls')
def redis_hgetalls(pattern:str='rid-*', hkeys:str="rid,tid,uid,label,borntm"):
	''' rid-230537:tid-1:uid-*  added 2022.5.17 '''
	rows = []
	hkeys = hkeys.strip().split(',') if hkeys else None 
	for key in redis.r.keys(pattern): 
		if redis.r.type(key) == 'hash': 
			arr = redis.r.hgetall(key)
			row = {k: arr.get(k,'')  for k in hkeys} if hkeys else arr 
			rows.append(row) 
	return rows # for JSONEachRow 

@app.get('/redis/keys_hgetall')
def redis_hgetalls_map(pattern:str='rid-230537:tid-0:uid-*'):
	''' added 2022.5.14 '''
	return [] if pattern.startswith("*") else [{"key": key, "value":redis.r.hgetall(key)} for key in redis.r.keys(pattern)]

@app.get('/redis/keys')
def redis_keys(pattern:str='rid-230537:tid-0:uid-*'):
	''' added 2022.5.14 '''
	return [] if pattern.startswith("*") else [{"key": key} for key in redis.r.keys(pattern)] 

@app.get('/redis/keys_hget')
def redis_keys_hget(pattern:str='rid-230537:tid-0:uid-*', hkey:str='rid', jsonloads:bool=False):
	''' added 2022.5.15 '''
	if pattern.startswith("*"): return []
	return [{"key": key, "value": ( res:=redis.r.hget(key, hkey), json.loads(res) if res and jsonloads else res)[-1] } for key in redis.r.keys(pattern)]

@app.get('/redis/hget')
def redis_hget(key:str='config:rid-10086:tid-1', hkey:str='rid', jsonloads:bool=False):
	''' added 2022.5.18 '''
	res = redis.r.hget(key, hkey)
	return json.loads(res) if res and jsonloads else res  

@app.post('/redis/execute_command')
def redis_execute_command(cmd:list='zrevrange rid-230537:snt_cola 0 10 withscores'.split(), func: str = None):
	''' func: eo.dic,eo.pair'''
	return mapf.get(func, lambda x: x)(redis.r.execute_command(*cmd))

@app.get("/ridsse")
async def ridsse_all(request: Request) -> StreamingResponse:
	''' return all the data of rid in a single json, 2022.4.21 '''
	async def getall(request: Request) -> Iterator[str]:
		rid = int(request.query_params.get('rid','230537'))
		span = int(request.query_params.get('sleep','3'))
		topk = int(request.query_params.get('topk','30'))
		while True:
			if await request.is_disconnected():	break 	
			scores  = [ round(score,1) for uid, score in redis.r.zrevrange(f"rid-{rid}:essay_score", 0, -1, True) ]
			json_data = json.dumps(
				{
					"time": datetime.now().strftime("%m-%d %H:%M:%S"), #%Y-%m-%d 
					"errorsum": zsum(f"rid-{rid}:cate"), 
					"wordsum":  zsum(f"rid-{rid}:essay_wordnum"), 
					"essaysum": redis.r.zcard(f"rid-{rid}:essay_score"), 
					"sntsum": redis.r.zcard(f"rid-{rid}:snt_cola"),
					"score-avg": round(sum(scores) / (len(scores) + 0.01),1),
					"score-max": scores[0] if len(scores) > 0 else 0 ,
					"score-min": scores[-1] if len(scores) > 0 else 0 ,
					"essay-score": redis.r.zrevrange(f"rid-{rid}:essay_score", 0, -1, True), 
					"catetop": redis.r.zrevrange(f"rid-{rid}:catetop", 0, -1, True), 
					"wordidf": redis.r.zrevrange(f"rid-{rid}:word_idf", 0, topk, True), 
					"zlogs": redis.r.zrevrange(f"rid-{rid}:zlogs", 0, topk, True), 
					"uidname": redis.r.hgetall(f"rid-{rid}:uidname"), 
				}
			)
			yield f"data:{json_data}\n\n"
			await asyncio.sleep(span)
	return StreamingResponse(getall(request), media_type="text/event-stream", headers={"Cache-Control": "no-cache","X-Accel-Buffering": "no"})

@app.get("/ridtid_scoring")
async def ridtid_scoring(request: Request) -> StreamingResponse:
	''' return result of tid=1, 2022.4.21 '''
	async def getall(request: Request) -> Iterator[str]:
		rid = int(request.query_params.get('rid','230537'))
		tid = int(request.query_params.get('tid','1'))
		span = int(request.query_params.get('sleep','3'))
		while True:
			if not await request.is_disconnected()==True:
				uid_label  = redis.r.hgetall(f"rid-{rid}:tid-{tid}:uid_label") 
				avg_score  = round( sum([ float(score) for uid, score in uid_label.items()]) / (len(uid_label)+ 0.01), 1) 
				json_data = json.dumps(
					{
						"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), #%Y-%m-%d 
						"uid_label": uid_label,
						"avg_score": avg_score, 
						"score_range": [ (f"{s}0+", i) for s,i in Counter([int( float(score)/10 ) for uid, score in uid_label.items()]).items()], 
						"score_sd": [ (uid,  abs(1 - (abs( float(score) - avg_score) / avg_score)) )  for uid, score in uid_label.items()], 
						"uidname": redis.r.hgetall(f"rid-{rid}:uidname"), 
					}
				)
				yield f"data:{json_data}\n\n"
			await asyncio.sleep(span)
	return StreamingResponse(getall(request), media_type="text/event-stream", headers={"Cache-Control": "no-cache","X-Accel-Buffering": "no"})

@app.post('/redis/execute_commands')
def redis_execute_commands(cmds:list=["FT.CREATE ftsnt ON HASH PREFIX 1 snt: SCHEMA snt TEXT lems TAG trps TAG kps TAG cates TAG score NUMERIC cola NUMERIC rid TAG uid TAG latest TAG tags TAG borntm NUMERIC SORTABLE","FT.CREATE ftessay ON HASH PREFIX 1 essay: SCHEMA rid TAG uid TAG tags TAG latest TAG score NUMERIC borntm NUMERIC SORTABLE","FT.CREATE ftitem ON HASH PREFIX 1 item: SCHEMA rid TAG uid TAG tags TAG latest TAG score NUMERIC tid NUMERIC borntm NUMERIC SORTABLE label TAG type TAG"]):
	''' execute simple batch cmds '''
	return [redis.r.execute_command(cmd) for cmd in cmds]

@app.post('/redis/xinfo')
def redis_xinfo(keys:list=["rid-230537:xwordidf","xessay"], name:str="last-entry"):	return { key: redis.r.xinfo_stream(key)[name]  for key in keys }
@app.get('/redis/delkeys')
def redis_delkeys(patterns:list=["rid-230537:*","essay:rid-230537:*"]): return [redis.r.delete(k) for pattern in patterns for k in redis.r.keys(pattern)]
@app.get('/')
def home(): return fastapi.responses.HTMLResponse(content=f"<h2>realtime essay api</h2><a href='/docs'> docs </a> | <a href='/redoc'> redoc </a><br>uvicorn uvirun:app --port 80 --host 0.0.0.0 --reload <br><br>last update:2022.4.22")
@app.post('/redis/xadd')
def redis_xadd(name:str="xitem", arr:dict={"rid":"230537", "uid":"1001", "tid":0, "type":"fill", "label":"open the door"}): return redis.r.xadd(name, arr )
@app.get('/redis/xrange')
def redis_xrange(name:str='xitem', min:str='-', max:str="+", count:int=1): return redis.r.xrange(name, min=min, max=max, count=count)
@app.get('/redis/xrevrange')
def redis_xrevrange(name:str='xlog', min:str='-', max:str="+", count:int=1): return redis.r.xrevrange(name, min=min, max=max, count=count)
@app.get('/redis/zrevrange')
def redis_zrevrange(name:str='rid-230537:log:tid-4', start:int=0, end:int=-1, withscores:bool=True, JSONEachRow:bool=False): return redis.r.zrevrange(name, start, end, withscores) if not JSONEachRow else [{"member":member, "score":score} for member, score in redis.r.zrevrange(name, start, end, withscores)]
@app.get('/redis/zrange')
def redis_zrange(name:str='rid-230537:log:tid-4', start:int=0, end:int=-1, withscores:bool=True, JSONEachRow:bool=False): return redis.r.zrange(name, start, end, withscores=withscores) if not JSONEachRow else [{"member":member, "score":score} for member, score in redis.r.zrange(name, start, end, withscores=withscores)]
@app.get('/redis/set')
def redis_set(key:str='rid-230537:config',value:str=""): return redis.r.set(key, value) 
@app.post('/redis/hset')
def redis_hset(arr:dict={}, key:str='rid-10086:tid-1:uid-pen-zz', k:str="label", v:str="v", tm:str=None):
	''' tm=tm to enable time versioning, 2022.5.16 '''
	now = time.time()
	if tm: arr.update({f"{k}:{tm}":now, f"{k}-{now}": v})
	return redis.r.hset(key, k, v, arr) 
	
def _mock_xadd(arr:dict={"rid":10086, "tids":[1,2,3], "uids":["AA","BB","ZZ","HH","JJ","MM","NN"], "key":"label", "labels":["A","B","C","D"],"loop":10, "name":"xrid:test", "sleep":1, "reset":1}): 
	rid,tids,uids,labels = arr.get('rid', 0), arr.get('tids',[]),arr.get('uids',[]),arr.get("labels", [])
	ntid, nuid, nlabel = len( tids), len( uids ) , len(labels) 
	if "reset" in arr: [ redis.r.delete(k) for k in redis.r.keys(f"rid-{rid}:tid-*")] # keep config
	name = arr.get('name', 'xrid:test')
	sleep = "sleep" in arr
	for i in range(int(arr.get('loop',0))):
		tid = tids[random.randint(0, ntid - 1)] 
		uid = uids[random.randint(0, nuid - 1)] 
		label = labels[random.randint(0, nlabel -1 )] 
		redis.r.xadd(name, {"rid":rid, "tid":tid, 'uid':uid, arr.get('key','label'): label})
		if sleep : time.sleep( random.random()) 

@app.post("/redis/mock_xadd")
async def redis_mock_xadd(background_tasks: BackgroundTasks, arr:dict={"rid":10086, "tids":[1,2,3,4,5,6,7,8,9,10], "uids":["AA","BB","CC","DD","EE","ZZ","HH","JJ","MM","NN"], "key":"label", "labels":["A","B","C","D"],"loop":20, "name":"xrid:test", "sleep":1, "reset":1} ):
	''' {"rid":10086, "tids":[1,2,3,4,5,6,7,8,9,10], "uids":["AA","BB","CC","DD","EE","ZZ","HH","JJ","MM","NN"], "key":"label", "labels":["A","B","C","D"],"loop":20, "name":"xrid:test", "sleep":1, "reset":1} '''
	background_tasks.add_task(_mock_xadd, arr)
	return arr

@app.post('/redis/hdel')
def redis_hdel(keys:list=[], name:str='one'): return redis.r.hdel(name, *keys) 
@app.get('/redis/hdel')
def redis_hdel_get(key:str='one', hkey:str='k,k1' , sep:str=','): return [redis.r.hdel(key, k) for k in hkey.split(sep)]
@app.post('/redis/zadd')
def redis_zadd(arr:dict={}, key:str='rid-230537:config'): return redis.r.zadd(key, arr) 
@app.get('/redis/xlen')
def redis_xlen(key:str='xsnt',ts:bool=False): return redis.r.xlen(key) if not ts else {"time":time.time(), "Value":redis.r.xlen(key)}

@app.get('/redis/tsvalue')
def redis_tsvalue(): 
	''' testing only, as the data source for grafana, 2022.5.9  '''
	import random 
	return [ { 'time': time.time(), "value": int(random.random() * 100)}]

@app.get("/redis/JSONEachRow")
def redis_JSONEachRow():
	''' https://segmentfault.com/a/1190000024497520 '''
	return [{
 "lat": 31.578766930461885,
 "lng": 116.95648590903424,
 "precphour": 0.0,
 "precphour12": 0.0,
 "precphour24": 0.0,
 "precphour3": 0.0
 },
 {
 "lat": 31.578766930461885,
 "lng": 116.96558407702439,
 "precphour": 0.0,
 "precphour12": 0.0,
 "precphour24": 0.0,
 "precphour3": 0.0
 }]

@app.post('/redis/xaddnew')
def redis_xadd_new(name:str="xessay", arr:dict={"rid":100876, "uid":1001, "tid":0, "type":"essay", "essay":"She has ready. It are ok."}):  
	''' '''
	inputmd5 = hashlib.md5(json.dumps(arr).encode("utf-8")).hexdigest() 
	if not redis.r.hexists(f"{name}:md5", inputmd5): 
		xid = redis.r.xadd(name, arr )
		redis.r.hset(f"{name}:md5", inputmd5, xid) 

@app.get('/redis/ft_search')
def ft_search(index:str='ftsnt', query:str="gladsome @rid:{230537}", args:str="limit 0 2 return 3 snt uid borntm"):
	''' FT.SEARCH ftsnt 'gladsome @rid:{230537}' limit 0 2 return 3 snt uid borntm  '''
	cmd = ["FT.SEARCH", index, query]
	cmd.extend( args.strip().split())
	return redis.r.execute_command(*cmd) 

@app.get('/redis/word_idf')
def word_idf():
	from dic import word_idf
	return word_idf.word_idf

@app.get('/redis/mapf_keys')
def mapf_keys(): return [name for name in mapf.keys()] 

@app.post('/requests/post_dict')
def requests_wrapper(arr:dict={"rid":1001, "uid":102,"tid":0, "essay_or_snts":"She has ready. It are ok."}, url:str="http://gpu120.wrask.com:8180/redis/todsk"): 
	''' added 2022.5.5 '''
	return requests.post(url, json=arr).json()

@app.get('/spacy/docdiff')
def spacy_docdiff(src:str="I like you.", tgt:str="I love you."): 
	''' 2022.4.28 ''' 
	import difflib
	src = [t.text for t in spacy.redisdoc(src,redis.bs, 'bs:')]
	tgt = [t.text for t in spacy.redisdoc(tgt,redis.bs, 'bs:')] #spacy.getdoc(tgt)
	return src if src == tgt else [s for s in difflib.ndiff(src, tgt) if not s.startswith('?')] #src:list, trg:list

def uvirun(port) : uvicorn.run(app, host='0.0.0.0', port=port) # python -m uvirun 16379
if __name__ == '__main__':
	import fire
	fire.Fire(uvirun)

'''
@app.post("/redis/mock_xadd")
async def redis_mock_xadd(arr:dict={"rid":10086, "tids":[1,2,3], "uids":["AA","BB","ZZ","HH","JJ","MM","NN"], "key":"label", "labels":["A","B","C","D"],"loop":10}, name: str="xrid:test", loop:int=10, sleep:bool=True): #, background_tasks: BackgroundTasks):
	rid,tids,uids,labels = arr.get('rid', 0), arr.get('tids',[]),arr.get('uids',[]),arr.get("labels", [])
	ntid, nuid, nlabel = len( tids), len( uids ) , len(labels) 
	for i in range(int(arr.get('loop',0))):
		tid = tids[random.randint(0, ntid - 1)] 
		uid = uids[random.randint(0, nuid - 1)] 
		label = labels[random.randint(0, nlabel -1 )] 
		redis.r.xadd(name, {"rid":rid, "tid":tid, 'uid':uid, arr.get('key','label'): label})
	return arr 

@app.post('/redis/mock_hset')
def redis_mock_hset(arr:dict={"rid":10086, "tids":[1,2,3], "uids":["AA","BB","ZZ","HH","JJ","MM","NN"], "key":"label", "labels":["A","B","C","D"],"loop":10} ):
	rid,tids,uids,labels = arr.get('rid', 0), arr.get('tids',[]),arr.get('uids',[]),arr.get("labels", [])
	ntid, nuid, nlabel = len( tids), len( uids ) , len(labels) 
	for i in range(int(arr.get('loop',0))):
		tid = tids[random.randint(0, ntid - 1)] 
		uid = uids[random.randint(0, nuid - 1)] 
		label = labels[random.randint(0, nlabel -1 )] 
		redis_hset({"rid":rid, "tid":tid}, f"rid-{rid}:tid-{tid}:uid-{uid}", arr.get('key','label'), label, tm="tm")
	return arr 

HSET "config:rid-10086:tid-1" "rid" "10086"
HSET "config:rid-10086:tid-2" "rid" "10086"
HSET "config:rid-10086:tid-3" "rid" "10086"
HSET "config:rid-10086:tid-4" "rid" "10086"
HSET "config:rid-10086:tid-5" "rid" "10086"
HSET "config:rid-10086:tid-6" "rid" "10086"
HSET "config:rid-10086:tid-7" "rid" "10086"
HSET "config:rid-10086:tid-8" "rid" "10086"
HSET "config:rid-10086:tid-9" "rid" "10086"

HSET "config:rid-10086:tid-1" "tid" "1"
HSET "config:rid-10086:tid-2" "tid" "2"
HSET "config:rid-10086:tid-3" "tid" "3"
HSET "config:rid-10086:tid-4" "tid" "4"
HSET "config:rid-10086:tid-5" "tid" "5"
HSET "config:rid-10086:tid-6" "tid" "6"
HSET "config:rid-10086:tid-7" "tid" "7"
HSET "config:rid-10086:tid-8" "tid" "8"
HSET "config:rid-10086:tid-9" "tid" "9"
HSET "config:rid-10086:tid-1" "key" "B"
HSET "config:rid-10086:tid-1" "score" "1.5"
HSET "config:rid-10086:tid-2" "key" "A"
HSET "config:rid-10086:tid-2" "score" "1.5"
HSET "config:rid-10086:tid-3" "key" "C"
HSET "config:rid-10086:tid-3" "score" "1.5"
HSET "config:rid-10086:tid-4" "key" "D"
HSET "config:rid-10086:tid-4" "score" "1.5"
HSET "config:rid-10086:tid-5" "key" "D"
HSET "config:rid-10086:tid-5" "score" "1.5"
HSET "config:rid-10086:tid-6" "key" "A"
HSET "config:rid-10086:tid-6" "score" "1.5"
HSET "config:rid-10086:tid-7" "key" "C"
HSET "config:rid-10086:tid-7" "score" "1.5"
HSET "config:rid-10086:tid-8" "key" "B"
HSET "config:rid-10086:tid-8" "score" "1.5"
HSET "config:rid-10086:tid-9" "key" "A"
HSET "config:rid-10086:tid-9" "score" "1.5"

http://daka.wrask.com/redis/hgetalls?pattern=rid-%2A&hkeys=rid%2Ctid%2Cuid%2Clabel%2Cborntm

http://daka.wrask.com/redis/hgetalls?pattern=config%3Arid-%2A&hkeys=rid%2Ctid%2Ckey%2Cscore


'''