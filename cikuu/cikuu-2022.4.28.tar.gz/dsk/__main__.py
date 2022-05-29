# 22-5-28  
import json, sys, time, fire,traceback, requests,os
import dsk,util

class Dsk(object):
	def __init__(self, dskhost:str='gpu120.wrask.com:7095'): 
		self.dskhost = dskhost

	def json_to_dskmkf(self,infile, host='192.168.121.3',port=3306,user='root',password='cikuutest!',db='dskmkf', load=True):  
		''' parse bupt.json -> dskmkf , 2022.5.28 '''
		import pymysql 
		conn = pymysql.connect(host=host,port=port,user=user,password=password,db=db)
		cursor= conn.cursor()
		with open(infile.split('.')[0] + ".dsk", 'w') as fw: 
			for line in open(infile, 'r').readlines(): #util.readline(infile) :
				try:
					start = time.time() 
					arr = json.loads(line)
					essay = arr.get("essay", "") 
					if not essay: continue 
					res = dsk.localgec_todsk(essay, dskhost=self.dskhost)
					res['info'].update({"essay_id": arr.get("essay_id", 0), "rid": arr.get("request_id", 0), "uid": arr.get("user_id",0), "e_version": arr.get("version",0) })
					dsk.submit_dskmkf(res, cursor)	 #eid,rid,uid,ver = int( info.get('essay_id',0) ),int( info.get('rid',0) ),int( info.get('uid',0) ),int( info.get('e_version',0) )
					conn.commit()
					print ( "id:", arr['id'] , "  eid:", arr['essay_id'], "\t timing:" , time.time() - start , flush=True) 
				except Exception as e:
					print (e) 
		print("finished parsing:", infile)

	def localgec_todsk(self, essay:str="She has ready. It are ok."): 
		''' test localgec todsk '''
		print (dsk.localgec_todsk(essay, dskhost=self.dskhost))

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
		import pika
		credentials = pika.PlainCredentials(user, pwd)  
		fire.connection = pika.BlockingConnection(pika.ConnectionParameters(host = mhost,port = mport,virtual_host = '/',credentials = credentials, heartbeat=heartbeat))
		fire.channel= fire.connection.channel()
		fire.index = idxname
		fire.debug = debug

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

		result = fire.channel.queue_declare(queue = queue_name, durable=durable) 
		print("queue is :", queue_name, flush=True)
		fire.channel.basic_consume(queue_name, callback) #mapf[queue_name] #mapf = { "dsk-dm": dskdm, }
		fire.channel.start_consuming()
		#fire.connection.close()

if __name__ == '__main__': 
	fire.Fire(Dsk) 