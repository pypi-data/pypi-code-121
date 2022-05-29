# 2022.4.13 python __main__.py xsnt --group ftsnt-cola   
import json, redis, os,requests

def process(item): #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
	''' '''
	for stm_arr in item : #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
		if stm_arr[0].startswith('xsnt'): # xsnt, xsntspacy
			for id,arr in stm_arr[1]: 
				try:
					snt = arr.get('snt','') 
					rid, uid, xid  = arr.get('rid','0'), arr.get('uid','0'), arr.get('xid','0')
					if snt and not redis.r.hexists(f"snt:rid-{rid}:uid-{uid}={snt}", "cola"): 
						res = requests.get("http://cola.werror.com/cola/get", params={"snt":snt}).json()
						redis.r.hset(f"snt:rid-{rid}:uid-{uid}={snt}", "cola", float(res))
						redis.r.zadd(f"rid-{rid}:snt_cola", { f"{uid},{xid}:{snt}": float(res) })  # xid = tm 
				except Exception as e:
					print ("parse err:", e, arr) 

if __name__ == '__main__':
	redis.r		= redis.Redis(decode_responses=True) 
	redis.bs	= redis.Redis(decode_responses=False) 
	redis.ttl	= 7200
	process([['xsnt', [('1583928357124-0', {'snt': 'The quick fox jumped over the lazy dog.'})]]])

'''
good/bad sentence ranking 

127.0.0.1:6379> ft.search ftsnt  "@cola:[0, 0.3]" limit 0 2 return 2 snt cola
1) (integer) 739

127.0.0.1:6379> ft.search ftsnt  "@cola:[0.8, 1.0]" limit 0 2 return 2 snt cola
1) (integer) 3787
2) "snt:rid-230537:uid-617925=Last Sunday,the weather was extremely unfavorable and freezing."
3) 1) "snt"
   2) "Last Sunday,the weather was extremely unfavorable and freezing."
   3) "cola"
   4) "0.973"
4) "snt:rid-230537:uid-625132=There are so many unforgettable days in my life."
5) 1) "snt"
   2) "There are so many unforgettable days in my life."
   3) "cola"
   4) "0.9699"

'''