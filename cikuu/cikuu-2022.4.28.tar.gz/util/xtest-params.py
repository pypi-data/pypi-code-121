# 2022.4.2
import json, time, fire,sys, redis, hashlib ,socket, os
now	= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))

def consume(stream, group, host='127.0.0.1', port=6379, db=0, waitms=3600000, ttl=7200, precount=3):
	''' python xtest-params.py xtest params --host 192.168.201.120 , 2022.4.2'''
	r = redis.Redis(host=host, port=port, db=db, decode_responses=True) 
	redis.bs = redis.Redis(host=host, port=port, db=db, decode_responses=False) 
	try:
		r.xgroup_create(stream, group,  mkstream=True)
	except Exception as e:
		print(e)

	consumer_name = f'consumer_{socket.gethostname()}_{os.getpid()}'
	print(f"Redis consumer started: {consumer_name}|{stream}|{group}| ", r, flush=True)
	while True:
		item = r.xreadgroup(group, consumer_name, {stream: '>'}, count=precount, noack=True, block= waitms )
		try:
			if not item: break
			id,arr = item[0][1][0]  #[['_new_snt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
			print (id, arr, "\t", now(), flush=True)
		except Exception as e:
			print(">>[xconsumeEx]", e, "\t|", item, "\t|",  now())

	r.xgroup_delconsumer(stream, group, consumer_name)
	r.close()
	print ("Quitted:", consumer_name, "\t",now())

if __name__ == '__main__':
	fire.Fire(consume)

'''
[r.xadd('xtest', {i:i}) for i in range(10)]

'''