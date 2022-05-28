# 2022.4.1
import json, time, fire,sys, redis, hashlib ,socket, spacy, os
#import util 
#logger = util.getlog("xsnt.log")
now	= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))

if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]

def consume(stream, group, host='127.0.0.1', port=6379, db=0, waitms=3600000, ttl=7200):
	''' python xsnt-spacy.py xsnt spacy --host 192.168.201.120 
	use spacy311 to fill the parsed cache, 2022.4.1 '''
	r = redis.Redis(host=host, port=port, db=db, decode_responses=True) 
	redis.bs = redis.Redis(host=host, port=port, db=db, decode_responses=False) 
	try:
		r.xgroup_create(stream, group,  mkstream=True)
	except Exception as e:
		print(e)

	consumer_name = f'consumer_{socket.gethostname()}_{os.getpid()}'
	print(f"Redis consumer started: {consumer_name}|{stream}|{group}| ", r, flush=True)
	while True:
		item = r.xreadgroup(group, consumer_name, {stream: '>'}, count=1, noack=True, block= waitms )
		try:
			if not item: break
			id,arr = item[0][1][0]  #[['_new_snt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
			#logger.info(f"{id}\t{json.dumps(arr)}\t{now()}")
			try:
				snt = arr.get('snt','') 
				bs  = redis.bs.get(f"bs:{snt}")
				if bs is None: 
					doc = spacy.nlp(snt)
					redis.bs.setex(f"bs:{snt}", ttl, spacy.tobs(doc))
					#logger.info(f"==missed:\t{snt}\t{now()}")
				else:
					r.expire(f"bs:{snt}", ttl) 
					#logger.info(f">>hitted:\t{snt}\t{now()}")
			except Exception as e1:
				print ("parse err:", e1, arr) 
		except Exception as e:
			print(">>[xconsumeEx]", e, "\t|", item, "\t|",  now())

	r.xgroup_delconsumer(stream, group, consumer_name)
	r.close()
	print ("Quitted:", consumer_name, "\t",now())

if __name__ == '__main__':
	fire.Fire(consume)