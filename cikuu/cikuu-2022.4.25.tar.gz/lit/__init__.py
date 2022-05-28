# 2022.3.15
import streamlit as st
import requests 
import pandas as pd

from pyecharts import options as opts #https://share.streamlit.io/andfanilo/streamlit-echarts-demo/master/app.py
from pyecharts.charts import Bar
from streamlit_echarts import st_pyecharts
from streamlit_echarts import st_echarts

corpus = {
"学习者": {"name": "sino","learner": True, "sntnum": 3440000},
"口语":{"name":"twit","learner": False},
"新闻":{"name":"nyt","learner": False},
"博客":{"name":"gblog","learner": False},
"论文":{"name":"sci","learner": False},
"小说":{"name":"guten","learner": False},
"中学生": {"name": "fengtai","learner": True},
"大学生": {"name": "clec","learner": True},
"英式英语":{"name":"bnc","learner": False},
}
corpuslist = [k for k,v in corpus.items()]

triple = {
"动宾": {"name": "dobj_VERB_NOUN", "reverse":False},
"形名": {"name": "amod_NOUN_ADJ","reverse":True},
"主谓": {"name": "nsubj_VERB_NOUN","reverse":True},
}
triplelist = [k for k,v in triple.items()]

def mf( cp, pos, word): 
	arr = requests.post(f"http://{cp}.jukuu.com/kpssi/hit", json=[f"{pos}:{word}","SUM:snt"]).json()
	return round(1000000 * arr.get(f"{pos}:{word}",0) / (arr.get(f"SUM:snt",1)), 2)

mfs		 = lambda pos, word, cps:  { cp: mf(corpus[cp]['name'], pos, word) for cp in cps}
fts_snts = lambda cp, term, topk=3:  [row[0] for row in requests.get(f"http://{cp}.jukuu.com/kpssi", params={"sql":f"SELECT snt FROM fts WHERE terms MATCH '{term}' limit {topk}"}).json()]

def bar_si(dic):
	b = (
    Bar()
    .add_xaxis([k for k,v in dic.items()]) 
    .add_yaxis(q, [v for k,v in dic.items()] )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="Collocation Frequency", subtitle="per million sentences"
        ),
        toolbox_opts=opts.ToolboxOpts(),
    )
)
	st_pyecharts(b)


def bar_data(data, y_label='Count', title=None, subtitle=None ):
	b = (
		Bar()
		.add_xaxis([s for s,i in data])
		.add_yaxis(y_label, [i for s,i in data])
		.set_global_opts(
			title_opts=opts.TitleOpts(
				title=title, subtitle=subtitle
			),
			toolbox_opts=opts.ToolboxOpts(),
		)
	)
	st_pyecharts(
		b, key="echarts"
	)  # Add key argument to not remount component at every Streamlit run

def bar_simple(): #https://share.streamlit.io/andfanilo/streamlit-echarts-demo/master/app.py
	options = {
    "xAxis": {
        "type": "category",
        "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "yAxis": {"type": "value"},
    "series": [{"data": [120, 200, 150, 80, 70, 110, 130], "type": "bar"}],
}
	st_echarts(options=options, height="500px")

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
	print ("hellol")