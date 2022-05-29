# 2022.3.2, my_doc, tag_doc,  sqlite-based , | uvicorn mytag-sqlite:app --host 0.0.0.0 --port 13306 --reload 
import json,os,re, requests,traceback,fire, time,math,collections , hashlib,sys
from collections import	defaultdict, Counter

from uvirun import * 
app.title = "My Tag api, sqlite-corpus"
app.tm = "2022.3.2"

from en import * # need 3.1.1  FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\zhang/.cache/lmdb-spacy311'
from en.spacybs import *
from en import terms,verbnet
attach = lambda doc: ( terms.attach(doc), verbnet.attach(doc), doc.user_data )[-1]  # return ssv, defaultdict(dict)
simple_sent		= lambda doc: len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 
complex_sent	= lambda doc: len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) > 0
compound_sent	= lambda doc: len([t for t in doc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0  # S.conj 

db = Spacybs("mytag.sqlite") # support es ops # db.close()

@app.get("/mytag/newdoc")
def add_text(text:str="The quick fox jumped over the lazy dog. The justice delayed is justice denied.", prefix:str='my', title:str=None, note:str="", addtag:bool=False):
	''' prefix: my/tag '''
	cursor=db.conn.cursor()
	docsnts = snts(text)
	if not title: title = docsnts[0]
	cursor.execute(f'INSERT INTO {prefix}_doc(title,body,note) VALUES (?,?,?)',(title, text, note))
	id = cursor.lastrowid
	print(id)
	for i, snt in enumerate(docsnts):
		doc = nlp(snt)
		db[snt] = tobs(doc)
		cursor.execute(f'INSERT or ignore INTO {prefix}_snt(sid, did, snt) VALUES (?,?,?)',(f"{id}-{i}",id, snt))
		#insert tok, trp, chk 
		for t in doc: 
			cursor.execute(f'INSERT or ignore INTO {prefix}_tok(sid, i, text, lem, pos, tag, dep, head) VALUES (?,?,?,?,?,?,?,?)',(f"{id}-{i}", t.i,
				t.text, t.lemma_, t.pos_, t.tag_, t.dep_, t.head.i))
			cursor.execute(f'INSERT or ignore INTO {prefix}_trp(sid, i, rel, govpos, govlem, deppos, deplem) VALUES (?,?,?,?,?,?,?)',(f"{id}-{i}", t.i,
				t.dep_, t.head.pos_, t.head.lemma_, t.pos_, t.lemma_))
		for np in doc.noun_chunks: 
			cursor.execute(f'INSERT or ignore INTO {prefix}_chk(sid, start, end, chunk, type, lem) VALUES (?,?,?,?,?,?)',(f"{id}-{i}", np.start, np.end, np.text, "np", doc[np.end-1].lemma_))
			
		if addtag: 
			stype = "简单句" if len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "复杂句"
			cursor.execute(f'INSERT or ignore INTO tag_stype(sid, stype) VALUES (?,?)',(f"{id}-{i}", stype))
			for np in doc.noun_chunks: 
				cursor.execute(f'INSERT or ignore INTO tag_span(sid, ibeg, iend, tag,note) VALUES (?,?,?,?,?)',(f"{id}-{i}", 
				doc[np.start].idx, doc[np.start].idx + len(np.text), "名词短语", np.text))

	db.conn.commit()
	return id #add_text(prefix="tag", addtag=True)

@app.get("/mytag/sql")
def corpus_sql(query:str="select * from tag_cate limit 2"):
	return [row for row in db.conn.execute(query).fetchall()]

def init(prefix="my"):
	try:
		db.conn.execute(f"CREATE TABLE IF NOT EXISTS {prefix}_doc (did INTEGER PRIMARY KEY AUTOINCREMENT, title varchar(256), body mediumtext not null, note text not null default '', tm timestamp )")
		db.conn.execute(f"CREATE TABLE IF NOT EXISTS {prefix}_snt ( sid varchar(32) PRIMARY KEY, did integer, snt text )")
		db.conn.execute(f'''CREATE VIRTUAL TABLE if not exists {prefix}_fts USING fts5(sid, snt, terms, columnsize=0, detail=full,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''') #self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=none,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''')
		db.conn.execute(f'CREATE TABLE IF NOT EXISTS {prefix}_tok (sid varchar(16), i int, text varchar(64), lem varchar(64), pos varchar(16), tag varchar(16), dep varchar(16), head int)') 
		db.conn.execute(f'CREATE TABLE IF NOT EXISTS {prefix}_trp (sid varchar(16), i int, rel varchar(32), govlem varchar(64), govpos varchar(16), deplem varchar(64), deppos varchar(16))') 
		db.conn.execute(f'CREATE TABLE IF NOT EXISTS {prefix}_chk (sid varchar(16), start int not null, end int not null, chunk varchar(128) , type varchar(32), lem varchar(64))') 
		db.conn.commit()
		db.conn.execute(f"CREATE UNIQUE INDEX {prefix}_trpidx ON {prefix}_trp (sid,i)") #CREATE UNIQUE INDEX index_name on table_name (column_name);
		db.conn.execute(f"CREATE UNIQUE INDEX {prefix}_chkidx ON {prefix}_chk (sid, start)")
		db.conn.execute(f"CREATE UNIQUE INDEX {prefix}_tokidx ON {prefix}_tok (sid,i)")
		db.conn.commit()
	except Exception as ex:
		print(">>toes ex:", ex)

@app.get("/mytag/refresh_db")
def mytag_refresh_db(): 
	global db 
	db.conn.commit()
	db.conn.close()
	if os.path.exists ("mytag.sqlite") : 
		os.remove("mytag.sqlite")
	db = Spacybs("mytag.sqlite")
	db.conn.execute(f"CREATE TABLE IF NOT EXISTS tag_stype ( sid varchar(32),  stype varchar(32), note varhcar(256), tm timestamp)")
	db.conn.execute(f"CREATE TABLE IF NOT EXISTS tag_span ( sid varchar(32), ibeg int not null, iend int not null, tag varchar(128) not null, note varhcar(256) not null default '', tm timestamp)")
	db.conn.execute(f"CREATE TABLE IF NOT EXISTS tag_cate ( cate varchar(32), tag varchar(32) not null, note varhcar(256) not null default '')")
	db.conn.commit()
	db.conn.execute(f"CREATE UNIQUE INDEX tag_stypeidx ON tag_stype (sid,stype)")
	db.conn.execute(f"CREATE UNIQUE INDEX tag_spanidx ON tag_span (sid,ibeg, iend)")
	db.conn.execute(f"CREATE UNIQUE INDEX tag_tagidx ON tag_cate (cate, tag)")
	[ db.conn.execute(f"insert or ignore into tag_cate ( cate,tag ) values ('从句','{v}')") for v in ("主语从句","宾语从句")]
	db.conn.commit()
	[ init(prefix) for prefix in ('my','tag')] 
	return db 

@app.get('/sent/terms')
def snt_terms(snt:str="I think that I am going to go swimming."):  
	''' return term for stats, 2022.2.26 ''' 
	try:
		doc = nlp(snt) #doc.user_data["snt"] = snt
		doc.user_data["tok"] = [ {"i": t.i, "text":t.text, "lower":t.text.lower(), "lem":t.lemma_, "pos":t.pos_, "tag":t.tag_, "dep":t.dep_, "head":t.head.i} for t in doc]
		attach(doc) 
		return doc.user_data
	except Exception as ex:
		return  {"ex":str(ex), "snt":snt }

if __name__ == "__main__":  
	uvicorn.run(app, host='0.0.0.0', port=13306)

'''
def add_si(s,i):
	db.conn.execute(f"INSERT INTO ssi (s, i) VALUES (?, {i}) ON CONFLICT(s) DO UPDATE SET i = i + {i}", (i,))

def remove_si(s,i):
	db.conn.execute(f"update ssi set i = i - {i} where s = ?", (s,))

conn.execute(f'CREATE TABLE IF NOT EXISTS {self.tablename} (key varchar(512) PRIMARY KEY, value blob)')
conn.execute('REPLACE	INTO spacybs (key,	value) VALUES (?,?)' % self.tablename,	(key, value))
conn.execute(f'CREATE TABLE IF NOT EXISTS ssi (s varchar(128) PRIMARY KEY, i int)')
stype ( ID INTEGER PRIMARY KEY   AUTOINCREMENT, sid integer, tag varchar(100), comment varhcar(256)  
spantag ( ID INTEGER PRIMARY KEY   AUTOINCREMENT, sid integer,  ibeg int, iend int , tag varchar(128), comment varhcar(256) )

INSERT INTO ssi (s, i)
VALUES ('127.0.0.1', 1)
ON CONFLICT(s) DO UPDATE SET i = i + 1;

connection=sqlite3.connect(':memory:')
cursor=connection.cursor()
cursor.execute("CREATE TABLE foo (id integer primary key autoincrement ,
                                    username varchar(50),
                                    password varchar(50))")
cursor.execute('INSERT INTO foo (username,password) VALUES (?,?)',
               ('test','test'))
print(cursor.lastrowid)
'''