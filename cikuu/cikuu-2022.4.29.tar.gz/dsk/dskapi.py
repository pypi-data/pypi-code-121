# 22-3-15   nohup uvicorn dskapi:app --port 16666 --host 0.0.0.0 --reload &
from collections import Counter
from dsk import *
eidvlist = lambda rids=[2589013,2362168],ver=None: (arr:=[], 	[arr.append(f"{k}-{ver}" if ver else f"{k}-{v}") for rid in rids for k,v in redis.r.hgetall(f"rid:{rid}").items()])[0]

import json,os,uvicorn,time,sys
from fastapi import FastAPI, File, UploadFile,Form, Body
from fastapi.responses import HTMLResponse
app	 = FastAPI() 
@app.get('/')
def home(): 
	return HTMLResponse(content=f"<h2>dskapi, based redis-6666</h2><a href='/docs'> docs </a> | <a href='/redoc'> redoc </a><br>uvicorn uvirun:app --port 80 --host 0.0.0.0 --reload <br><br> 2022.3.15")

@app.get('/dskdm/scores/{rid}')
def rid_scores(rid:str="2536901"):  
	''' 2536901 
	return {eidv:score} ''' 
	return {eidv: redis.r.hget(eidv,'score') for eidv in eidvlist([rid])}

@app.get('/dskdm/feedbacks/{rid}/')
def rid_feedbacks(rid:str="2536901", topk:int=None):  
	''' 2536901
	return {fd:count} ''' 
	si = Counter() #	redis.r.hset(f"fd:{snt}", cate, v.get('kp',''))
	for eidv in eidvlist([rid]):
		for snt in json.loads(redis.r.hget(eidv, 'snts')):
			for k in redis.r.hkeys(f"fd:{snt}"):
				si.update({k:1})
	return si.most_common(topk)

short_msgs = lambda snt, cate :  [v['short_msg'] for k,v in json.loads(redis.r.get(f"mkf:{snt}"))['feedback'].items() if v['cate'].startswith(cate) ] 

@app.get('/dskdm/snts/{rid}/')
def rid_snts(rid:str="2536901", cate:str="e_snt.nv_agree", topk:int=3):  
	''' 2536901 ''' 
	dic = {}
	for eidv in eidvlist([rid]):
		for snt in json.loads(redis.r.hget(eidv, 'snts')):
			for k in redis.r.hkeys(f"fd:{snt}"):
				if k.startswith(cate): 
					dic.update({snt: short_msgs(snt, cate)[0] } )  #json.loads(redis.r.get(f"mkf:{snt}"))['feedback']
					if len(dic) >= topk: return dic
	return dic

@app.get('/dskdm/dim/{rid}')
def rid_dim(rid:str="2536901", dim:str='awl'):  
	''' 2536901   awl/ast/None
	return {eidv:dim} ''' 
	return {eidv: json.loads(redis.r.hget(eidv,'dim'))[dim] for eidv in eidvlist([rid.strip()])} if dim else {eidv: json.loads(redis.r.hget(eidv,'dim')) for eidv in eidvlist([rid.strip()])}

@app.get('/dskdm/trp/{rid}')
def rid_poslemmas(rid:str="2536901", rel:str='dobj_VERB_NOUN', topk:int=None):  
	''' 2536901   rel: dobj_VERB_NOUN/amod_NOUN_ADJ/nsubj_VERB_NOUN
	return Counter ''' 
	si = Counter()
	dep,gpos,dpos = rel.strip().split('_')[0:3]
	for eidv in eidvlist([rid.strip()]):
		for doc in eidv_docs(eidv):
			[ si.update({ f"{t.head.lemma_} {t.lemma_}" :1}) for t in doc if t.dep_ == dep and t.head.pos_ == gpos and t.pos_ == dpos ]
	return si.most_common(topk)

@app.get('/dskdm/poslemmas/{rid}')
def rid_poslemmas(rid:str="2536901", pos:str='VERB', topk:int=None):  
	''' 2536901   pos: VERB/NOUN/ADJ/NOUN/LEX/LEM
	return Counter ''' 
	si = Counter()
	for eidv in eidvlist([rid.strip()]):
		for doc in eidv_docs(eidv):
			if pos == 'LEX': 
				[ si.update({t.text.lower():1}) for t in doc if t.pos_ not in ("PROPN","SPACE")]
			elif pos == 'LEM':
				[ si.update({t.lemma_:1}) for t in doc]
			else:
				[ si.update({t.lemma_:1}) for t in doc if t.pos_ == pos]
	return si.most_common(topk)

from dic.word_awl import word_awl
from dic.word_gsl1 import word_gsl1
from dic.word_gsl2 import word_gsl2
word_level = {"awl": word_awl, "gsl1":word_gsl1, "gsl2":word_gsl2}
@app.get('/dskdm/wordlevel/{rid}')
def rid_wordlevel(rid:str="2536901", level:str='awl', topk:int=None):  
	''' 2536901   level: awl/gsl1/gsl2
	return Counter ''' 
	si = Counter()
	dic = word_level[level] 
	for eidv in eidvlist([rid]):
		for doc in eidv_docs(eidv):
			[ si.update({t.text.lower():1}) for t in doc if t.text.lower() in dic]
	return si.most_common(topk)

if __name__ == '__main__': 
	uvicorn.run(app, host='0.0.0.0', port=16666)

#rid_dims	= lambda rid=2589013:	{ eidv: json.loads(redis.r.hget(eidv,'dim')) for eidv in eidv_list(rid) }