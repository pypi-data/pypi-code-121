# 2022.4.7,  pip install -U torch transformers func_timeout
import json,os,time, sys,math, torch,re
from transformers import pipeline

myname		= os.getenv("myname","noname") # docker name, to be used in the haproxy, to mark different source  
cuda		= os.getenv("cuda",-1) # https://huggingface.co/transformers/v3.0.2/main_classes/pipelines.html #Pipeline supports running on CPU or GPU through the device argument. Users can specify device argument as an integer, -1 meaning "CPU", >= 0 referring the CUDA device ordinal.
task		= os.getenv("task","text2text-generation")
model		= os.getenv("model","/grammar_error_correcter_v1")  #prithivida/grammar_error_correcter_v1
token_split	= lambda sent: re.findall(r"[\w']+|[.,!?;]", sent) # return list
common_perc	= lambda snt="She has ready.", trans="She is ready.": ( toks := set(token_split(snt)), len([t for t in token_split(trans) if t in toks]) / (len(toks)+0.01) )[-1]

def gecsnts(snts:list=["She has ready.","It are ok."],  max_length:int=128,  do_sample:bool=False, batch_size:int=32
		,unchanged_ratio:float=0.45, len_ratio:float=0.5, topk:int=0  # normally, set topk = batch_size 
		, mget =lambda snts: [None for snt in snts] # cache_func , ie. r.mget
		):
	''' batch_size needs to be used on the pipe call, not on the pipeline call. |https://github.com/huggingface/transformers/issues/14613
	return {'She has ready.': 'She is ready.'}, 'It are ok.': 'It is ok.'}
	'''
	if not hasattr(gecsnts, 'pipe'):
		gecsnts.pipe  = pipeline(task, model=model, device=int(cuda)) #https://huggingface.co/transformers/v3.0.2/main_classes/pipelines.html
		if torch.cuda.is_available(): print ("cuda is_available", flush=True) #CUDA_VISIBLE_DEVICES=0
		print(gecsnts.pipe("She has ready."), f"\t|cuda:{cuda}, task:{task}, model:{model}", flush=True )

	gecs = mget(snts) 
	newsnts = [snt for snt, gec in zip(snts, gecs) if gec is None and snt.count(' ') + 10 < max_length]
	if topk > 0 and len(newsnts) > topk : newsnts = newsnts[0:topk] # only trans topk sents, added 2022.4.2

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
	return {snt:gec if gec is not None else dic.get(snt, snt) for snt, gec in zip(snts, gecs) } 

def gecsnts_timeout(snts:list=["She has ready.","It are ok."], timeout:int=6, max_length:int=128,  do_sample:bool=False, batch_size:int=32, unchanged_ratio:float=0.45, len_ratio:float=0.5):
	''' '''
	from func_timeout import func_timeout, FunctionTimedOut
	# how to do if len(snts) > batch_size 
	try:
		return func_timeout( timeout ,gecsnts , args=(snts,max_length,do_sample,batch_size,unchanged_ratio,len_ratio))
	except FunctionTimedOut:
		print ("gecsnts expired:\n", snts) 
	except Exception as err:
		print("gecsnts failed:",snts)
	return {snt:snt for snt in snts}

def pipeline_snt(input:str="He has ready.",  max_length:int=50,  do_sample:bool=False, batch_size:int=32): 
	''' for testing only, no cache, used in haproxy  '''
	return {myname: gecsnts([input], max_length=max_length, do_sample=do_sample, batch_size=batch_size) }

if __name__ == '__main__': # how to add a cache ? 
	print(gecsnts())
