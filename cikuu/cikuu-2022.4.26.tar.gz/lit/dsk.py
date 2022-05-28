# 2022.3.30
import streamlit as st
import requests
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Bar
from streamlit_echarts import st_pyecharts

import redis,spacy,json,requests
from collections import defaultdict, Counter
redis.dsk	= redis.Redis("127.0.0.1", port=3362, db=0, decode_responses=True) 
redis.mkf	= redis.Redis("127.0.0.1", port=3362, db=1, decode_responses=True) 
redis.bs	= redis.Redis("127.0.0.1", port=3362, db=2, decode_responses=False)
redis.eev   = redis.Redis(host='127.0.0.1', port=3361, db=1, decode_responses=True)
r = redis.dsk

if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.getdoc	= lambda snt: ( bs := redis.bs.get(snt), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setnx(snt, spacy.tobs(doc)) if not bs else None )[1]

eidv_list   = lambda rid: [f"{k}-{v}" for k,v in redis.dsk.hgetall(f"rid:{rid}").items()]
rid_snts	= lambda rid: (	snts := [], [ snts.extend(json.loads(redis.dsk.hget(eidv, 'snts'))) for eidv in eidv_list(rid) ] )[0]
rid_mkfs	= lambda rid: [	json.loads(mkf) for mkf in redis.mkf.mget( rid_snts(rid)) ]
eidv_score  = lambda eidv: json.loads(redis.dsk.hget(eidv,'dsk')).get('info',{}).get('final_score',0.0)
eidv_docs  = lambda eidv: [ spacy.getdoc(snt) for snt in json.loads(redis.dsk.hget(eidv,'snts'))]
doc_term   = lambda doc, ssi:  [ ssi[t.pos_].update({t.lemma_:1}) for t in doc]
eidv_term  = lambda eidv: ( ssi := defaultdict(Counter), [ doc_term(doc,ssi)  for doc in eidv_docs(eidv)] )[0]

eidvlist	= lambda rids=[2589013,2362168],ver=None: (arr:=[], 	[arr.append(f"{k}-{ver}" if ver else f"{k}-{v}") for rid in rids for k,v in redis.r.hgetall(f"rid:{rid}").items()])[0]
rid_feedbacks= lambda rid=2589013:	[	json.loads(mkf).get('feedback',{}) for mkf in redis.mkf.mget( rid_snts(rid) ) ]
rid_dims	= lambda rid=2589013,name=None:	{ eidv: json.loads(redis.dsk.hget(eidv,'dsk')).get('doc',{}).get(name,0) if name else json.loads(redis.dsk.hget(eidv,'dsk')).get('doc',{}) for eidv in final_eids_of_rid(rid) }

def final_eids_of_rid(rid:int=2589013, asdic:bool=False):  
	''' 2589013, eid of final version list, return {eid:ver}  {153358308": 17,  "153359759": 27,} ''' 
	dic = defaultdict(int) 
	for eidv in redis.dsk.zrange(f"rid:{rid}",0,-1): 
		arr = eidv.split('-')
		if len(arr) == 2 : 
			eid = int(arr[0])
			ver = int(arr[1])
			if ver > dic[eid] : dic[eid] = ver 
	return dic if asdic else [f"{eid}-{ver}" for eid,ver in dic.items()]

def first_eids_of_rid(rid:int=2589013, asdic:bool=False):  
	''' eid of first version  return {eid:ver}  {153358308": 17,  "153359759": 27,} ''' 
	dic = defaultdict(int) 
	for eidv in redis.dsk.zrange(f"rid:{rid}",0,-1): 
		arr = eidv.split('-')
		if len(arr) == 2 : 
			eid = int(arr[0])
			ver = int(arr[1])
			if ver < dic[eid] or dic[eid] <= 0 : dic[eid] = ver 
	return dic if asdic else [f"{eid}-{ver}" for eid,ver in dic.items()]

from math import log as ln
def likelihood(a,b,c,d, minus=None):  #from: http://ucrel.lancs.ac.uk/llwizard.html
	try:
		if a is None or a <= 0 : a = 0.000001
		if b is None or b <= 0 : b = 0.000001
		E1 = c * (a + b) / (c + d)
		E2 = d * (a + b) / (c + d)
		G2 = round(2 * ((a * ln(a / E1)) + (b * ln(b / E2))), 2)
		if minus or  (minus is None and a/c < b/d): G2 = 0 - G2
		return G2
	except Exception as e:
		print ("likelihood ex:",e, a,b,c,d)
		return 0
