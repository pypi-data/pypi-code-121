# 22-3-13  dsk into one redis-db,  mkf:{snt}, fd:{snt}, bs:{snt},  eidv, rid:{rid}, uid:{uid}
import json, sys, time, redis, fire,traceback, spacy,requests,os
from collections import defaultdict, Counter

rhost    = os.getenv("dskdm_host", "127.0.0.1") 
rport	 = int(os.getenv("dskdm_port", 6666))
rdb		 = int(os.getenv("dskdm_db", 0))
redis.r	 = redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=True)
redis.bs = redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=False)

if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.getdoc	= lambda snt: ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setnx(f"bs:{snt}", spacy.tobs(doc)) if not bs else None )[1]

uids_topk	= lambda topk=10:		redis.r.zrevrange("uids",0, topk, True)
rids_topk	= lambda topk=10:		redis.r.zrevrange("rids",0, topk, True) #[('10', 61.0), ('2589013', 31.0), ('2589553', 7.0), ('2589069', 1.0), ('2588479', 1.0), ('2539223', 1.0)]
eidv_list   = lambda rid=2589013:	[f"{k}-{v}" for k,v in redis.r.hgetall(f"rid:{rid}").items()]
rid_snts	= lambda rid=2589013:	(	snts := [], [ snts.extend(json.loads(redis.r.hget(eidv, 'snts'))) for eidv in eidv_list(rid) ] )[0]
rid_mkfs	= lambda rid=2589013:	[	json.loads(mkf) for mkf in redis.r.mget( [ f"mkf:{snt}" for snt in rid_snts(rid)]) ]
rid_dims	= lambda rid=2589013:	{ eidv: json.loads(redis.r.hget(eidv,'dim')) for eidv in eidv_list(rid) }
eidv_score  = lambda eidv='153359759-27':	redis.r.hget(eidv,'score')
eidv_docs	= lambda eidv='153359759-27':	[ spacy.getdoc(snt) for snt in json.loads(redis.r.hget(eidv,'snts'))]
doc_terms	= lambda doc, ssi:				[ ssi[t.pos_].update({t.lemma_:1}) for t in doc]
doc_pos		= lambda doc, ssi, pos='VERB':	[ ssi[t.pos_].update({t.lemma_:1}) for t in doc if t.pos_ == pos]
eidv_terms	= lambda eidv='153359759-27':	( ssi := defaultdict(Counter), [ doc_terms(doc,ssi)  for doc in eidv_docs(eidv)] )[0]
rid_terms	= lambda rid=2589013:			( ssi := defaultdict(Counter), [ doc_terms( spacy.getdoc(snt) ,ssi)  for snt in rid_snts(rid)] )[0]
rid_pos		= lambda rid=2589013,pos='VERB':( ssi := defaultdict(Counter), [ doc_pos(spacy.getdoc(snt) ,ssi,pos) for snt in rid_snts(rid)] )[0]
#print (rid_dims())

# rids		= r.zrange("rids:zhengzhou",0,-1)
eidvlist		= lambda rids=[2589013,2362168],ver=None: (arr:=[], 	[arr.append(f"{k}-{ver}" if ver else f"{k}-{v}") for rid in rids for k,v in redis.r.hgetall(f"rid:{rid}").items()])[0]
eidvlist_if		= lambda rids=[2589013,2362168],ver=2: (arr:=[], 	[arr.append(f"{k}-{ver}") for rid in rids for k,v in redis.r.hgetall(f"rid:{rid}").items() if redis.r.exists(f"{k}-{ver}")])[0]
eidvlist_dims	= lambda eidvs, dim='awl':	{ eidv: json.loads(redis.r.hget(eidv,'dim'))[dim] for eidv in eidvs }
eidvlist_words	= lambda eidvs, words:	( si := Counter(), [ si.update({t.lower():1})  for doc in eidv_docs(eidv) for t in doc if t.lower() in words ])[0]

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

		redis.r.hmset(eidv, {'rid': rid, 'uid':uid, 'score': score, 
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
					redis.r.hset(f"fd:{snt}", cate, v.get('kp','')) # todo: add simple/complex here 
	
	except Exception as e:
		print("ex:", e, dsk)
		exc_type, exc_value, exc_obj = sys.exc_info()
		traceback.print_tb(exc_obj)

def readline(infile, sepa=None):
	with open(infile, 'r') as fp: #,encoding='utf-8'
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

if __name__ == '__main__': 
	pass #print (rids_topk())

# docker run -d --restart=always --name kvrocks -p 6666:6666 -v /data/dskdm-kvr6666:/var/lib/kvrocks/db kvrocks/kvrocks
'''
{eidv: redis.r.hget(eidv,'score') for eidv in eidvlist(r.zrange("rids:zhengzhou",0,-1))} # final score
{eidv: redis.r.hget(eidv,'score') for eidv in eidvlist(r.zrange("rids:zhengzhou",0,-1), ver=2)} #init score
{eidv: json.loads(redis.r.hget(eidv,'dim'))['awl'] for eidv in eidvlist(r.zrange("rids:zhengzhou",0,-1))} # final dim
'''