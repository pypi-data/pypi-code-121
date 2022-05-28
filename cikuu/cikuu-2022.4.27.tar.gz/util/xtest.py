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

	item = r.xreadgroup(group, consumer_name, {stream: '>'}, count=precount, noack=True, block= waitms )
	print(">>got:", item, flush=True) 
	r.xgroup_delconsumer(stream, group, consumer_name)
	r.close()
	print ("Quitted:", consumer_name, "\t",now())

if __name__ == '__main__':
	fire.Fire(consume)

'''
[r.xadd('xtest', {i:i}) for i in range(10)]

Redis consumer started: consumer_gpu120_32912|xtest|gpoup1|  Redis<ConnectionPool<Connection<host=192.168.201.120,port=6379,db=0>>>
>>got: [['xtest', [('1648947076426-1', {'4': '4'}), ('1648947076427-0', {'5': '5'}), ('1648947076427-1', {'6': '6'})]]]
Quitted: consumer_gpu120_32912 	 2022.04.03 08:51:40


'''