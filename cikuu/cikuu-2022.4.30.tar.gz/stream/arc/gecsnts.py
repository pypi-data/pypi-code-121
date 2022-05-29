# 2022.4.11  translate snts, and publish xsntgec  |  python __main__.py xsnts --group gecsnts --precount 1
import json, time, sys, redis, socket, os,traceback

def getgecs(snts, host="gpu120.wrask.com", port=6379, timeout=5): # put into the ufw white ip list 
	''' '''
	if not hasattr(getgecs, 'r'): getgecs.r = redis.Redis(host=host,port=port, decode_responses=True)
	id  = getgecs.r.xadd("xsnts", {"snts":json.dumps(snts)})
	res	= getgecs.r.blpop([f"suc:{id}",f"err:{id}"], timeout=timeout)
	return {} if res is None else json.loads(res[1])

def process(item): 
	''' 2022.4.11 '''
	for stm_arr in item : #[['xsnts', [('1583928357124-0', {'snts': 'hello worlds'})]]]
		if stm_arr[0].startswith('xsnts'): 
			for id,arr in stm_arr[1]: 
				try:
					snts	= json.loads(arr.get('snts','[]'))
					gecs	= redis.r.mget( [f"gec:{snt}" for snt in snts])
					newsnts = [snt for snt, gec in zip(snts, gecs) if gec is None ]
					sntdic  = getgecs(newsnts) 
					[ redis.r.setex(f"gec:{snt}", redis.ttl, gec) for snt, gec in sntdic.items()]
					arr['sntgec'] = json.dumps({ snt : gec if gec is not None else sntdic.get(snt, snt) for snt, gec in zip(snts, gecs) })
					redis.r.xadd("xsntgec", arr ) # with uid,rid, xid
				except Exception as e:
					print ("parse err:", e, id, arr) 
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)

if __name__ == '__main__':
	redis.r		= redis.Redis(decode_responses=True) 
	redis.bs	= redis.Redis(decode_responses=False) 
	redis.ttl	= 7200
	process([['xsnt', [('1583928357124-0', {'snt': "She has ready."})]]])
