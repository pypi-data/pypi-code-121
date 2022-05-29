#2022.4.27 
import json,os,time,redis, socket,requests,en, hashlib,traceback,sys,fire,spacy
now	= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))

if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]

def terms(arr, doc): 
	from dic import word_idf 
	rid,uid = arr.get('rid','0'), arr.get('uid','0')
	lems = [ f"{t.pos_}_{t.lemma_}" for t in doc  if t.pos_ not in ('PUNCT','SPACE','PROPN')]
	trps = [ f"{t.dep_}_{t.head.pos_}_{t.pos_}:{t.head.lemma_} {t.lemma_}" for t in doc if t.pos_ not in ('PUNCT')]
	stype = "stype_simple" if len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "stype_complex" 
	if len([t for t in doc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0 : stype = stype + ",stype_compound"

	arr.update({"tc": len(doc), "lems": ','.join(lems), "trps": ','.join(trps), "tags": stype}) #"rid": rid, "uid": uid, "snt": doc.text, 
	[arr.update({"rootv": t.lemma_}) for t in doc if t.dep_ == 'ROOT' and t.pos_.startswith("V")]
	redis.r.hset(f"snt:rid-{rid}:uid-{uid}={arr['snt']}", "rid", rid, arr )

	[redis.r.zadd(f"rid-{rid}:word_idf", { t.text.lower(): word_idf.word_idf.get(t.text.lower(),0) }) for t in doc]
	[redis.r.zadd(f"rid-{rid}:lemma_idf", { f"{t.pos_}_{t.lemma_}" : word_idf.word_idf[t.lemma_] }) for t in doc if t.pos_ not in ('PUNCT','SPACE','PROPN') and t.lemma_ in word_idf.word_idf ]

def process(xid, arr): #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
	''' '''
	try:
		snt = arr.get('snt','') 
		bs  = redis.bs.get(f"bs:{snt}")
		doc = spacy.nlp(snt) if bs is None else spacy.frombs(bs) 
		if bs is None: redis.bs.setex(f"bs:{snt}", redis.ttl, spacy.tobs(doc))

		terms(arr,doc) 
	except Exception as e:
		print ("parse err:", e, arr) 

def consume(name:str, func:str="spacy",  host='172.17.0.1', port=6379, db=0, waitms=3600000, ttl=7200, precount=1,debug=False,  ): 
	''' python xsnt-spacy.py xsnt '''
	redis.r		= redis.Redis(host=host, port=port, db=db, decode_responses=True) 
	redis.bs	= redis.Redis(host=host, port=port, db=db, decode_responses=False) 
	redis.ttl	= ttl 
	redis.debug = debug

	try:
		redis.r.xgroup_create(name, func,  mkstream=True) # func is also the group name
	except Exception as e:
		print(e)

	consumer_name = f'consumer_{socket.gethostname()}_{os.getpid()}'
	print(f"Started: {consumer_name}|{name}|{func}| ", redis.r, now(), flush=True)
	while True:
		item = redis.r.xreadgroup(func, consumer_name, {name: '>'}, count=precount, noack=True, block= waitms )
		if not item: break
		if redis.debug: print("xmessage:\t", item, "\t", now(), flush=True)  #redis.func(item)  #[['_new_snt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
		for stm_arr in item : #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
			for id,arr in stm_arr[1]: 
				try:
					process(id, arr) 
				except Exception as e:
					print(">>[stream]", e, "\t|", id, arr)
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)

	redis.r.xgroup_delconsumer(name, func, consumer_name)
	redis.r.close()
	print ("Quitted:", consumer_name, "\t",now())

if __name__ == '__main__':
	fire.Fire(consume)