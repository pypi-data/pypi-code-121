# 22-4-7  engine worker on every cvm, uvirun port: 8000   
import json,os,uvicorn,time,sys, fastapi,requests,en,traceback
from collections import Counter

app	= fastapi.FastAPI() 
@app.get('/essay/sntbr')
def nlp_sntbr(text:str="The quick fox jumped over the lazy dog. Justice delayed is justice denied.", trim:bool=True, with_pid:bool=False, with_offset:bool=False):
	''' '''
	return spacy.sntpidoff(text) if with_offset else spacy.sntpid(text) if with_pid else spacy.snts(text, trim) 

has_cl	= lambda d: any([t for t in d if t.dep_ in ('ccomp','xcomp','mark','csubj','relcl','pcomp')])
cl_num	= lambda docs: len([d for d in docs if has_cl(d)])
import mkf 
@app.post('/essay/todsk')
def essay_to_dsk(sntdic:dict={"She has ready.":"She is ready.", "It are ok.":"It is ok."}, 
	essay:str="The quick fox jumped over the lazy dog. Justice delayed is justice denied.",
	asdsk:bool=True, diffmerge:bool=False, cl_ratio:bool=True, dskhost:str="172.17.0.1:7095"):  # dsk.jukuu.com
	''' a simple wrapper of dsk-7095 , 2022.4.6 '''
	try:
		sntpids = spacy.sntpid(essay)
		snts	= [ snt for snt,pid in sntpids ] 
		pids	= [ pid for snt,pid in sntpids ] 
		docs	= [ spacy.nlp(snt) for snt in snts ] 
		input	= [ mkf.mkf_input(i,snts[i],sntdic.get(snts[i],snts[i]), [t.text for t in doc], [t.text for t in (doc if snts[i] == sntdic.get(snts[i],snts[i]) else spacy.nlp(sntdic.get(snts[i],snts[i])) )], doc, diffmerge, pids[i] )   for i, doc in enumerate(docs)]
		dsk		= requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json()
		if cl_ratio and isinstance(dsk, dict) and 'doc' in dsk: dsk['doc']['cl_ratio'] = cl_num(docs) / (len(snts) + 0.01)
		return dsk 
	except Exception as ex:
		print(">>gecv1_dsk Ex:", ex, "\t|", sntdic)
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)
		return str(ex)

@app.get('/')
def home(): return fastapi.responses.HTMLResponse(content=f"<h2>dsk engine worker in each cvm, wrapper of dsk-7095</h2><a href='/docs'> docs </a> | <a href='/redoc'> redoc </a><br> python -m dsk.uvirun 17095 <br><br> 2022.4.7")

@app.get('/essay/snts/feedbacks')
def snts_feedbacks(snts:list=["The quick fox jumped over the lazy dog.","Justice delayed is justice denied."],asdsk:bool=False, diffmerge:bool=False, dskhost:str="172.17.0.1:7095"):
		''' a simple wrapper of dsk-7095, for a quick feedback computing, 2022.4.6 '''
		try:
			docs	= [ spacy.nlp(snt) for snt in snts ] 
			input	= [ mkf.mkf_input(i,snts[i],snts[i], [t.text for t in doc], [t.text for t in doc], doc, diffmerge)   for i, doc in enumerate(docs)]
			return requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json() if input else {}
		except Exception as ex:
			print(">>snts_feedbacks Ex:", ex, "\t|", snts)

@app.get('/essay/feedbacks')
def feedbacks(essay:str="The quick fox jumped over the lazy dog. Justice delayed is justice denied.",asdsk:bool=False, diffmerge:bool=False, dskhost:str="172.17.0.1:7095"):
		''' a simple wrapper of dsk-7095, for a quick feedback generation, 2022.4.6 '''
		try:
			sntpids = spacy.sntpid(essay)
			snts	= [ snt for snt,pid in sntpids ] 
			pids	= [ pid for snt,pid in sntpids ] 
			docs	= [ spacy.nlp(snt) for snt in snts ] 
			input	= [ mkf.mkf_input(i,snts[i],snts[i], [t.text for t in doc], [t.text for t in doc], doc, diffmerge, pids[i] )   for i, doc in enumerate(docs)]
			return requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json() if input else {}
		except Exception as ex:
			print(">>gecv1_dsk Ex:", ex, "\t|", essay)

@app.post('/essay/gecv1')
def gecv1_dsk(arr:dict={"essay":"English is a internationaly language which becomes importantly for modern world. In China, English is took to be a foreigh language which many student choosed to learn. They begin to studying English at a early age. They use at least one hour to learn English knowledges a day. Even kids in kindergarten have begun learning simple words. That's a good phenomenan, for English is essential nowadays. In addition to, some people think English is superior than Chinese. In me opinion, though English is for great significance, but English is after all a foreign language. it is hard for people to see eye to eye. English do help us read English original works, but Chinese helps us learn a true China. Only by characters Chinese literature can send off its brilliance. Learning a country's culture, especial its classic culture, the first thing is learn its language. Because of we are Chinese, why do we give up our mother tongue and learn our owne culture through a foreign language?"}, 
	diffmerge:bool=False, body:str='essay', asdsk:bool=True, gecoff:bool=False, dskhost:str="172.17.0.1:7095", asjson:bool=True):  #dsk.jukuu.com
	''' call sequ:  1. spacy  2. gecv1, 3. dsk7095,  2022.4.7 '''
	import gecv1
	try:
		sntpids = spacy.sntpid(arr.get(body,''))
		snts	= [ snt for snt,pid in sntpids ] 
		pids	= [ pid for snt,pid in sntpids ] 
		docs	= [ spacy.nlp(snt) for snt in snts ]
		sntdic  = gecv1.gecsnts(snts) if not gecoff else { snt:snt for snt in snts}
		input	= [ mkf.mkf_input(i,snts[i],sntdic.get(snts[i],snts[i]), [t.text for t in doc], [t.text for t in (doc if snts[i] == sntdic.get(snts[i],snts[i]) else spacy.nlp(sntdic.get(snts[i],snts[i])) )], doc, diffmerge, pids[i] )   for i, doc in enumerate(docs)]
		res		= requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")})
		return res.json() if asjson else res.text
	except Exception as ex:
		print(">>gecv1_dsk Ex:", ex, "\t|", arr)
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)
		return str(ex)

@app.post('/essay/xadd')
def xadd_blpop(arr:dict={"essay":"English is a internationaly language which becomes importantly for modern world. In China, English is took to be a foreigh language."}, 
		rhost:str='172.17.0.1', rport=6379, rdb=0, 
		timeout:int=3, stream:str='xessay'): 
	''' arr keys: score/pingyu/debug/timeout , 2022.4.6 '''
	import redis 
	if not hasattr(redis,'r'):  
		redis.r	 = redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=True) 
		redis.bs = redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=False) 

	id = redis.r.xadd(stream, arr) 
	res	= redis.r.blpop([f"suc:{id}",f"err:{id}"], timeout= int(arr.get('timeout',timeout)) )
	return res if res is None else json.loads(res[1])

def run(port):
	''' python3 -m dsk.uvirun 8000 '''
	uvicorn.run(app, host='0.0.0.0', port=port)

if __name__ == '__main__': 
	import fire
	fire.Fire(run)	