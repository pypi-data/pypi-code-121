#2022.4.1 uvicorn wps-blpop:app --port 7005 --host 0.0.0.0 --reload
import json, time, traceback, en, fastapi, uvicorn, sys, redis,pika,requests,os

app	= fastapi.FastAPI()
credentials = pika.PlainCredentials('pigai', 'NdyX3KuCq')
parameters	= pika.ConnectionParameters( os.getenv('mhost','192.168.201.79'), 5672, '/', credentials, heartbeat=0) #, heartbeat=60
connection	= pika.BlockingConnection(parameters)
redis.channel= connection.channel() 
redis.r		= redis.Redis(host=os.getenv('rhost','192.168.201.120'), decode_responses=True)
redis.rkey  = os.getenv("routing_key", "wps-dsk-to-blpop")

@app.post("/wps/blpop")
def wps_blpop(arr:dict={"key":"1002-3", "essay":"English is a internationaly language which becomes importantly for modern world. In China, English is took to be a foreigh language which many student choosed to learn. They begin to studying English at a early age. They use at least one hour to learn English knowledges a day. Even kids in kindergarten have begun learning simple words. That's a good phenomenan, for English is essential nowadays. In addition to, some people think English is superior than Chinese. In me opinion, though English is for great significance, but English is after all a foreign language. it is hard for people to see eye to eye. English do help us read English original works, but Chinese helps us learn a true China. Only by characters Chinese literature can send off its brilliance. Learning a country's culture, especial its classic culture, the first thing is learn its language. Because of we are Chinese, why do we give up our mother tongue and learn our owne culture through a foreign language?"}, 
	exchange:str="wps-essay", essay_routing_key:str="wps-essay-normal", timeout:int = 5, asjson:bool=True):  
	''' push data to mq, and then pull the result from redis, 2022.4.1 '''
	try:
		if not 'rid' in arr: arr['rid'] = '10'
		arr['routing_key'] = redis.rkey
		key = arr['key'] # must exists	
		redis.channel.basic_publish(exchange=exchange,routing_key=essay_routing_key, body=json.dumps(arr))  #, ensure_ascii=False
		res	= redis.r.blpop([f"gec-suc:{key}",f"gec-err:{key}"], timeout=timeout)	
		if res is None: return {"failed": "Please try to set 'timeout' to a larger value"}
		return json.loads(res[1]) if asjson else res[1] 
	except Exception as err:
		print("Failed:", err, "\n", arr)
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)
		return {"failed": arr['key'], "error": str(err)}

@app.get('/')
def home(): return fastapi.responses.HTMLResponse(content=f"<h2>wps api</h2><a href='/docs'> docs </a> | <a href='/redoc'> redoc </a><br><br>2022.4.1")

@app.get("/wps/ping")
def wps_ping(timeout:int=6,  asjson:bool=False):  
	''' test only '''
	arr	= {"key":f"1002-{time.time()}", "rid":"10","routing_key":"wps-dsk-to-blpop","essay":"English is a internationaly language which becomes importantly for modern world. \nIn China, English is took to be a foreigh language which many student choosed to learn. They begin to studying English at a early age. They use at least one hour to learn English knowledges a day. Even kids in kindergarten have begun learning simple words. That's a good phenomenan, for English is essential nowadays.\nIn addition to, some people think English is superior than Chinese. In me opinion, though English is for great significance, but English is after all a foreign language. it is hard for people to see eye to eye. English do help us read English original works, but Chinese helps us learn a true China. Only by characters Chinese literature can send off its brilliance. Learning a country's culture, especial its classic culture, the first thing is learn its language. Because of we are Chinese, why do we give up our mother tongue and learn our owne culture through a foreign language?"}
	key = arr["key"] 

	requests.post(f"http://root:jkpigai!@192.168.201.79:15672/api/exchanges/%2f/wps-essay/publish", json={"properties":{},"routing_key":'wps-essay-normal',"payload":json.dumps(arr),"payload_encoding":"string"}).text 
	res	= redis.r.blpop([f"gec-suc:{key}",f"gec-err:{key}"], timeout=timeout)	
	return json.loads(res[1]) if asjson else res 

if __name__ == '__main__': #uvicorn.run(app, host='0.0.0.0', port=wwwport)
	print (wps_blpop({"key":"1110", "essay":"Hello world I love you."})) 

'''
@app.get("/wps/essay")
def wps_essay(key:str="1001", essay:str="English is a internationaly language which becomes importantly for modern world.", 
	exchange:str="wps-essay", essay_routing_key:str="wps-essay-normal", timeout:int = 5, asjson:bool=True):  
	# to get essay str, with Chinese chars inside, 2022.4.1
	return wps_blpop({"key":key, "essay":essay},exchange,essay_routing_key,timeout,asjson  )
'''