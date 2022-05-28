# 2022.4.10 python __main__.py xsnt --group ftsnt   | spacybs is not needed to run 
import json, time, sys, redis, socket, spacy, os

if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.getdoc	= lambda snt:  ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setex(f"bs:{snt}", redis.ttl, spacy.tobs(doc)) if bs is None else None )[1]

def index(rid, uid, snt, doc, arr):
	''' snt:rid-100876:uid-1001={snt} '''
	from dic import word_idf 
	for t in doc: # added 2022.4.13
		if t.text.lower() in word_idf.word_idf:  
			redis.r.zadd(f"rid-{rid}:word_idf", { t.text.lower(): word_idf.word_idf[t.text.lower()] })
		if t.lemma_ in word_idf.word_idf:  # add vp later 
			redis.r.zadd(f"rid-{rid}:{t.pos_}", { t.lemma_: word_idf.word_idf[t.lemma_] })

	# or judge the last char is [a..z] ? 2022.4.13
	#if not snt or not snt.endswith(".") or not snt.endswith("!") or not snt.endswith("?") or not snt.endswith("'") or not snt.endswith('"'): # incomplete snt
	#	return 

	if not redis.r.hexists(f"snt:rid-{rid}:uid-{uid}={snt}", "lems"):
		lems = [ f"{t.pos_}_{t.lemma_}" for t in doc  if t.pos_ not in ('PUNCT')]
		trps = [ f"{t.dep_}_{t.head.pos_}_{t.pos_}:{t.head.lemma_} {t.lemma_}" for t in doc if t.pos_ not in ('PUNCT')]
		stype = "simple" if len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "complex" 
		if len([t for t in doc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0 : stype = stype + ",compound"
		# index mkf 
		arr.update({"rid": rid, "uid": uid, "snt": snt, "lems": ','.join(lems), "trps": ','.join(trps), "tags": stype})
		redis.r.hset(f"snt:rid-{rid}:uid-{uid}={snt}", "rid", rid, arr )
		if redis.debug: print(snt, arr, flush=True)

def process(item): #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
	''' '''
	for stm_arr in item : #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
		if stm_arr[0].startswith('xsnt'): # xsnt, xsntspacy
			for id,arr in stm_arr[1]: 
				try:
					snt = arr.get('snt','').strip() 
					doc = spacy.getdoc(snt)  
					index(arr.get('rid','0'), arr.get('uid','0'), snt, doc , arr) 
				except Exception as e:
					print ("process err:", e, arr) 

if __name__ == '__main__':
	redis.r		= redis.Redis("172.17.0.1",decode_responses=True) 
	redis.bs	= redis.Redis("172.17.0.1",decode_responses=False) 
	redis.ttl	= 7200
	redis.debug = True
	process([['xsnt', [('1583928357124-0', {'snt': 'The quick fox jumped over the lazy dog.'})]]])

'''
keys snt:* 
5076
'''