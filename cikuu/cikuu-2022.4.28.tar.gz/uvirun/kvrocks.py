# redis rest wrapper, added 2022.3.2,  backend is redis/pika/kvrocks 
import json,fire,os,redis,requests
from uvirun import * 

@app.get("/redis/{db}")
def redis_execute(db:int=0, code:str="r.info()"):
	''' one line python code runner, '''
	if not hasattr(redis, code): setattr(redis, code, compile(code, '', 'eval') )  
	return eval(getattr(redis, code), {"requests":requests, "json":json, "r":redis.dbs[db], 'redis':redis})

@app.get("/redis/{db}/hjoin/{hkey}")
def hgetall_join(hkey:str="rid:2573411", db:int=0, sepa:str="-"):
	''' eidv:  [{k}-{v}] '''
	return [f"{k}{sepa}{v}" for k,v in redis.dbs[db].hgetall(hkey).items()]

#-----  dsk func --- 
@app.get("/dsk/{rid}/eidvlist")
def eidv_list(rid: int=2573411): return [f"{k}-{v}" for k,v in redis.dbs[0].hgetall(f"rid:{rid}").items()]
@app.get("/dsk/{rid}/snts")
def rid_snts(rid: int=2573411): return (snts := [], [ snts.extend(json.loads(redis.dbs[0].hget(eidv, 'snts'))) for eidv in eidv_list(rid) ] )[0]
@app.get("/dsk/{rid}/mkfs")
def rid_mkfs(rid: int=2573411): return [	json.loads(mkf) for mkf in redis.dbs[1].mget( rid_snts(rid)) ]
@app.get("/dsk/{eidv}/score")
def eidv_score(eidv:str='2573411-2'): return json.loads(redis.dbs[0].hget(eidv,'dsk')).get('info',{}).get('final_score',0.0)

def run(self, port, rhost='127.0.0.1', rport=6379, dbsum=1, bsdb=-1) :
	''' open redis connections , ie:  python -m uvirun.kvrocks 16379
	when bsdb >=0 : enable spacy byte stream cache 
	'''
	redis.dbs	= [redis.Redis(rhost, port=rport, db=i, decode_responses=True) for i in range(0,dbsum) ]
	#redis.r		= redis.dbs[0]  # default 
	if bsdb >=0 : 
		redis.bs	= redis.Redis(rhost, port=rport, db=bsdb, decode_responses=False)
		import spacy 
		if not hasattr(spacy, 'nlp'): 
			spacy.nlp		= spacy.load('en_core_web_sm')
			spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
			spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
			spacy.getdoc	= lambda snt: ( bs := redis.bs.get(snt), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setnx(snt, spacy.tobs(doc)) if not bs else None )[1]

	uvicorn.run(app, host='0.0.0.0', port=port)

if __name__ == "__main__":  
	fire.Fire(run)

'''
eidv_list   = lambda rid: [f"{k}-{v}" for k,v in redis.dsk.hgetall(f"rid:{rid}").items()]
rid_snts	= lambda rid: (	snts := [], [ snts.extend(json.loads(redis.dsk.hget(eidv, 'snts'))) for eidv in eidv_list(rid) ] )[0]
rid_mkfs	= lambda rid: [	json.loads(mkf) for mkf in redis.mkf.mget( rid_snts(rid)) ]
eidv_score  = lambda eidv: json.loads(redis.dsk.hget(eidv,'dsk')).get('info',{}).get('final_score',0.0)
'''