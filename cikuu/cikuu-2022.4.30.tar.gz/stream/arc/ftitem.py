# 2022.4.12 python __main__.py xitem --group ftitem
import json, time, sys, redis, socket, os,traceback
now	= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))

def submit(xid, arr:dict={"rid":"230537", "uid":'1001', "tid":0, "type":"fill", "label":"open the door"}): 
	'''  ''' 
	rid,uid,tid,label	= arr.get('rid', '0'), arr.get('uid', '0'),arr.get('tid','0'),arr.get('label','')
	borntm			= float( int(xid.split('-')[0])/1000 )
	xidlatest		= redis.r.hget(f"rid-{rid}:xid_latest", f"{uid},{tid}") 
	if xidlatest: redis.r.hset(f"item:{xidlatest}", "latest", 0) # only one is marked as 'latest' 
	redis.r.hset(f"rid-{rid}:xid_latest", f"{uid},{tid}", xid)

	score = redis.r.hget(f"rid-{rid}:tid-{tid}", label)
	if score is None: score = 0
	if redis.debug: print(rid,uid,tid, score , now(), flush=True) 

	arr.update({'borntm':borntm, 'latest':1, "score": float(score)})
	redis.r.hset(f"item:{xid}", "borntm", borntm, arr )  # mirror data of the xitem 
	redis.r.zadd(f"rid-{rid}:zlogs", {json.dumps(arr): borntm}) 
	# cache , for a quicker show 
	redis.r.hset(f"rid-{rid}:uid-{uid}:tid_label", tid,  label )
	redis.r.hset(f"rid-{rid}:tid-{tid}:uid_label", uid,  label )

def process(item): 
	''' 2022.4.12 '''
	for stm_arr in item : 
		if stm_arr[0].startswith('xitem'): 
			for id,arr in stm_arr[1]: 
				try:
					submit(id, arr) 
				except Exception as e:
					print ("process err:", e, id, arr) 
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)

if __name__ == '__main__':
	redis.r		= redis.Redis(decode_responses=True) 
	redis.bs	= redis.Redis(decode_responses=False) 
	redis.ttl	= 7200
	redis.debug = True
	submit('1583928357124-0')
