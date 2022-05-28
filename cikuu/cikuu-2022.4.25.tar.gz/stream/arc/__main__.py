#2022.4.16  xstream consumers 
# docker run --name redis --restart=always -d -p 172.17.0.1:6379:6379 -v $PWD/redis-data:/data redis redis-server --notify-keyspace-events KEA --save ""  --appendonly no
# docker run -d --name redis -p 172.17.0.1:6379:6379 redislabs/redisearch:2.4.3
# docker run -d --restart=always --name=webdis --env=REDIS_HOST=172.17.0.1 --env=REDIS_PORT=6379 -e VIRTUAL_PORT=7379 -p 7379:7379 wrask/webdis
# docker run -d --rm --name redisUI -e REDIS_1_HOST=172.17.0.1 -e REDIS_1_NAME=rft -e REDIS_1_PORT=6379 -p 26379:80 erikdubbelboer/phpredisadmin:v1.13.2
# cola, move redis consumer insider
# docker swarm , start multiple instance, without using supervisor
# python -m stream 

import json,os,time,redis, socket,requests,en, hashlib,traceback,sys
now	= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))

def consume(name:str, func:str,  host='172.17.0.1', port=6379, db=0, waitms=3600000, ttl=7200, precount=1,debug=False, dskhost:str="172.17.0.1:7095" ): 
	''' python -m stream xsnt spacybs | stream name must start with 'x*' , otherwise is a channel of pubsub '''
	redis.r		= redis.Redis(host=host, port=port, db=db, decode_responses=True) 
	redis.bs	= redis.Redis(host=host, port=port, db=db, decode_responses=False) 
	redis.ttl	= ttl 
	redis.debug = debug
	redis.dskhost= dskhost	

	x = __import__("stream", fromlist=[func]) # gecv1.py 
	f = getattr(x, func) 
	print (f"name is : {name} (x* means stream, else channel/pubsub), func is : {f}", flush=True)
	
	if not name.startswith("x"): # is a pubsub channel 
		print (f'pubsub start to listen : {name}, with {f}', now(), flush=True)
		ps = redis.r.pubsub(ignore_subscribe_messages=True)  #https://pypi.org/project/redis/
		ps.subscribe(name)  
		for item in ps.listen():  # keep listening, and print the message upon the detection of message in the channel
			if item['type'] == 'message':
				try:
					f(item['data'])
				except Exception as e:
					print(">>[pubsub]", e, "\t|", item)
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)
		return # is needed ? 

	try:
		redis.r.xgroup_create(name, func,  mkstream=True)
	except Exception as e:
		print(e)

	consumer_name = f'consumer_{socket.gethostname()}_{os.getpid()}'
	print(f"Started: {consumer_name}|{name}|{func}| ", redis.r, now(), f, flush=True)
	while True:
		item = redis.r.xreadgroup(func, consumer_name, {name: '>'}, count=precount, noack=True, block= waitms )
		if not item: break
		if redis.debug: print("xmessage:\t", item, "\t", now(), flush=True)  #redis.func(item)  #[['_new_snt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
		for stm_arr in item : #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
			for id,arr in stm_arr[1]: 
				try:
					f(id, arr) 
				except Exception as e:
					print(">>[stream]", e, "\t|", id, arr)
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)

	redis.r.xgroup_delconsumer(name, func, consumer_name)
	redis.r.close()
	print ("Quitted:", consumer_name, "\t",now())


if __name__ == '__main__':
	import fire
	fire.Fire(consume)