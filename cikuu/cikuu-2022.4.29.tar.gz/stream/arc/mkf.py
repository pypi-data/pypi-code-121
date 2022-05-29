# 2022.4.11  |  python __main__.py xsntgec --group mkf --precount 1
import json, time, sys, redis, socket, os,traceback  #, en,requests

def process(item): #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
	''' '''
	from dsk import mkf
	for stm_arr in item : #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
		if stm_arr[0].startswith('xsntgec'): 
			for id,arr in stm_arr[1]: 
				try:
					sntgec = json.loads(arr.get('sntgec',{}))
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
					print ("process err:", e, id, arr) 
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)

if __name__ == '__main__':
	redis.r		= redis.Redis(decode_responses=True) 
	redis.bs	= redis.Redis(decode_responses=False) 
	redis.ttl	= 7200
	redis.dskhost="127.0.0.1:7095"
	process([['xsntgec', [('1583928357124-0', {'sntgec': "{\"She has ready.\": \"She is ready.\"}"})]]])


'''
def sntgec_mkfs(sntgec, arr, diffmerge:bool=False, dskhost:str="172.17.0.1:7095") :  
	#from en import dims
	from dsk import mkf  #, score  
	#snts   = [snt for snt,gec in sntgec.items()]
	#docs   = getdocs(snts)
	dsk	 = mkf.sntsmkf( [ (snt,gec) for snt,gec in sntgec.items()], dskhost=dskhost, asdsk=True )
	redis.r.hset(f"essay:{arr.get('xid','0')}", "score", dsk.get('info',{}).get("final_score",0), dsk.get('doc',{}) ) # awl, ast, .. 

	#edims  = dims.docs_to_dims(snts, docs) 
	#formula_score = score.dims_score(edims)['formula_score']
	#redis.r.hset(f"essay:{arr.get('xid','0')}", "score", formula_score, edims) # awl, ast, .. 
	
	#inputs = mkf.mkf_inputs(snts, docs, sntgec, diffmerge)
	#mkfs   = requests.post(f"http://{dskhost}/parser", data={"q":json.dumps(inputs).encode("utf-8")}).json() if snts else []
	return zip(snts, dsk['snt'])
#now		= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
#getdocs = lambda snts:  [ ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt))[1] for snt in snts ]

'''