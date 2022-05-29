#!/usr/bin/env python -W ignore::DeprecationWarning 
# 2022.2.17, upgrade of sntbs, spacy 3.1.1-based, one single file
import sqlite3,json,collections, fire, traceback,sys, time
from collections import	UserDict,Counter,defaultdict
from tqdm import tqdm

import en # need 3.1.1 #from en import * #
from en import terms,verbnet #, snt_source
attach = lambda doc: ( terms.attach(doc), verbnet.attach(doc), doc.user_data )[-1]  # return ssv, defaultdict(dict)

class Spacybs(UserDict): # change to a neutral name, such as Dbdict ?  then Docbs(Dbdict),   add compress later ? 2021-2-3
	def	__init__(self, filename, tablename='spacybs'): 
		self.filename =	filename
		self.tablename = tablename
		self.conn =	sqlite3.connect(self.filename, check_same_thread=False) 
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS {self.tablename} (key varchar(512) PRIMARY KEY, value blob)')
		self.conn.execute('PRAGMA synchronous=OFF')
		self.conn.commit()

	def	__str__(self): 	return "SqliteDict(%s)"	% (self.filename)
	def	__repr__(self): return str(self)  #	no need	of something complex
	def	__len__(self):	return self.conn.execute('SELECT COUNT(*) FROM	"%s"' %	self.tablename).fetchone()[0]
	def	count(self):	return self.conn.execute('SELECT count(*) FROM "%s"'% self.tablename).fetchone()[0]

	def	keys(self, start=0, len=-1):  
		for key in self.conn.execute(f'SELECT key FROM {self.tablename} ORDER BY rowid limit {start},{len}' ).fetchall(): yield key[0]
	def	values(self, start=0, len=-1): 
		for	value in self.conn.execute(f'SELECT value FROM {self.tablename} ORDER BY rowid  limit {start},{len}').fetchall(): yield value[0]
	def	items(self, start=0, len=-1): 
		for rowid, key, value in self.conn.execute(f'SELECT rowid, key, value FROM	{self.tablename} ORDER BY rowid limit {start},{len}' ).fetchall(): 	yield rowid, key, value
	def	docs(self, start=0, len=-1): 
		for	value in self.conn.execute(f'SELECT value FROM {self.tablename} ORDER BY rowid  limit {start},{len}').fetchall(): yield from_docbin(value[0])

	def	__contains__(self, key): return self.conn.execute('SELECT 1 FROM "%s" WHERE key = ?' %	self.tablename, (key,)).fetchone() is not None

	def	__getitem__(self, key):
		item = self.conn.execute(f'SELECT value FROM "{self.tablename}" WHERE key = ? limit 1', (key,)).fetchone()
		return None if item	is None else item[0] # else json.loads(...)
	def get(self, key): return self[key]

	def	__setitem__(self, key, value): 	self.conn.execute('REPLACE	INTO "%s" (key,	value) VALUES (?,?)' % self.tablename,	(key, value))
	def set(self, key, value): self[key] = value
	def	__delitem__(self, key): self.conn.execute('DELETE FROM	"%s" WHERE key = ?'	% self.tablename,	(key,))
	def	__iter__(self): 		return self.keys()
	def	close(self): 	self.conn.commit()

def init_db(filename):
	conn = sqlite3.connect(filename, check_same_thread=False)  
	conn.execute(f'DROP TABLE IF EXISTS fts')
	conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=full,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''') #self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=none,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''')
	conn.execute('PRAGMA synchronous=OFF')
	conn.commit()
	return conn

def submit_si(dbfile, si, cutoff=0):
	conn = sqlite3.connect(dbfile, check_same_thread=False)  
	conn.execute(f'DROP TABLE IF EXISTS si')
	conn.execute(f'CREATE TABLE IF NOT EXISTS si (s varchar(128) PRIMARY KEY, i int) without rowid')
	for k,v in si.items():
		if v > cutoff : 
			conn.execute(f"replace into si(s,i) values(?,?)", (k,v))
	conn.commit()

def submit_ssi(dbfile, ssi):
	conn = sqlite3.connect(dbfile, check_same_thread=False)  
	conn.execute(f'DROP TABLE IF EXISTS ssi')
	conn.execute(f'CREATE TABLE IF NOT EXISTS ssi (s varchar(128) PRIMARY KEY, i int) without rowid')
	for k,v in ssi.items(): #redis.dm.zadd(f"{corpus}:{k}", dict(v))
		for s,i in v.items(): 
			conn.execute(f"replace into ssi(s,i) values(?,?)", (f"{k}:{s}",i))
	conn.commit()

def submit_wav(dbfile, ssi): # added 2022.5.22
	conn = sqlite3.connect(dbfile, check_same_thread=False)  
	conn.execute(f'DROP TABLE IF EXISTS wav')
	conn.execute(f'CREATE TABLE IF NOT EXISTS wav (word varchar(64), attr varchar(64), val int, PRIMARY KEY(word, attr) ) without rowid') # sim (key, hkey, hval)  
	for k,v in ssi.items(): #redis.dm.zadd(f"{corpus}:{k}", dict(v))
		for s,i in v.items(): 
			conn.execute(f"replace into wav(word, attr,val) values(?,?,?)", (k, s,i))
	conn.commit()

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

incr	= lambda si, *names, delta = 1: [si.update({name: delta}) for name in names ] #incr(si, "one", "two")
doc_fts = lambda conn, rowid, snt, doc: conn.execute(f"insert or ignore into fts(rowid, snt,terms) values(?,?,?)", (rowid, snt, " ".join([ f"{t.pos_}_{t.lemma_}" for t in doc] + [ f"{t.tag_}_{t.lemma_}" for t in doc] + [ f"{t.dep_}_{t.head.pos_}_{t.pos_}_{t.head.lemma_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')]) ))

class util(object):
	
	def fts(self,dbfile, outfile):  
		''' clec.spacybs -> add fts, select * from fts where match(kps) against ('+open_VERB' in boolean mode), 2022.2.26 '''
		conn = init_db(outfile)
		for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try:
				doc = spacy.frombs(bs)
				kps = " ".join([ f"{t.pos_}_{t.lemma_}" for t in doc] + [ f"{t.tag_}_{t.lemma_}" for t in doc] + [ f"{t.dep_}_{t.head.pos_}_{t.pos_}_{t.head.lemma_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')])
				conn.execute(f"insert or ignore into fts(rowid, snt,terms) values(?,?,?)", (rowid, snt, kps ))
			except Exception as e:
				print ("ex:", e, rowid, snt)
		conn.commit()
		print (f"[fts] finished, {dbfile}")

	def fts_docsnts(self,spacydbfile, dbfile):  
		''' doc(rowid, arr['snts']) => fts ,  2022.3.28 '''
		conn = sqlite3.connect(dbfile, check_same_thread=False)  
		conn.execute(f'DROP TABLE IF EXISTS fts')
		conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(sid, snt, terms, columnsize=0, detail=full,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''') #self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=none,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''')
		conn.execute('PRAGMA synchronous=OFF')
		db = Spacybs(dbfile)
		for row in conn.execute("select rowid, arr from doc").fetchall(): 
			try:
				rowid = row[0]
				snts = json.loads(row[1]).get('snts',[])
				for idx, snt in enumerate(snts): 
					doc = spacy.frombs(db[snt]) if snt in db else spacy.nlp(snt) 
					kps = " ".join([ f"{t.pos_}_{t.lemma_}" for t in doc] + [ f"{t.tag_}_{t.lemma_}" for t in doc] + [ f"{t.dep_}_{t.head.pos_}_{t.pos_}_{t.head.lemma_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')])
					conn.execute(f"insert or ignore into fts(sid, snt,terms) values(?,?,?)", (f"{rowid}-{idx}", snt, kps ))
			except Exception as e:
				print ("ex:", e, row)
		conn.commit()
		print (f"[fts_docsnts] finished, {dbfile}")

	def index(self,dbfile, outfile=None, fts=True, topk=None):  
		''' clec.spacybs -> clec.sqlite, 2022.2.27 '''
		if not outfile : outfile  = dbfile.split('.')[0] + ".sqlite" 
		print (f"[index] started, {dbfile} -> {outfile}", flush=True)
		if fts: conn = init_db(outfile)
		ssi = defaultdict(Counter) 
		for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try:
				doc = spacy.frombs(bs)
				terms.zset_ssi(doc, ssi)
				if fts: doc_fts(conn, rowid, snt, doc) 
				if topk is not None and rowid > topk : break # add 2022.3.29, wiki.spacybs is too big , 50G memory is not enough
			except Exception as e:
				print ("ex:", e, rowid, snt)
		if fts: conn.commit()
		print (f"start to dump ssi, {dbfile} -> {outfile}")
		submit_ssi(outfile, ssi)
		print (f"[index] finished, {dbfile} -> {outfile}")

	def towav(self,dbfile, outfile=None, fts=True, topk=None):  
		''' clec.spacybs -> clec.sqlwav, 2022.5.22 '''
		if not outfile : outfile  = dbfile.split('.')[0] + ".sqlwav" 
		print (f"[index] started, {dbfile} -> {outfile}", flush=True)
		if fts: conn = init_db(outfile)
		ssi = defaultdict(Counter) 
		for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try:
				doc = spacy.frombs(bs)
				terms.zset_ssi(doc, ssi)
				if fts: doc_fts(conn, rowid, snt, doc) 
				if topk is not None and rowid > topk : break # add 2022.3.29, wiki.spacybs is too big , 50G memory is not enough
			except Exception as e:
				print ("ex:", e, rowid, snt)
		if fts: conn.commit()
		print (f"start to dump wav, {dbfile} -> {outfile}")
		submit_wav(outfile, ssi)
		print (f"[index] finished, {dbfile} -> {outfile}")

	def tojson(self,dbfile, outfile=None):  
		''' clec.spacybs -> clec.JSONEachRow, 2022.5.23 '''
		if not outfile : outfile  = dbfile.split('.')[0] + ".JSONEachRow" 
		print (f"[index] started, {dbfile} -> {outfile}", flush=True)
		with open(outfile, 'w') as fw: 
			for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
				try:
					doc = spacy.frombs(bs)
					for t in doc: #arr = [ {'sid': rowid, 'i':t.i, "head":t.head.i, 'lex':t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gpos":t.head.pos_, "glem":t.head.lemma_} for t in doc]
						arr = {'sid': rowid, 'i':t.i, "head":t.head.i, 'lex':t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gpos":t.head.pos_, "glem":t.head.lemma_}
						fw.write(json.dumps(arr)+"\n") 
				except Exception as e:
					print ("ex:", e, rowid, snt)
		print (f"[index] finished, {dbfile} -> {outfile}")

	def indexdoc(self,dbfile, sql="select id, doc_txt from doc", ssi=False):  
		''' spider_docs.sqlit3, 2022.3.11 '''
		print (f"[indexdoc] started, {dbfile} ", flush=True)
		conn = sqlite3.connect(dbfile, check_same_thread=False)  
		conn.execute(f'DROP TABLE IF EXISTS fts')
		conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(sid, snt, terms, columnsize=0, detail=full,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''') #self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=none,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''')
		conn.execute('PRAGMA synchronous=OFF')
		conn.commit()
		db = Spacybs(dbfile + ".spacybs")
		ssi = defaultdict(Counter) #si = Counter()
		for row in conn.execute(sql).fetchall(): 
			try:
				did		= row[0]
				essay	= row[1]
				for i,snt in enumerate(spacy.snts(essay) ): 
					doc = spacy.nlp(snt) #frombs(bs)
					if snt and not snt in db: db[snt] = spacy.tobs(nlp(snt))
					conn.execute(f"insert or ignore into fts(sid, snt,terms) values(?,?,?)", (f"{did}-{i}", snt, " ".join([ f"{t.pos_}_{t.lemma_}" for t in doc] + [ f"{t.tag_}_{t.lemma_}" for t in doc] + [ f"{t.dep_}_{t.head.pos_}_{t.pos_}_{t.head.lemma_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')]) ))
					if ssi: terms.zset_ssi(doc, ssi)
			except Exception as e:
				print ("ex:", e, rowid, snt)
		conn.commit()
		db.close()
		print (f"start to dump ssi, {dbfile}")
		if ssi: submit_ssi(dbfile, ssi)
		print (f"[indexdoc] finished, {dbfile}")

	def si(self,dbfile, outfile):  
		''' clec.spacybs -> add si, 2022.2.26 '''
		si = Counter()
		for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try:
				doc = spacy.frombs(bs)
				for t in doc:
					si.update({f"{t.pos_}:{t.lemma_}":1}) # VERB:book 
					si.update({f"LEM:{t.lemma_}":1})
					si.update({f"LOW:{t.text.lower()}":1})
					si.update({f"{t.lemma_}:{t.pos_}:{t.tag_}":1}) #book:VERB:VBD
					si.update({f"{t.lemma_}:LEX:{t.text.lower()}":1}) #book:LEX:booked 
					if t.pos_ not in ("PROPN","PUNCT"): si.update({f"{t.lemma_}:POS:{t.pos_}":1})
					si.update({f"{t.dep_}_{t.head.pos_}_{t.pos_}:{t.head.lemma_} {t.lemma_}":1})
			except Exception as e:
				print ("ex:", e, rowid, snt)
		submit_si(outfile, si)
		print (f"[si] finished, {dbfile}")

	def clasi(self,dbfile, outfile=None):  #CREATE TABLE clasi ( cp varchar(16) not null, lemma varchar(64) not null,  attr varchar(32) not null,  s varchar(64) not null default '', i int not null default 0, unique key uk(cp,lemma,attr,s), index attrs(cp,attr,s)) engine=myisam;
		''' clec.spacybs -> clec.clasi, 2022.5.7 '''
		si = Counter()
		for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try:
				doc = spacy.frombs(bs)
				for t in doc:
					si.update({f"{t.lemma_}\tLEMMA\t{t.lemma_}":1}) 
					si.update({f"{t.lemma_}\tLEX\t{t.text.lower()}":1}) 
					si.update({f"{t.lemma_}\t{t.pos_}\t{t.tag_}":1}) #book  VERB  VBD
					if t.pos_ not in ("PROPN","PUNCT"): si.update({f"{t.lemma_}\tPOS\t{t.pos_}":1})
					si.update({f"{t.head.lemma_}\t{t.dep_}_{t.head.pos_}_{t.pos_}\t{t.lemma_}":1})
			except Exception as e:
				print ("ex:", e, rowid, snt)
		name = dbfile.split('.')[0]
		with open(outfile if outfile else f"{name}.clasi", 'w') as fw: 
			for s,i in si.items():
				try:
					fw.write(f"{name}\t{s}\t{i}\n")
				except Exception as e:
					pass
		print (f"[clasi] finished, {dbfile}")

	def train(self, sntfile, dbfile=None): 
		''' train clec.snt => clec.spacybs, 2021.8.1 '''
		if not dbfile : dbfile = sntfile.split(".")[0].lower() + ".spacybs"
		print("started:", sntfile, dbfile,flush=True)
		db = Spacybs(dbfile)
		for line in tqdm(open(sntfile,'r').readlines()):
			try:
				snt = line.strip()
				if snt and not snt in db: 
					db[snt] = spacy.tobs(spacy.nlp(snt))
			except Exception as e:
				print ("parse ex:", e, line)
		db.close()
		print("finished:", sntfile, dbfile)

	def train_json(self, jsonfile, docidx=6, dbfile=None): 
		''' train spider.json => spider.spacybs, the first column is the docID 2022.3.26 '''
		if not dbfile : dbfile = jsonfile.split(".")[0].lower() + ".spacybs"
		print("started:", jsonfile, dbfile,flush=True)
		start = time.time()
		db = Spacybs(dbfile)
		db.conn.execute(f'CREATE TABLE IF NOT EXISTS doc (did int PRIMARY KEY, arr text, snts text) without rowid')
		for line in readline(jsonfile):
			try:
				arr = json.loads(line.strip(), strict=False)
				did = arr[0]
				essay = arr[docidx]
				snts = spacy.snts(essay) 
				db.conn.execute(f"insert or ignore into doc(did, arr, snts) values(?,?,?)", (did, line, json.dumps(snts)))
				for snt in snts: 
					if snt and not snt in db: 
						db[snt] = spacy.tobs(spacy.nlp(snt))
				#print (did , time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))) #finished: 1k 1k.spacybs 	 using:| 325.5633900165558
			except Exception as e:
				print ("parse ex:", e, line)
		db.close()
		print("finished:", jsonfile, dbfile, "\t using:|", time.time() - start)

	def addfile(self, infile, dbfile=None): 
		''' inau.txt => inau.doc-spacybs, doc(arr), spacybs,  2022.3.26 
		find . -name "*.txt" -exec python spacybs.py addfile {} inau.doc-spacybs \;
		'''
		if not dbfile : dbfile = infile.split(".")[0].lower() + ".doc-spacybs"
		print("started:", infile, dbfile,flush=True)
		start = time.time()
		db = Spacybs(dbfile)
		#db.conn.execute(f'CREATE TABLE IF NOT EXISTS doc (id INTEGER PRIMARY KEY AUTOINCREMENT, arr MEDIUMTEXT, snts MEDIUMTEXT)') # add a md5 ? 
		db.conn.execute(f'CREATE TABLE IF NOT EXISTS doc (arr MEDIUMTEXT)') # { filename, doc,  snts , 
		text = open(infile,'r').read().strip()
		snts = spacy.snts(text) 
		#db.conn.execute(f"insert or ignore into doc(arr, snts) values(?,?)", (json.dumps({'filename':infile, 'doc':text}), json.dumps(snts)))
		db.conn.execute(f"insert or ignore into doc(arr) values(?)", (json.dumps({'filename':infile, 'doc':text, 'snts':snts}), ))
		for snt in snts: 
			if snt and not snt in db: 
				db[snt] = spacy.tobs(spacy.nlp(snt))
		db.close()
		print("finished:", infile, dbfile, "\t | using:", time.time() - start)

	def load_docjson(self, infile, dbfile=None): 
		''' biz.json => biz.doc-spacybs, doc(arr), spacybs,  2022.3.26 '''
		if not dbfile : dbfile = infile.split(".")[0].lower() + ".doc-spacybs"
		print("started:", infile, dbfile,flush=True)
		start = time.time()
		db = Spacybs(dbfile)
		db.conn.execute(f'drop TABLE IF EXISTS doc')
		db.conn.execute(f'CREATE TABLE IF NOT EXISTS doc (arr MEDIUMTEXT)') # { filename, doc,  snts , 
		for line in open(infile,'r').readlines():
			line = line.strip()
			if not line: continue
			db.conn.execute(f"insert or ignore into doc(arr) values(?)", (line, ))
			arr = json.loads(line) 
			for snt in arr['snts']: 
				if snt and not snt in db: 
					db[snt] = spacy.tobs(spacy.nlp(snt))
		db.conn.commit()
		db.close()
		print("finished:", infile, dbfile, "\t | using:", time.time() - start)

	def load_doc(self, infile, dbfile): 
		''' spider-all.json => spider.sqlite, doc(arr), spacybs,  2022.3.30 '''
		print("started:", infile, dbfile,flush=True)
		start = time.time()
		db = Spacybs(dbfile)
		db.conn.execute(f'drop TABLE IF EXISTS doc')
		db.conn.execute(f'CREATE TABLE IF NOT EXISTS doc (arr MEDIUMTEXT)') # { filename, doc,  snts , 
		db.conn.execute(f'DROP TABLE IF EXISTS fts')
		db.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(sid, snt, terms, columnsize=0, detail=full,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''') #self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=none,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''')

		for line in readline(infile):
			try:
				line = line.strip()
				if not line: continue
				arr = json.loads(line)
				rowid = int( arr['id'])
				db.conn.execute(f"insert or ignore into doc(rowid, arr) values(?,?)", (rowid, line))
				for idx, snt in enumerate(arr['snts']): 
					doc = spacy.frombs(db[snt]) if snt in db else spacy.nlp(snt) 
					kps = " ".join([ f"{t.pos_}_{t.lemma_}" for t in doc] + [ f"{t.tag_}_{t.lemma_}" for t in doc] + [ f"{t.dep_}_{t.head.pos_}_{t.pos_}_{t.head.lemma_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')])
					db.conn.execute(f"insert or ignore into fts(sid, snt,terms) values(?,?,?)", (f"{rowid}-{idx}", snt, kps ))
			except Exception as ex:
				print(">>ex:", ex,"\t|",line)

		db.conn.commit()
		db.close()
		print("finished:", infile, dbfile, "\t | using:", time.time() - start)

	def topika(self,dbfile, name=None, host='127.0.0.1', port=9311, db_bs=0, db_dm=5):  
		''' clec.spacybs -> :  snt:clec(list) , {snt}:bs(hash),  2022.1.20 '''
		import redis
		rdm = redis.Redis(host=host, port=port, db=db_dm, decode_responses=True)
		rbs = redis.Redis(host=host, port=port, db=db_bs)
		if not name: name = dbfile.split('.')[0].lower()
		rdm.delete(f"snts:{name}")
		for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try:
				doc = spacy.frombs(bs)
				rdm.rpush(f"snts:{name}", snt ) 
				rbs.setnx(snt, spacy.tobs(doc))
			except Exception as e:
				print ("ex:", e, rowid, snt)
		print (f"[tobs] finished, {dbfile}, {name}")

	def idsource(self,dbfile, outfile=None ):  
		''' clec.spacybs -> clec.idsource , 2022.2.11
			{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}
			Then submit:  es.py idsource  clec.idsource
		'''
		if not outfile: outfile = dbfile.split(".")[0] + ".idsource"
		with open(outfile, 'w') as fw:
			for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
				try:
					doc = spacy.frombs(bs) 
					ssv = attach(doc) 
					for id, source in ssv.items():
						source.update({"src": rowid})
						fw.write(json.dumps({"_id": f"{rowid}-{id}", "_source":source}) + "\n") 
				except Exception as ex:
					print(">>idsource ex:", ex,"\t|", rowid, snt)
		print("submit idsource finished:", dbfile, outfile)

	def snt_toes(self,dbfile, idxname=None, eshost='127.0.0.1', esport=9200, batch=1000000 , refresh=True):  
		''' clec.spacybs -> es/clec directly, 2022.3.25
			{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14}}
		'''
		from elasticsearch import Elasticsearch,helpers
		from so import config
		from en import terms,verbnet, snt_source
		es	= Elasticsearch([ f"http://{eshost}:{esport}" ])  
		if not idxname : idxname = dbfile.split('.')[0].lower()
		if refresh and es.indices.exists(index=idxname): es.indices.delete(index=idxname)
		if not es.indices.exists(index=idxname): es.indices.create(index=idxname, body=config) 

		print ("toes started:", dbfile, idxname, es, flush=True)
		actions=[]
		for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try:
				doc = spacy.frombs(bs) 
				ssv = attach(doc) 
				actions.append({'_op_type':'index', '_index':idxname, '_id': rowid, '_source': snt_source(rowid, doc)}) 
				for id, source in ssv.items():
					source.update({"src":rowid}) # sid doesnot work  "sid": rowid, 
					actions.append({'_op_type':'index', '_index':idxname, '_id': f"{rowid}-{id}", '_source':source})
				if len(actions) > batch : 
					helpers.bulk(client=es,actions=actions, raise_on_error=False)
					actions = []
					print (rowid, snt , flush=True) 
			except Exception as ex:
				print(">>toes ex:", ex,"\t|", rowid, snt)
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)

		helpers.bulk(client=es,actions=actions, raise_on_error=False)
		print("toes finished:", dbfile, idxname)
	
	def doc_toes(self,dbfile, idxname=None, eshost='127.0.0.1', esport=9200, batch=1000000 , refresh=True):  
		''' inau.doc-spacybs -> es/inau directly, 2022.3.26	'''
		from elasticsearch import Elasticsearch,helpers
		from so import config
		from en import terms,verbnet, snt_source
		es	= Elasticsearch([ f"http://{eshost}:{esport}" ])  
		if not idxname : idxname = dbfile.split('.')[0].lower()
		if refresh and es.indices.exists(index=idxname): es.indices.delete(index=idxname)
		if not es.indices.exists(index=idxname): es.indices.create(index=idxname, body=config) 

		db = Spacybs(dbfile)
		print ("doc_toes started:", dbfile, idxname, es, flush=True)
		actions=[]
		for row in db.conn.execute("select rowid, arr from doc").fetchall(): 
			did	 = row[0]
			arr	 = json.loads(row[1])
			snts = arr.get('snts',[])
			arr.update({"did":int(did), "type":"doc"})
			actions.append({'_op_type':'index', '_index':idxname, '_id': did, '_source': arr}) 

			for idx, snt in enumerate(snts): 
				try:
					doc = spacy.frombs(db[snt]) # if snt in db else spacy.nlp(snt) 
					ssv = attach(doc) 
					sid = f"{did}-{idx}"
					actions.append({'_op_type':'index', '_index':idxname, '_id': sid, '_source': snt_source(sid, doc)}) 
					for id, source in ssv.items():
						source.update({"src":sid}) # sid doesnot work  "sid": rowid, 
						actions.append({'_op_type':'index', '_index':idxname, '_id': f"{sid}-{id}", '_source':source})
					if len(actions) > batch : 
						helpers.bulk(client=es,actions=actions, raise_on_error=False)
						actions = []
						print (did, idx, snt , flush=True) 
				except Exception as ex:
					print(">>toes ex:", ex,"\t|", idx, snt)
					exc_type, exc_value, exc_traceback_obj = sys.exc_info()
					traceback.print_tb(exc_traceback_obj)

		helpers.bulk(client=es,actions=actions, raise_on_error=False)
		print("toes finished:", dbfile, idxname)

	def tosnt(self,dbfile):  
		''' dump snt to console '''
		for snt in Spacybs(dbfile).keys() :
			print(snt)

	def merge(self, inpath, attachpath):
		''' 2022.3.27 '''
		conn = sqlite3.connect(inpath)
		conn.text_factory = str
		cur = conn.cursor()
		cur.execute(f'attach database {attachpath} as w')
		cur.execute(f'insert or ignore into spacybs select * from w.spacybs')
		conn.commit()
		print ("finished:", inpath, attachpath) 
			
if __name__	== '__main__':
	fire.Fire(util)

'''
def es_source(name, snt, doc, skip_punct:bool=True): 
	id  = hashlib.md5(snt.strip().encode("utf-8")).hexdigest()
	sntlen = len(doc)
	arr = {f"{name}-{id}": {"snt": snt, "type":"snt", "tc": sntlen, "awl":  sum([ len(t.text) for t in doc])/sntlen, 'postag': ' '.join(['^'] + [f"{t.text}_{t.lemma_}_{t.tag_}_{t.pos_}" for t in doc] + ['$']) } }
	
	[ arr.update({ f"{name}-{id}-trp-{t.i}" : {"src":f"{name}-{id}",'type':'trp','gov': t.head.lemma_, 'rel': f"{t.dep_}_{t.head.pos_}_{t.pos_}", 'dep': t.lemma_ }}) for t in doc if not skip_punct or t.dep_ not in ('punct')]
	[ arr.update({ f"{name}-{id}-tok-{t.i}" : {'type':'tok', 'src': f"{name}-{id}", 'lex': t.text, 'low': t.text.lower(), 'lem': t.lemma_, 'pos': t.pos_, 'tag': t.tag_, 'i':t.i, 'head': t.head.i }}) for t in doc]
	[ arr.update({ f"{name}-{id}-np-{np.start}" : {'type':'np', 'src': f"{name}-{id}", 'lem': doc[np.end-1].lemma_, 'chunk': np.text, }}) for np in doc.noun_chunks]
	return arr 

		conn.execute(f'DROP TABLE IF EXISTS termsnt')
		conn.execute(f'CREATE TABLE IF NOT EXISTS termsnt (term varchar(128) PRIMARY KEY, snt text)')
					termsnt[f"{t.pos_}:{t.lemma_}"] = snt  # highlight later 
					termsnt[f"{t.dep_}_{t.head.lemma_}_{t.lemma_}:{t.head.lemma_} {t.lemma_}"] = snt 
		for term,snt in termsnt.items():
			conn.execute(f"insert or ignore into termsnt(term,snt) values(?,?)", (term, snt))
		conn.commit()

				incr(si, "sum:snt") #si.update({"sntnum":1})
				for t in doc:
					incr(si, "sum:lex",f"{t.pos_}:{t.lemma_}",f"LEM:{t.lemma_}",f"LOW:{t.text.lower()}"
					,f"{t.lemma_}:{t.pos_}:{t.tag_}" #book:VERB:VBD
					,f"{t.lemma_}:LEX:{t.text.lower()}" #book:LEX:booked 
					,f"{t.dep_}_{t.head.lemma_}_{t.lemma_}:{t.head.lemma_} {t.lemma_}")
					if t.pos_ not in ("PROPN","PUNCT"): si.update({f"{t.lemma_}:POS:{t.pos_}":1})


http://sentbase.com/lemma/lex/?q=belong

sqlite> select * from ssi where s like 'book/LEX:%';
book/LEX:book|51
book/LEX:books|40
book/LEX:booked|1
sqlite> select * from ssi where s like 'book/POS:%';
book/POS:NOUN|91
book/POS:VERB|1
sqlite> select * from ssi where s like 'dobj_VERB_NOUN:open %';
dobj_VERB_NOUN:open calendar|1
dobj_VERB_NOUN:open window|2

sqlite> select * from ssi where s like 'consider/VERB:%';
consider/VERB:VB|5
consider/VERB:#|24
consider/VERB:nsubj|12

select * from fts where snt match('booked')  limit 3;

select * from fts where terms match('dobj_VERB_NOUN_open_door')  limit 3;
select * from fts where terms match('VERB_open')  limit 3;

http://sentbase.com/trp/

sqlite> select * from ssi where s in ('dobj_VERB_NOUN:overcome difficulty','~amod_NOUN_ADJ:overcome difficulty');
dobj_VERB_NOUN:overcome difficulty|2

sqlite> select * from ssi where s like 'dobj_VERB_NOUN:overcome %' order by i desc;
dobj_VERB_NOUN:overcome difficulty|2
dobj_VERB_NOUN:overcome illness|1
dobj_VERB_NOUN:overcome dizziness|1
dobj_VERB_NOUN:overcome obstacle|1
dobj_VERB_NOUN:overcome sorrow|1
dobj_VERB_NOUN:overcome date|1

sqlite> select * from ssi where s like '~dobj_VERB_NOUN:difficulty %' order by i desc;
~dobj_VERB_NOUN:difficulty have|6
~dobj_VERB_NOUN:difficulty overcome|2
~dobj_VERB_NOUN:difficulty avoid|1
~dobj_VERB_NOUN:difficulty find|1

select snt from fts where terms match('dobj_VERB_NOUN_overcome_difficulty')  limit 10;
select * from ssi where s in ('dobj_VERB_NOUN:overcome difficulty','~amod_NOUN_ADJ:front door')

				actions.append({'_op_type':'index', '_index':idxname, '_id': rowid, '_source':{'type':'snt', 'snt':snt,'pred_offset': en.pred_offset(doc), 
				'postag':'_^ ' + ' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]) + ' _$',
				'src': rowid,  'tc': len(doc)}}) #'sid': rowid,

def spider(self,dbfile, limit="0-10"):  
		# spider_docs.sqlit3, 2022.3.26
		print (f"[indexdoc] started, {dbfile}, {limit} ", flush=True)
		conn = sqlite3.connect(dbfile, check_same_thread=False)  
		db = Spacybs(dbfile + ".{limit}.spacybs")
		db.conn.execute(f'CREATE TABLE IF NOT EXISTS snts (did int PRIMARY KEY, snts text) without rowid')
		for row in conn.execute(f"select id, doc_txt from doc limit {limit.replace('-',',')}").fetchall(): 
			try:
				did		= row[0]
				essay	= row[1]
				snts	= spacy.snts(essay)
				db.conn.execute(f"insert or ignore into snts(did, snts) values(?,?)", (did, json.dumps(snts)))
				for i,snt in enumerate(snts): 
					doc = spacy.nlp(snt) 
					if snt and not snt in db: db[snt] = spacy.tobs(spacy.nlp(snt))
			except Exception as e:
				print ("ex:", e, row)
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)
		conn.commit()
		db.close()
		print (f"[spider] finished, {dbfile}")

ubuntu@es-corpusly-com-105-249:~/pypi/en$ python spacybs.py load_docjson biz.json 
started: biz.json biz.doc-spacybs
finished: biz.json biz.doc-spacybs 	 | using: 951.5030801296234

cikuu@101.35.196.171|kp>select * from clec;  # lemma, attr, name, cnt
+----------------+-------+------------+-----+
| type           | lem   | attr       | cnt |
+----------------+-------+------------+-----+
| dobj_VERB_NOUN | open  | door       |  16 |
| LEX            | book  | book       | 132 |
| LEX            | book  | booked     |   3 |
| LEX            | book  | books      |  32 |
| NP             | book  | a book     |  16 |
| POS            | book  | NOUN       | 136 |
| POS            | book  | VERB       |   6 |
| POS            | sound | ADJ        |  16 |
| POS            | sound | VERB       |   6 |
| vtov           | plan  | plan to go |   6 |
+----------------+-------+------------+-----+

[ {'sid': rowid, 'i':t.i, "head":t.head.i, 'lex':t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gpos":t.head.pos_, "glem":t.head.lemma_} for t in doc]

CREATE TABLE gzjc
(
`sid` UInt32,
`i` UInt16,
`head` UInt16,
`lex` varchar(64), 
`lem` varchar(64), 
`pos` varchar(16), 
`tag` varchar(16), 
`dep` varchar(16), 
`gpos` varchar(16), 
`glem` varchar(64)
)ENGINE = MergeTree
PRIMARY KEY (sid, i)
ORDER BY (sid, i);

clickhouse-client --query="INSERT INTO gzjc FORMAT JSONEachRow" < gzjc.JSONEachRow

'''