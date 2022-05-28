# 2022.3.6  docker run -it --rm -e file=grampos.svdb -v grampos.svdb:/grampos.svdb -p 8080:80 wrask/sqlite uvicorn sqlite:app --host 0.0.0.0 --port 80
import uvicorn,json,os,collections, sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app		= FastAPI()
file	= os.getenv('file', "grampos.kvdb") 
conn	= sqlite3.connect(file, check_same_thread=False)  
conn.execute('PRAGMA synchronous=OFF')
conn.execute('PRAGMA case_sensitive_like = 1')

@app.get("/sqlite/fetchall")
def sqlite_fetchall(sql:str="select * from si limit 2"):
	''' reutrn list '''
	return [row for row in conn.execute(sql).fetchall()]

@app.get("/sqlite/fetchone")
def sqlite_fetchone(sql:str="select * from si limit 1"):
	''' reutrn one row '''
	return [row for row in conn.execute(sql).fetchone()]

@app.post("/sqlite/hitkeys")
def sqlite_hit_keys(keys:list=["VERB:learn","play a _jj role"], table:str='si', key_column:str='s'):
	''' return rows '''
	return [ row for row in conn.execute(f"select * from {table} where {key_column} in ('"+"','".join([k.replace("'","''") for k in keys])+"')") ]

@app.get("/sqlite/getcnt")
def sqlite_getcnt(sql:str="select count(*) from si"): 
	''' return cnt '''
	return [row for row in conn.execute(sql).fetchone()][0]

@app.get('/')
def home(): return HTMLResponse(content=f"<h2> sqlite api, grampos.svdb, gram,sidb </h2> <a href='/docs'> docs </a> | <a href='/redoc'> redoc </a> <br>2022-3-6 ")

@app.post("/sqlite/batch")
def sqlite_batch(sqls:list=["select * from si limit 2","select * from si where s like 'book/POS:%'"]):
	''' multiple sqls '''
	return { sql: [row for row in conn.execute(sql).fetchall()] for sql in sqls }

if __name__ == "__main__":  
	print(sqlite_fetchall())