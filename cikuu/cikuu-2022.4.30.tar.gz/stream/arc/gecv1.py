# 2022.4.10 cp from dsk/xgecv1.py 
import json, time, sys, redis, hashlib ,socket, os,math, torch,re,traceback
from transformers import pipeline

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

def process(item): #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
	''' '''
	for stm_arr in item : #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
		if stm_arr[0].startswith('xsnts'): 
			for id,arr in stm_arr[1]: 
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
		elif stm_arr[0].startswith('xsnt'): # xsnt, xsntgec 
			try:
				snts	= [arr.get('snt','') for id,arr in stm_arr[1]] #[['xsnt', [('1648947215933-0', {'snt': '1'}), ('1648947215933-1', {'2': '2'}), ('1648947215934-0', {'3': '3'}), ('1648947215934-1', {'4': '4'}), ('1648947215934-2', {'5': '5'}), ('1648947215935-0', {'6': '6'}), ('1648947215935-1', {'7': '7'}), ('1648947215935-2', {'8': '8'}), ('1648947215936-0', {'9': '9'})]]]
				newsnts = [snt for snt in snts if snt and not redis.r.exists(f"gec:{snt}") ]

				if newsnts: 
					sntdic	= gecsnts(newsnts) 
					[redis.r.setex(f"gec:{snt}", redis.ttl, gec) for snt, gec in sntdic.items()]
			except Exception as e:
				print(">>[process_xsnt ex]", e, "\t|", stm_arr[1], "\t|",  now())
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)

if __name__ == '__main__':
	redis.r		= redis.Redis(decode_responses=True) 
	redis.bs	= redis.Redis(decode_responses=False) 
	redis.ttl	= 7200
	process([['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]) 

'''
>>> id = r.xadd('xsnts', {"snts":json.dumps(["She has ready."])})
>>> id
'1648958192091-0'
>>> r.blpop(["suc:1648958192091-0"])
('suc:1648958192091-0', '{"She has ready.": "She is ready."}')
'''