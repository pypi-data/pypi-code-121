#2022.2.13
import json,os,time,redis,requests, fire, socket
now	= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))

def consume(stream, group,  host='127.0.0.1', port=6379, db=0, waitms=3600000, ttl=3600,
		keyname = 'snts', url="http://127.0.0.1:9100",):
	''' stream: xgecsnts, group: gecv1 '''
	r = redis.Redis(host=host, port=port, db=db, decode_responses=True) 
	try:
		r.xgroup_create(stream, group,  mkstream=True)
	except Exception as e:
		print(e)

	consumer_name = f'consumer_{socket.gethostname()}_{os.getpid()}'
	print(f"Started: {consumer_name}|{stream}|{group}| ", r, flush=True)
	while True:
		item = r.xreadgroup(group, consumer_name, {stream: '>'}, count=1, noack=True, block= waitms )
		try:
			if not item: break
			#print(item)
			id,params = item[0][1][0]  #[['_new_snt', [('1583928357124-0', {'snt': 'hello worlds'})]]]

			try:
				snts = json.loads(params[keyname]) #if 'snts' in params else [params.get('snt','')] # add 'snt' for debug convenience 
				res = requests.post(url, json=snts).text
				r.lpush(f"{id}:suc", res)
				r.expire(f"{id}:suc", ttl) 
			except Exception as e1:
				r.lpush(f"{id}:err", json.dumps(params))
				r.expire(f"{id}:err", ttl) 
				print(">>ex:", e, "\t|", id, params, now())

		except Exception as e:
			print(">>[xconsumeEx]", e, "\t|", item)

	r.xgroup_delconsumer(stream, group, consumer_name)
	r.close()
	print ("Quitted:", consumer_name, "\t",now())

if __name__ == '__main__':
	fire.Fire(consume)