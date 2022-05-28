# 2022.4.8  stream: xmkf     {'snt': , /'snts': ..}
import json, time, fire,sys, redis, socket, os,traceback, en,requests
now		= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
getdocs = lambda snts:  [ ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt))[1] for snt in snts ]

def getgecs(snts): 
	''' '''
	gecs	= redis.r.mget(snts) 
	newsnts = [snt for snt, gec in zip(snts, gecs) if snt and gec is None ]
	sntdic  = {snt:gec for snt, gec in zip(snts, gecs) if snt and gec is not None }
	if newsnts: 
		redis.r.publish("new_gecs", json.dumps(newsnts))
		id	= redis.r.xadd("xsnts", {'snts':json.dumps(newsnts)})
		res = redis.r.blpop([f"suc:{id}",f"err:{id}"], timeout=len(newsnts) + 2 )
		if res is None : return sntdic 
		sntdic.update(json.loads(res[1]))
	return sntdic 

def snts_mkfs(snts, diffmerge:bool=False, dskhost:str="172.17.0.1:7095") :  
	''' added 2022.4.8 '''
	import mkf 
	docs   = getdocs(snts)
	sntdic = getgecs(snts) 
	inputs = mkf.mkf_inputs(snts, docs, sntdic, diffmerge)
	mkfs   = requests.post(f"http://{dskhost}/parser", data={"q":json.dumps(inputs).encode("utf-8")}).json()
	return mkfs

def process_snt(messages): #[('1648947215933-0', {'snt': 'hello'}), ('1648947215933-1', {'2': '2'}),
	''' to prefill the cache  '''
	try:
		snts	= [arr.get('snt','') for id,arr in messages] #[['xsnt', [('1648947215933-0', {'snt': '1'}), ('1648947215933-1', {'2': '2'}), ('1648947215934-0', {'3': '3'}), ('1648947215934-1', {'4': '4'}), ('1648947215934-2', {'5': '5'}), ('1648947215935-0', {'6': '6'}), ('1648947215935-1', {'7': '7'}), ('1648947215935-2', {'8': '8'}), ('1648947215936-0', {'9': '9'})]]]
		newsnts = [snt for snt in snts if snt and not redis.r.exists(f"mkf:{snt}") ]
		if newsnts: 
			[redis.r.setex(f"mkf:{snt}", redis.ttl, json.dumps(mkf)) for snt, mkf in zip(newsnts, snts_mkfs(newsnts) ) ]
	except Exception as e:
		print(">>[process_snt ex]", e, "\t|", messages)
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)

def process_snts(messages): #[('1648947215933-0', {'snts': '1'}), ('1648947215933-1', {'2': '2'}),
	''' id = xadd('xsnts',  {"snts":["hello"]}),  blpop(id) , 2022.4.3'''
	for id,arr in messages:
		try:
			if 'snts' in arr: 
				snts	= json.loads(arr['snts'])
				mkfs	= snts_mkfs(snts) 
				redis.r.lpush(f"suc:{id}", json.dumps(mkfs) )
				redis.r.expire(f"suc:{id}", redis.ttl) 
		except Exception as e:
			print ("parse err:", e, id, arr) 
			redis.r.lpush(f"err:{id}", json.dumps(arr))
			redis.r.expire(f"err:{id}", redis.ttl) 
			redis.r.setex(f"exception:{id}", redis.ttl, str(e))

def consume(group, stream="xmkf", rhost='127.0.0.1', rport=6379, rdb=0, maxlen=100000, waitms=3600000, ttl=7200, precount=16, debug=False):
	''' python xmkf.py mkf '''
	redis.r		= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=True) 
	redis.bs	= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=False) 
	redis.ttl	= ttl
	try:
		redis.r.xgroup_create(stream, group,  mkstream=True)
	except Exception as e:
		print(e)
	redis.r.xtrim(stream, maxlen)

	consumer_name = f'consumer_{socket.gethostname()}_{os.getpid()}'
	print(f"Redis consumer started: {consumer_name}|{group}| ", redis.r, "\t|", now(), flush=True)
	while True:
		item = redis.r.xreadgroup(group, consumer_name, {stream: '>'}, count=precount, noack=True, block= waitms )
		if not item: break #[['xsnt', [('1648947215933-0', {'snt': '1'}), ('1648947215933-1', {'2': '2'}), ('1648947215934-0', {'3': '3'}), ('1648947215934-1', {'4': '4'}), ('1648947215934-2', {'5': '5'}), ('1648947215935-0', {'6': '6'}), ('1648947215935-1', {'7': '7'}), ('1648947215935-2', {'8': '8'}), ('1648947215936-0', {'9': '9'})]]]
		if debug: print( item, "\t", now(), flush=True) 
		for arr in item:  #['xsnt', [('1648947215933-0', {'snt': '1'}),
			process_snt(arr[1])  # if exists 'snt' 
			process_snts(arr[1]) # if exists 'snts' 

	redis.r.xgroup_delconsumer(stream, group, consumer_name)
	redis.r.close()
	print ("Quitted:", consumer_name, "\t",now())

if __name__ == '__main__':
	fire.Fire(consume)

'''
>>> id = r.xadd('xsnts', {"snts":json.dumps(["She has ready."])})
>>> id
'1648958192091-0'
>>> r.blpop(["suc:1648958192091-0"])
('suc:1648958192091-0', '{"She has ready.": "She is ready."}')
'''