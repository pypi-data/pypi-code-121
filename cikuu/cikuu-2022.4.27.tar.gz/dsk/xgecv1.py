# 2022.4.5 upgrade of xsnt-gecv1.py 
import json, time, fire,sys, redis, hashlib ,socket, os,math, torch,re,traceback
from transformers import pipeline

rhost		= os.getenv("rhost", "172.17.0.1")
rport		= int(os.getenv('rport', 6379))
rdb			= int(os.getenv('rdb', 0))
redis.r		= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=True) 
redis.bs	= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=False) 
cuda		= os.getenv("cuda",-1) # https://huggingface.co/transformers/v3.0.2/main_classes/pipelines.html #Pipeline supports running on CPU or GPU through the device argument. Users can specify device argument as an integer, -1 meaning "CPU", >= 0 referring the CUDA device ordinal.
task		= os.getenv("task","text2text-generation")
model		= os.getenv("model","/grammar_error_correcter_v1")  #prithivida/grammar_error_correcter_v1
now			= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
token_split	= lambda sent: re.findall(r"[\w']+|[.,!?;]", sent) # return list
common_perc	= lambda snt="She has ready.", trans="She is ready.": ( toks := set(token_split(snt)), len([t for t in token_split(trans) if t in toks]) / (len(toks)+0.01) )[-1]

def gecsnts(snts:list=["She has ready.","It are ok."],  max_length:int=128,  do_sample:bool=False, batch_size:int=64, unchanged_ratio:float=0.45, len_ratio:float=0.5):
	''' batch_size needs to be used on the pipe call, not on the pipeline call. |https://github.com/huggingface/transformers/issues/14613
	return {'She has ready.': 'She is ready.'}, 'It are ok.': 'It is ok.'}
	'''
	if not hasattr(gecsnts, 'pipe'):
		gecsnts.pipe  = pipeline(task, model=model, device=int(cuda)) #https://huggingface.co/transformers/v3.0.2/main_classes/pipelines.html
		if torch.cuda.is_available(): print ("cuda is_available", flush=True) #CUDA_VISIBLE_DEVICES=0
		print(gecsnts.pipe("She has ready."), f"\t|cuda:{cuda}, task:{task}, model:{model}", flush=True )

	snts = [snt for snt in snts if snt.count(' ') + 10 < max_length ] # skip extra long sents 	# check the extreme long sent ?  truncate it ? 2022.4.3 
	dic = {} #{'hello world': 'Hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello world hello', 'I am ok.': 'I am ok.'}
	
	sntslen = len(snts) 
	offset = 0 
	while offset < sntslen: # added 2022.4.5
		for snt, tgt in zip(snts, gecsnts.pipe(snts[offset:offset + batch_size],  max_length=max_length, do_sample=do_sample, batch_size=batch_size)):
			trans = tgt['generated_text']  # todo : if token change > 50% , skip the trans
			if not ' ' in trans or not ' ' in snt.strip(): # ' ' => "generated_text": "Then, a few years later, the saga began."
				dic[snt] = snt # keep unchanged
			elif common_perc(snt, trans) < unchanged_ratio or abs(math.log( len(snt)/len(trans))) > len_ratio:
				dic[snt] = snt # changed too much, -> discard 
			else:
				dic[snt] = trans
		offset = offset + batch_size
	return dic

## === api 
def xgecsnts_blpop(snts:list=["She has ready.","It are ok."], timeout=3, ):
	''' name:xsnt/xsnts, arr: {"snt": "hello"}  added 2022.4.4 '''
	id	= redis.r.xadd("xsnts", {'snts':json.dumps(snts)})
	return redis.r.blpop([f"suc:{id}",f"err:{id}"], timeout=timeout)

def redis_gecsnts(snts:list=["She has ready.","It are ok."], topk=0, timeout=3):
	''' use blpop-based func, 2022.4.7 '''
	try:
		gecs	= redis.r.mget([ f"gec:{snt}" for snt in snts])
		newsnts = [snt for snt, gec in zip(snts, gecs) if snt and gec is None ]
		if topk > 0 and len(newsnts) > topk : newsnts = newsnts[0:topk] # only trans topk sents

		res		= xgecsnts_blpop(newsnts, timeout=timeout) 
		if res is None : # how to notify the result of this timeout event? 
			redis.r.publish('gecv1_timeout', json.dumps(snts)) #arr['gecv1_timeout'] = newsnts # for debug 
			return { snt: gec for snt, gec in zip(snts, gecs) if gec is not None}

		sntdic  = json.loads(res[1]) #('suc:1649063447036-0', '{"She has ready.": "She is ready.", "It are ok.": "It is ok."}')
		return { snt: gec if gec is not None else sntdic.get(snt,snt) for snt, gec in zip(snts, gecs)}
	except Exception as ex:
		print(">>gecsnts Ex:", ex, "\t|", snts)
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)
		return {}

def process_xsnt(messages): #[('1648947215933-0', {'snt': 'hello'}), ('1648947215933-1', {'2': '2'}),
	''' to prefill the cache  '''
	try:
		snts	= [arr.get('snt','') for id,arr in messages] #[['xsnt', [('1648947215933-0', {'snt': '1'}), ('1648947215933-1', {'2': '2'}), ('1648947215934-0', {'3': '3'}), ('1648947215934-1', {'4': '4'}), ('1648947215934-2', {'5': '5'}), ('1648947215935-0', {'6': '6'}), ('1648947215935-1', {'7': '7'}), ('1648947215935-2', {'8': '8'}), ('1648947215936-0', {'9': '9'})]]]
		newsnts = [snt for snt in snts if snt and not redis.r.exists(f"gec:{snt}") ]

		if newsnts: 
			sntdic	= gecsnts(newsnts) 
			[redis.r.setex(f"gec:{snt}", redis.ttl, gec) for snt, gec in sntdic.items()]
	except Exception as e:
		print(">>[process_xsnt ex]", e, "\t|", messages, "\t|",  now())
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)

def process_xsnts(messages): #[('1648947215933-0', {'snts': '1'}), ('1648947215933-1', {'2': '2'}),
	''' id = xadd('xsnts',  {"snts":["hello"]}),  blpop(id) , 2022.4.3'''
	for id,arr in messages:
		try:
			snts	= json.loads(arr.get('snts','[]'))
			gecs	= redis.r.mget([ f"gec:{snt}" for snt in snts])
			newsnts = [snt for snt, gec in zip(snts, gecs) if snt and gec is None ]
			sntdic	= gecsnts(newsnts) if newsnts else {}
			res		= { snt: gec if gec is not None else sntdic.get(snt,snt) for snt, gec in zip(snts, gecs)}
			redis.r.lpush(f"suc:{id}", json.dumps(res) )
			redis.r.expire(f"suc:{id}", redis.ttl) 
		except Exception as e:
			print ("parse err:", e, id, arr) 
			redis.r.lpush(f"err:{id}", json.dumps(arr))
			redis.r.expire(f"err:{id}", redis.ttl) 
			redis.r.setex(f"exception:{id}", redis.ttl, str(e))

def consume(group, xsnt="xsnt", xsnts="xsnts", maxlen=100000, waitms=3600000, ttl=7200, precount=64, debug=False):
	''' rhost=192.168.201.120 cuda=2 python xgecv1.py consume gecv1 '''
	redis.ttl = ttl
	try:
		redis.r.xgroup_create(xsnt, group,  mkstream=True)
	except Exception as e:
		print(e)

	try:
		redis.r.xgroup_create(xsnts, group,  mkstream=True)
	except Exception as e:
		print(e)

	redis.r.xtrim(xsnt, maxlen)
	redis.r.xtrim(xsnts, maxlen)

	consumer_name = f'consumer_{socket.gethostname()}_{os.getpid()}'
	print(f"Redis consumer started: {consumer_name}|{group}| ", redis.r, gecsnts(), "\n", now(), flush=True)
	while True:
		item = redis.r.xreadgroup(group, consumer_name, {xsnt: '>', xsnts: '>'}, count=precount, noack=True, block= waitms )
		if not item: break #[['xsnt', [('1648947215933-0', {'snt': '1'}), ('1648947215933-1', {'2': '2'}), ('1648947215934-0', {'3': '3'}), ('1648947215934-1', {'4': '4'}), ('1648947215934-2', {'5': '5'}), ('1648947215935-0', {'6': '6'}), ('1648947215935-1', {'7': '7'}), ('1648947215935-2', {'8': '8'}), ('1648947215936-0', {'9': '9'})]]]
		if debug: print( item, "\t", now(), flush=True) 
		for arr in item:  #['xsnt', [('1648947215933-0', {'snt': '1'}),
			if arr[0] == xsnt : 
				process_xsnt(arr[1]) 
			elif arr[0] == xsnts : 
				process_xsnts(arr[1]) 

	redis.r.xgroup_delconsumer(xsnt, group, consumer_name)
	redis.r.xgroup_delconsumer(xsnts, group, consumer_name)
	redis.r.close()
	print ("Quitted:", consumer_name, "\t",now())

if __name__ == '__main__':
	fire.Fire({"consume":consume, "gecsnts": lambda: gecsnts(), 
	"hello": lambda: redis_gecsnts(), 
	"xgecsnts": lambda: xgecsnts_blpop()})

'''
>>> id = r.xadd('xsnts', {"snts":json.dumps(["She has ready."])})
>>> id
'1648958192091-0'
>>> r.blpop(["suc:1648958192091-0"])
('suc:1648958192091-0', '{"She has ready.": "She is ready."}')
'''