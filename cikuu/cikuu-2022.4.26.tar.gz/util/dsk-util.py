# 22-3-11  dsk into one redis-db,  mkf:{snt}, fd:{snt}, bs:{snt},  eidv, rid:{rid}, uid:{uid}
import json, sys, time, redis, fire,traceback, spacy,requests
from elasticsearch import Elasticsearch,helpers

if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.getdoc	= lambda snt: ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setnx(f"bs:{snt}", spacy.tobs(doc)) if not bs else None )[1]

def hver(key, eid, ver ):
	res = redis.r.hget(key, eid)
	try: 
		if not res :
			redis.r.hset(key, eid, ver)
		else: 
			if int(ver) > int(res) : redis.r.hset(key, eid, ver)
	except Exception as e:
		print("ex:", e, eid)

def submit_hdsk(dsk, rid, uid, eid, ver):
	''' added 2022.3.11 '''
	try: 
		info = dsk.get('info',{})
		eidv = f"{eid}-{ver}"
		score = info.get('final_score', 0)

		redis.r.zadd("eids",  { f"{eid}-{ver}":  int(eid) + min(int(ver)/100000, 0.99) })	
		redis.r.zadd(eid,  {ver: int(ver) })	
		hver(f"rid:{rid}", eid, ver ) 
		hver(f"uid:{uid}", eid, ver ) 
		redis.r.zincrby('rids', 1, rid)  #redis.r.sadd("rids",  rid)	
		redis.r.zincrby('uids', 1, uid)  #redis.r.sadd("uids",  uid)	

		redis.r.hset(eidv, 'rid', rid, {'uid':uid, 'score': score, 
		'snts': json.dumps([arrsnt['meta'].get('snt','').strip() for arrsnt in dsk['snt'] ]), 
		"pids": json.dumps([arrsnt['meta'].get('pid',-1) for arrsnt in dsk['snt'] ]),
		"dim":	json.dumps(dsk['doc']), 
		"kw":	json.dumps(dsk['kw']), 
		"info": json.dumps(dsk['info']), 
		})

		for arrsnt in dsk['snt']:
			snt = arrsnt.get('meta',{}).get('snt','')
			redis.r.setnx( f"mkf:{snt}", json.dumps(arrsnt))
			for k, v in arrsnt.get('feedback',{}).items():
				cate = v.get('cate','')
				if cate.startswith ("e_") or cate.startswith("w_"): 
					redis.r.hset(f"fd:{snt}", cate, v.get('kp',''))
	
	except Exception as e:
		print("ex:", e, dsk)
		exc_type, exc_value, exc_obj = sys.exc_info()
		traceback.print_tb(exc_obj)

def get_eid_ver(eid):
	try:
		res = fire.es.get(index=fire.index, id=id) # doc_type=self.index_type,
		return int(res['hits']['hits']['_source'].get('ver',0))
	except Exception as ex:
		return 0

def index_dsk(dsk, index, rid, uid, eid, ver) : 
	try:
		info = dsk.get("info", {})
		snts  = [ ar['meta']['snt'].strip() for ar in dsk['snt']] 
		final_score = float( info.get('final_score',0) ) 
		if ver <= get_eid_ver(eid): return 
		fire.es.delete_by_query(fire.index, conflicts='proceed', body={"query":{"match":{"eid":eid}}})

		actions=[]
		actions.append({'_op_type':'index', '_index':index, '_id': eid, '_source':{'type':'doc', 'eid': eid, 'rid': rid , 'uid': uid, 'ver':ver, 'final_score':final_score}})
		for idx, snt in enumerate(snts) : 
			doc = spacy.getdoc(snt.strip())
			sntlen = len(doc)
			if not sntlen : continue
			actions.append({'_op_type':'index', '_index':index,  '_id': f"{eid}:snt-{idx}",  '_source': {'snt':doc.text, "eid":eid, 'rid': rid , 'uid': uid, 'tc':sntlen, 'awl': sum([ len(t.text) for t in doc])/sntlen ,  'type':'snt',	'postag':' '.join(['^'] + [f"{t.text}_{t.lemma_}_{t.tag_}_{t.pos_}" for t in doc] + ['$']) }})
			[actions.append({'_op_type':'index', '_index':index, '_id': f"{eid}:snt-{idx}:trp-{t.i}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'trp', 'src': f"{eid}:snt-{idx}", 'gov': t.head.lemma_, 'rel': f"{t.dep_}_{t.head.pos_}_{t.pos_}", 'dep': t.lemma_ }}) for t in doc if t.dep_ not in ('punct')]
			[actions.append({'_op_type':'index', '_index':index, '_id': f"{eid}:snt-{idx}:tok-{t.i}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'tok', 'src': f"{eid}:snt-{idx}", 'lex': t.text, 'low': t.text.lower(), 'lem': t.lemma_, 'pos': t.pos_, 'tag': t.tag_, 'i':t.i, 'head': t.head.i }}) for t in doc]
			[actions.append({'_op_type':'index', '_index':index, '_id': f"{eid}:snt-{idx}:np-{np.start}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'np', 'src': f"{eid}:snt-{idx}", 'lem': doc[np.end-1].lemma_, 'chunk': np.text, }}) for np in doc.noun_chunks]
		
			for ar in dsk['snt']:
				for kp, v in ar['feedback'].items():
					actions.append({'_op_type':'index', '_index':index,  '_id': f"{eid}:snt-{idx}:kp-{v['ibeg']}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid, 'type':'feedback',
					'src': f"{eid}:snt-{idx}",  'kp':v['kp'], 'cate': v['cate']} })

		helpers.bulk(client=fire.es,actions=actions, raise_on_error=False)
		if fire.debug: print ("eid:", eid, 'ver:', ver, "rid:", rid, "uid:", uid)
	except Exception as ex:
		print ('index_dsk ex:', ex)

def readline(infile, sepa=None):
	with open(infile, 'r') as fp: #,encoding='utf-8'
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def callback(ch, method, properties, body):
	try:
		ch.basic_ack(delivery_tag = method.delivery_tag)
		line	= body.decode().replace(':null,',':"",')
		dsk		= json.loads(line)
		info	= dsk.get('info',{})
		rid		= int(info.get('rid',0))
		uid		= int(info.get("uid",0))
		ver		= int(info.get('e_version',0))
		eid		= str(info.get('essay_id',0))
		if eid.isdigit():  # from common flow chart 
			eid = int(eid) 
			submit_hdsk(dsk , rid, uid, eid , ver) 
			index_dsk(dsk , fire.index, rid, uid, eid, ver) 
	except Exception as ex:
		print(">>callback Ex:", ex, time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time())), body.decode()[0:10])
		fire.channel.close()
		fire.connection.close()
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)

class util(object):
	def __init__(self, host='127.0.0.1', port=6379, db=0):
		redis.r	 = redis.Redis(host=host, port=port, db=db, decode_responses=True)
		redis.bs = redis.Redis(host=host, port=port, db=db, decode_responses=False)

	def test(self): 
		''' for test '''
		arr = {"key":"1002-3", "rid":"10", "essay":"English is a internationaly language which becomes importantly for modern world. In China, English is took to be a foreigh language which many student choosed to learn. They begin to studying English at a early age. They use at least one hour to learn English knowledges a day. Even kids in kindergarten have begun learning simple words. That's a good phenomenan, for English is essential nowadays. In addition to, some people think English is superior than Chinese. In me opinion, though English is for great significance, but English is after all a foreign language. it is hard for people to see eye to eye. English do help us read English original works, but Chinese helps us learn a true China. Only by characters Chinese literature can send off its brilliance. Learning a country's culture, especial its classic culture, the first thing is learn its language. Because of we are Chinese, why do we give up our mother tongue and learn our owne culture through a foreign language?"}
		dsk = requests.post("http://wrask.com:7002/gec/dsk?dskhost=dsk.jukuu.com", json=arr).json() 
		submit_hdsk(dsk, 10, 101, 1001,3 ) 

	def info(self): 
		''' hgetall rid:709125 '''
		print( redis.r.hgetall("rid:709125"))

	def parse(self, infile, outfile=None, gechost="127.0.0.1:7002", dskhost='127.0.0.1:7095'): 
		''' parse eev dumped file, one line, one json  '''
		#from util import readline 
		if not outfile: outfile = infile + ".dsk" 
		print ("start to load:", infile, flush=True) 
		with open(outfile, 'w') as fw: 
			for line in readline(infile): 
				try:
					arr = json.loads(line.strip().replace(", null,", ", '',") )
					if not arr : continue 
					arr['rid'] = arr.get('request_id',0)
					dsk = requests.post(f"http://{gechost}/gecv1/dsk?dskhost={dskhost}", json=arr).json()
					fw.write(json.dumps(dsk) + "\n") 
					#submit_hdsk(dsk, arr.get('request_id',0), arr.get("user_id",0), arr.get('essay_id',0), arr.get('version',0) ) 
				except Exception as e:
					print("ex:", e, line)
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)

		print ("finished:", infile, outfile,  flush=True) 

	def consume(self, queue_name, mhost='127.0.0.1', mport=5672, user='guest', pwd='guest', heartbeat=60, durable=True, eshost='es.corpusly.com', idxname='dskes', debug=False ):
		''' rabbitmq consumer  '''
		import pika 
		credentials = pika.PlainCredentials(user, pwd)  
		fire.connection = pika.BlockingConnection(pika.ConnectionParameters(host = mhost,port = mport,virtual_host = '/',credentials = credentials, heartbeat=heartbeat))
		fire.channel= fire.connection.channel()
		fire.es	= Elasticsearch([ eshost ]) 
		fire.index = idxname
		fire.debug = debug

		result = fire.channel.queue_declare(queue = queue_name, durable=durable) 
		print("queue is :", queue_name, flush=True)
		fire.channel.basic_consume(queue_name, callback) #mapf[queue_name] #mapf = { "dsk-dm": dskdm, }
		fire.channel.start_consuming()
		#fire.connection.close()

if __name__ == '__main__': 
	fire.Fire(util) 

# docker run -d --restart=always --name kvrocks -p 6666:6666 -v /data/dskdm-kvr6666:/tmp/kvrocks kvrocks/kvrocks