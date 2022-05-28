# 22-3-24  , move the data from dsk-fanout to redis blpop 
import pika,json, sys, time, redis, fire,traceback

class util(object):
	def __init__(self,  host='127.0.0.1', port=5672, user='root', pwd='***', heartbeat=60, ):
		credentials = pika.PlainCredentials(user, pwd)  
		fire.connection = pika.BlockingConnection(pika.ConnectionParameters(host = host,port = port,virtual_host = '/',credentials = credentials, heartbeat=heartbeat))
		fire.channel= fire.connection.channel()

	def blpop(self, queue, rhost = '127.0.0.1', rport=6379, rdb=0, ):  
		'''  '''
		redis.r	= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=True)
		result = fire.channel.queue_declare(queue = queue, durable=True)
		print("queue is :", queue, host, redis.r, flush=True)

		def callback(ch, method, properties, body):
			try:
				ch.basic_ack(delivery_tag = method.delivery_tag)
				dsk = json.loads(body.decode())
				key = dsk.get("info",{}).get("key", time.time()) # must has unique 'key'

				try:
					redis.r.publish('dsk', body.decode() )  
					redis.r.lpush(f"gec-suc:{key}", json.dumps(dsk))
					redis.r.expire(f"gec-suc:{key}", 36000) 
				except Exception as e:
					redis.r.lpush(f"gec-err:{key}", body.decode())
					redis.r.expire(f"gec-err:{key}", 36000) 

			except Exception as ex:
				redis.r.setex(f"gec-invalid-input:{time.time()}", 7200, body.decode())
				print(">>callback Ex:", ex, time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time())), body.decode()[0:10])
				#fire.channel.close()
				#fire.connection.close()

		fire.channel.basic_consume(queue, callback)
		fire.channel.start_consuming()
		#fire.connection.close()

if __name__ == '__main__': 
	fire.Fire(util) 