# 2022.3.2  /home/ubuntu/.local/lib/python3.8/site-packages/uvirun/sqlite.py
import json,fire,os,sqlite3
from uvirun import * 

@app.get("/sqlite/dbnames")
def sqlite_dbnames():
	''' name list of the given folder '''
	return [k for k,v in fire.conns.items()]

@app.get("/sqlite")
def sqlite_query(sql:str="select * from ssi limit 2"):
	''' single file mode '''
	return [row for row in fire.conn.execute(sql).fetchall()]

query = lambda name, sql:  [row for row in fire.conns[name].execute(sql).fetchall()]
@app.post("/sqlite/query")
def sqlite_query(names:list=["gzjc","clec"], sql:str="select * from ssi limit 2"):
	''' query from multiple dbs '''
	return { name : query(name, sql) for name in names }

class util(object):
	def __init__(self): pass 

	def single(self, dbfile, port) :
		''' open a single sqlite db, ie:  python -m uvirun.sqlite test.sqlite 13306 '''
		fire.conn = sqlite3.connect(dbfile, check_same_thread=False)  
		fire.conn.execute('PRAGMA synchronous=OFF')
		uvicorn.run(app, host='0.0.0.0', port=port)

	def folder(self, folder, port, suffix=".sqlite") :
		''' open a folder of sqlite db, ie: python -m uviru.sqlite corpus 13306 '''
		fire.conns = {}
		for root, dirs, files in os.walk(folder):
			for file in files: 
				if file.endswith(suffix):	
					try: 
						print ("root:|", root, "\tfile:|", file, "\tfolder:|", folder, flush=True)
						fire.conns[ file.split('.')[0] ] = sqlite3.connect(f"{root}/{file}", check_same_thread=False)  
					except Exception as e:
						print ("ex:", e, "\t|", file)
		uvicorn.run(app, host='0.0.0.0', port=port)

if __name__ == "__main__":  
	fire.Fire(util)