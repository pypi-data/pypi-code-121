# 2022.3.6  docker run -it --rm -e file=dic.sqlite -p 8080:80 wrask/sqlite:dic uvicorn sqlite-kpssi:app --host 0.0.0.0 --port 80
import uvicorn,json,os,collections, sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app		= FastAPI()
file	= os.getenv('file', "dic.sqlite") 
conn	= sqlite3.connect(file, check_same_thread=False)  
conn.execute('PRAGMA synchronous=OFF')
conn.execute('PRAGMA case_sensitive_like = 1')

rows	= lambda sql: [row for row in conn.execute(sql).fetchall()]
hit		= lambda keys=['NOUN:attention','VERB:be'] : { row[0] : row[1] for row in conn.execute("select s,i from ssi where s in ('"+"','".join([k.replace("'","''") for k in keys])+"')") } 

@app.get("/kpssi")
def sqlite_rows(sql:str="select * from ssi limit 2"):
	''' sqlite query rows '''
	return rows(sql)

@app.post("/kpssi/hit")
def sqlite_hit(keys:list=["VERB:learn","dobj_VERB_NOUN:learn knowledge"]):
	''' hit multiple keys '''
	return hit(keys) 

@app.get("/kpssi/si")
def sqlite_si(key:str="SUM:snt"): 
	''' SUM:snt -> {i} '''
	return [row for row in conn.execute(f"select i from ssi where s = '{key}'").fetchone()][0]

@app.get("/kpssi/zsum")
def sqlite_zsum(prefix:str="dobj_VERB_NOUN:open "): #VERB:
	''' prefix= VERB:/dobj_VERB_NOUN:open  select sum(i) from ssi where s like '{prefix}%' '''
	return [row for row in conn.execute(f"select sum(i) from ssi where s like '{prefix}%'").fetchone()][0]

@app.get('/')
def home(): return HTMLResponse(content=f"<h2> sqlite-kpssi api, clec/gzjc/dic/... </h2> <a href='/docs'> docs </a> | <a href='/redoc'> redoc </a> <br>2022-3-6 ")

@app.post("/kpssi/batch")
def sqlite_query(sqls:list=["select * from ssi limit 2","select * from ssi where s like 'book/POS:%'"]):
	''' multiple sqls '''
	return { sql: rows(sql) for sql in sqls }

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

@app.post("/kpssi/keyness")
def kpssi_keyness(si:dict={"VERB:book":7,"VERB:consider":3}, si_sum:int=None, ref_sum:int=None):
	''' compared with lower lex of current corpus  '''
	dic		= sqlite_hit( [k for k,v in si.items()])
	si_sum	= sum([ i for s,i in si.items() ]) if not si_sum else si_sum
	ref_sum	= sum([ i for s,i in dic.items() ]) if not ref_sum else ref_sum
	return [ ( s, i, dic.get(s,0), likelihood(i,dic.get(s,0) ,si_sum,ref_sum) ) for s,i in si.items()]

if __name__ == "__main__":  
	print(kpssi_keyness())