# 2022.4.16  python -m stream.xsnts-dsk xsnts --group dsk 
import json, time, sys, redis, socket, os,traceback

def getgecs(snts, host="gpu120.wrask.com", port=6379, timeout=5): # put into the ufw white ip list 
	''' '''
	if not hasattr(getgecs, 'r'): getgecs.r = redis.Redis(host=host,port=port, decode_responses=True)
	id  = getgecs.r.xadd("xsnts", {"snts":json.dumps(snts)})
	res	= getgecs.r.blpop([f"suc:{id}",f"err:{id}"], timeout=timeout)
	return {} if res is None else json.loads(res[1])

def process(item): 
	''' 2022.4.11 '''
	from dsk import mkf
	for stm_arr in item : #[['xsnts', [('1583928357124-0', {'snts': 'hello worlds'})]]]
		if stm_arr[0].startswith('xsnts'): 
			for id,arr in stm_arr[1]: 
				try:
					snts	= json.loads(arr.get('snts','[]'))
					gecs	= redis.r.mget( [f"gec:{snt}" for snt in snts])
					newsnts = [snt for snt, gec in zip(snts, gecs) if gec is None ]
					sntgec  = getgecs(newsnts) 
					[ redis.r.setex(f"gec:{snt}", redis.ttl, gec) for snt, gec in sntgec.items()]

					rid,uid,xid	= arr.get('rid','0'),  arr.get('uid','0'),  arr.get('xid','0')
					dsk	 = mkf.sntsmkf( [ (snt,gec) for snt,gec in sntgec.items()], dskhost=redis.dskhost, asdsk=True, getdoc= lambda snt: ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt))[1] )
					redis.r.setex(f"dsk:{xid}", redis.ttl, json.dumps(dsk)) 

					score = float(dsk.get('info',{}).get("final_score",0))
					redis.r.hset(f"essay:{xid}", "score", score , dsk.get('doc',{}) ) # awl, ast, .. 
					redis.r.zadd(f"rid-{rid}:essay_score", {uid: score} ) # overwriting 

					for mkf in dsk.get('snt',[]):  #for snt, mkf in sntgec_mkfs(sntgec, arr):
						snt = mkf.get('meta',{}).get('snt','')
						redis.r.setex(f"mkf:{snt}", redis.ttl, json.dumps(mkf))
						if not redis.r.hexists(f"snt:rid-{rid}:uid-{uid}={snt}", "cates"):
							cates = [ v['cate'][2:] for k,v in mkf.get('feedback',{}).items() if v['cate'].startswith("e_") or v['cate'].startswith("w_") ]
							redis.r.hset(f"snt:rid-{rid}:uid-{uid}={snt}", "cates", ','.join(cates))
							for cate in cates: 
								redis.r.zincrby(f"rid-{rid}:cate", 1, cate) # snt.nv_agree
								redis.r.zincrby(f"rid-{rid}:catetop", 1, cate.split('.')[0]) # snt

				except Exception as e:
					print ("xsnts-dsk err:", e, id, arr) 
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)

def test():
	redis.r		= redis.Redis(decode_responses=True) 
	redis.bs	= redis.Redis(decode_responses=False) 
	redis.ttl	= 7200
	process([['xsnt', [('1583928357124-0', {'snt': "She has ready."})]]])

from stream import xconsume 
redis.func = process
if __name__ == '__main__':
	import fire
	fire.Fire(xconsume)
