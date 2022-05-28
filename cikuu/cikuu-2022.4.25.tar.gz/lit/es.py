# 2022.3.30
import streamlit as st
import requests
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Bar
from streamlit_echarts import st_pyecharts,st_echarts

import redis,spacy,json,requests,os
from collections import defaultdict, Counter

if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.getdoc	= lambda snt: ( bs := redis.bs.get(snt), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setnx(snt, spacy.tobs(doc)) if not bs else None )[1]

from elasticsearch import Elasticsearch,helpers
eshost = os.getenv("eshost","192.168.201.76")
es = Elasticsearch([ f"http://{eshost}:9200" ])  
rows = lambda query, asdic=False: ( res:=requests.post(f"http://{eshost}:9200/_sql",json={"query": query}).json().get('rows',[]), dict(res) if asdic else res)[-1]
freq = lambda query: rows(query)[0][0]
mget = lambda ids, index='essaydm': { ar.get('_id',''): ar.get('_source',{})  for ar in requests.post(f"http://{eshost}:9200/{index}/_mget",json={"ids": ids}).json().get('docs',[])}
#mget("inau", ['./1941-Roosevelt.txt-28','./1941-Roosevelt.txt-12'])

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
def grid_gb(df, pagesize=10): 
	gb = GridOptionsBuilder.from_dataframe(df)
	#customize gridOptions  pip install streamlit-aggrid
	gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
	gb.configure_side_bar()
	gb.configure_selection("single")
	gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=pagesize)
	gb.configure_grid_options(domLayout='normal')
	return gb

def grid_response(df, height=345):
	gb = grid_gb(df) 
	return AgGrid(
		df, 
		gridOptions=gb.build(),
		height=height, 
		width='100%',
		data_return_mode=DataReturnMode.__members__["FILTERED"], 
		update_mode=GridUpdateMode.__members__["MODEL_CHANGED"],
		fit_columns_on_grid_load=True, # auto fit 
		allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
		)

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

if __name__ == '__main__':
	print (rows("select lem, count(distinct uid) cnt from essaydm where type = 'tok' and rid in (2593658,2513865,2589848) and pos='VERB' group by lem order by cnt desc limit 10", True))

# https://www.elastic.co/guide/en/elasticsearch/reference/7.8/set-up-lifecycle-policy.html   ttl 