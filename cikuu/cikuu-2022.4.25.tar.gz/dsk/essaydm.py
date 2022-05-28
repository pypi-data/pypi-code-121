# 2022.3.29 cp from dsk-to-essaydm python dsk-to-essaydm.py dsk-to-essaydm --debug true --eshost 172.18.0.1
import json, fire, spacy, redis,traceback

if not hasattr(redis, 'dsk'): 
	rhost = '127.0.0.1'
	rport = 3362
	redis.dsk	= redis.Redis(host=rhost, port=rport, db=0, decode_responses=True)
	redis.mkf	= redis.Redis(host=rhost, port=rport, db=1, decode_responses=True)
	redis.bs	= redis.Redis(host=rhost, port=rport, db=2, decode_responses=False)

if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.getdoc	= lambda snt: ( bs := redis.bs.get(snt), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setnx(snt, spacy.tobs(doc)) if not bs else None )[1]

def docs_terms(eid, rid, uid, docs) : 
	actions=[]
	for idx, doc in enumerate(docs) : 
		sntlen = len(doc)
		if not sntlen : continue
		actions.append({  '_id': f"{eid}-{idx}",  '_source': {'snt':doc.text, "eid":eid, 'rid': rid , 'uid': uid, 'tc':sntlen, 'awl': sum([ len(t.text) for t in doc])/sntlen ,  'type':'snt',	'postag':' '.join(['_^'] + [f"{t.text}_{t.lemma_}_{t.tag_}_{t.pos_}" for t in doc] + ['_$']) }})
		[actions.append({ '_id': f"{eid}-{idx}:trp-{t.i}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'trp', 'src': f"{eid}-{idx}", 'gov': t.head.lemma_, 'rel': f"{t.dep_}_{t.head.pos_}_{t.pos_}", 'dep': t.lemma_ }}) for t in doc if t.dep_ not in ('punct')]
		[actions.append({ '_id': f"{eid}-{idx}:tok-{t.i}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'tok', 'src': f"{eid}-{idx}", 'lex': t.text, 'low': t.text.lower(), 'lem': t.lemma_, 'pos': t.pos_, 'tag': t.tag_, 'i':t.i, 'head': t.head.i }}) for t in doc]
		[actions.append({ '_id': f"{eid}-{idx}:np-{np.start}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'np', 'src': f"{eid}-{idx}", 'lem': doc[np.end-1].lemma_, 'chunk': np.text, }}) for np in doc.noun_chunks]
	return actions 

def index_dsk_actions(eid, rid, uid,final_score, snts, docs, dims, mkfs, index) : 
	''' NOT check eid duplicated '''
	actions=[]
	dims.update({'type':'doc', 'eid': eid, 'rid': rid , 'uid': uid, 'ver':ver, 'final_score':final_score}) #dims = dsk.get("doc", {})
	actions.append({'_op_type':'index', '_index':index, '_id': eid, '_source':dims})

	for idx, snt, doc in enumerate(zip(snts,docs)) : 
		sntlen = len(doc)
		if not sntlen : continue
		actions.append({'_op_type':'index', '_index':index,  '_id': f"{eid}-{idx}",  '_source': {'snt':doc.text, "eid":eid, 'rid': rid , 'uid': uid, 'tc':sntlen, 'awl': sum([ len(t.text) for t in doc])/sntlen ,  'type':'snt',	'postag':' '.join(['^'] + [f"{t.text}_{t.lemma_}_{t.tag_}_{t.pos_}" for t in doc] + ['$']) }})
		[actions.append({'_op_type':'index', '_index':index, '_id': f"{eid}-{idx}:trp-{t.i}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'trp', 'src': f"{eid}-{idx}", 'gov': t.head.lemma_, 'rel': f"{t.dep_}_{t.head.pos_}_{t.pos_}", 'dep': t.lemma_ }}) for t in doc if t.dep_ not in ('punct')]
		[actions.append({'_op_type':'index', '_index':index, '_id': f"{eid}-{idx}:tok-{t.i}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'tok', 'src': f"{eid}-{idx}", 'lex': t.text, 'low': t.text.lower(), 'lem': t.lemma_, 'pos': t.pos_, 'tag': t.tag_, 'i':t.i, 'head': t.head.i }}) for t in doc]
		[actions.append({'_op_type':'index', '_index':index, '_id': f"{eid}-{idx}:np-{np.start}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'np', 'src': f"{eid}-{idx}", 'lem': doc[np.end-1].lemma_, 'chunk': np.text, }}) for np in doc.noun_chunks]
	
		for mkf in mkfs: #dsk['snt']
			for kp, v in mkf['feedback'].items():
				actions.append({'_op_type':'index', '_index':index,  '_id': f"{eid}-{idx}:kp-{v['ibeg']}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid, 'type':'feedback',
				'src': f"{eid}-{idx}",  'kp':v['kp'], 'cate': v['cate']} })
	return actions 

from collections import defaultdict 
def eids (topk=1000):
	''' '''
	eidver = defaultdict(int)
	for eidv in redis.dsk.zrevrange("eids",0, topk): #154762930-2
		arr = eidv.split("-")
		if len(arr) == 2 and eidver[arr[0]] < int(arr[1]) :  
			eidver[arr[0]] = int(arr[1]) 
	return eidver

def eidver (topk):
	''' print: {eid:maxver} '''
	dic = defaultdict(int)
	for eidv in redis.dsk.zrevrange("eids",0, topk): #154762930-2
		arr = eidv.split("-")
		if len(arr) == 2 and dic[arr[0]] < int(arr[1]) :  
			dic[arr[0]] = int(arr[1]) 
	for s,i in dic.items(): print (f"{s}-{i}")

def idsource(eidvfile,  outfile=None): 
	''' dump 3362 data to id_source '''
	if outfile is None : outfile = eidvfile + ".json"
	print ("started:", redis.dsk, eidvfile, outfile, flush=True) 
	with open(outfile, 'w') as fw : 
		for eidv in open(eidvfile,'r').readlines(): #for eid,ver in eids(topk).items(): 
			try:
				eidv = eidv.strip()
				eid = int(eidv.split('-')[0])
				ver = int(eidv.split('-')[-1])
				res = redis.dsk.hgetall( eidv ) # dsk/pids/snts 
				dsk = json.loads(res['dsk'])
				info = dsk.get("info", {})
				snts = json.loads(res['snts'])
				docs = [spacy.getdoc(snt) for snt in snts ]
				rid = int( info.get('rid',0) )
				uid = int( info.get('uid',0) )

				dims = dsk['doc']
				dims.update({'type':'doc', 'eid': eid, 'rid': rid , 'uid': uid, 'ver':ver, 'final_score': float( info.get('final_score',0) ) }) #dims = dsk.get("doc", {})
				fw.write( json.dumps( {'_id': eid, '_source':dims} ) +"\n" )
				[fw.write( json.dumps(act) + "\n" ) for act in docs_terms(eid, rid, uid, docs) ]

				for idx, mkf in enumerate(redis.mkf.mget(snts)): 
					mkf = json.loads(mkf)
					for kp, v in mkf['feedback'].items():
						arr = {'_id': f"{eid}-{idx}:kp-{v['ibeg']}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid, 'type':'feedback', 'src': f"{eid}-{idx}",  'kp':v['kp'], 'cate': v['cate']} }
						fw.write( json.dumps(arr) + "\n" )
			except Exception as ex:
				print ('ex:', ex, "\t", eidv) #hkeys 154779759-3
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)

		print ("finished:", redis.dsk, outfile  ) 

if __name__ == '__main__': 
	fire.Fire({"eidver":eidver, "idsource":idsource}) 

'''

	import redis 
	from elasticsearch import Elasticsearch,helpers
	fire.es		= Elasticsearch([ f"http://{eshost}:{esport}" ]) 
	fire.index  = idxname
	redis.dsk	= redis.Redis(host=rhost, port=rport, db=0, decode_responses=True)
	redis.mkf	= redis.Redis(host=rhost, port=rport, db=1, decode_responses=True)
	redis.bs	= redis.Redis(host=rhost, port=rport, db=2, decode_responses=False)
	print (eshost, fire.es, redis.dsk , flush=True)

	es_eids = set([ doc['_id'] for doc in helpers.scan(fire.es,query={"query": {"match": {"type":"doc"}}}, index=idxname)])
	print ("count of eids in ES", len(es_eids))


def get_eid_ver(es, eid, index): # only final version data kept 
	try:
		res = es.get(index=index, id=eid) # doc_type=self.index_type,
		return int(res['hits']['hits']['_source'].get('ver',0))
	except Exception as ex:
		return 0
'''