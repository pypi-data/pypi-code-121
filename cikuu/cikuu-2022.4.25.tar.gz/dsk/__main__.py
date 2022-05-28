# 22-3-13  util and mq 
import json, sys, time, fire,traceback, requests,os, pika
from dsk import *
from dsk.dskes import * 

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def callback(ch, method, properties, body):
	try:
		ch.basic_ack(delivery_tag = method.delivery_tag)
		line	= body.decode().replace(':null,',':"",')
		dsk		= json.loads(line)
		info	= dsk.get('info',{})
		rid		= int(info.get('rid',0))
		uid		= int(info.get("uid",0))
		ver		= int(info.get('e_version',0))
		eid		= str(info.get('essay_id',0))
		if eid.isdigit():  # from the common source
			eid = int(eid) 
			submit_hdsk(dsk , rid, uid, eid , ver) 
			index_dsk(dsk , fire.index, rid, uid, eid, ver) 
	except Exception as ex:
		print(">>callback Ex:", ex, time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time())), body.decode()[0:10])
		fire.channel.close()
		fire.connection.close()
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)

class util(object):
	def __init__(self): pass

	def info(self): 
		''' hgetall rid:709125 '''
		print( redis.r.zrevrange("rids", 0, 10,True))

	def eevdsk(self, infile, host='127.0.0.1', port=6379, db=0, refresh=False):
		''' load parsed dsk from eev, 2022.3.14 '''
		redis.r	 = redis.Redis(host=host, port=port, db=db, decode_responses=True)
		redis.bs = redis.Redis(host=host, port=port, db=db, decode_responses=False)
		if refresh: redis.r.flushdb()
		name = infile.split(".")[0] 
		print ("start to load:", infile, flush=True) 
		for line in readline(infile): 
			try:
				dsk		= json.loads(line.strip()) 
				info	= dsk.get('info',{})
				rid		= int(info.get('request_id',0)) # load from eev
				uid		= int(info.get("user_id",0))
				ver		= int(info.get('version',0))
				eid		= int(info.get('essay_id',0))
				redis.r.zincrby(f'rids:{name}', 1, rid) # record this file 
				submit_hdsk(dsk , rid, uid, eid , ver) 
			except Exception as ex:
				print(">>eevdsk Ex:", ex, "\t|", line)
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)
		print ("finished:", infile, flush=True) 

	def parse_eev(self, rid, outfile=None, host='127.0.0.1', port=3361, db=1, gechost="wrask.com:7002", dskhost='127.0.0.1:7095'): 
		''' parse eev from gpu120 redis 3361, added 2022.3.15  '''
		if not outfile: outfile = f"{rid}.dsk" 
		r	 = redis.Redis(host=host, port=port, db=db, decode_responses=True)
		print ("start to load:", r, rid, flush=True) 
		with open(outfile, 'w') as fw: 
			for eidv in r.zrange(f"rid:{rid}", 0, -1):
				try:
					start = time.time()
					arr = r.hgetall(eidv)
					arr['rid'] = int(arr.get('request_id',0))
					dsk = requests.post(f"http://{gechost}/gec/dsk?dskhost={dskhost}", json=arr).json()
					fw.write(json.dumps(dsk) + "\n") 
					print(eidv, "\t| ", time.time() - start, flush=True)
				except Exception as e:
					print("ex:", e, eidv)
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)
		print ("parse_eev finished:", rid, outfile, r,  flush=True)

	def parse(self, infile, outfile=None, gechost="127.0.0.1:7002", dskhost='127.0.0.1:7095'): 
		''' parse eev dumped file, one line, one json  '''
		#from util import readline 
		if not outfile: outfile = infile + ".dsk" 
		print ("start to load:", infile, flush=True) 
		with open(outfile, 'w') as fw: 
			for line in readline(infile): 
				try:
					arr = json.loads(line.strip().replace(", null,", ", '',") )
					if not arr : continue 
					arr['rid'] = arr.get('request_id',0)
					dsk = requests.post(f"http://{gechost}/gec/dsk?dskhost={dskhost}", json=arr).json()
					fw.write(json.dumps(dsk) + "\n") 
					#submit_hdsk(dsk, arr.get('request_id',0), arr.get("user_id",0), arr.get('essay_id',0), arr.get('version',0) ) 
				except Exception as e:
					print("ex:", e, line)
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)

		print ("finished:", infile, outfile,  flush=True) 

	def consume(self, queue_name, mhost='127.0.0.1', mport=5672, user='guest', pwd='guest', heartbeat=60, durable=True, idxname='dskes', debug=False ):
		''' rabbitmq consumer  '''
		credentials = pika.PlainCredentials(user, pwd)  
		fire.connection = pika.BlockingConnection(pika.ConnectionParameters(host = mhost,port = mport,virtual_host = '/',credentials = credentials, heartbeat=heartbeat))
		fire.channel= fire.connection.channel()
		fire.index = idxname
		fire.debug = debug

		result = fire.channel.queue_declare(queue = queue_name, durable=durable) 
		print("queue is :", queue_name, flush=True)
		fire.channel.basic_consume(queue_name, callback) #mapf[queue_name] #mapf = { "dsk-dm": dskdm, }
		fire.channel.start_consuming()
		#fire.connection.close()

if __name__ == '__main__': 
	fire.Fire(util) 