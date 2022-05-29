# 2022.3.16 cp from spacybs | doc, snt, fts, mkf 
import sqlite3,json,collections, fire, traceback,sys,spacy,requests, hashlib
from collections import	UserDict,Counter,defaultdict

md5		= lambda s: hashlib.md5(s.encode("utf8")).hexdigest()
spacy.nlp= spacy.load('en_core_web_sm')
frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
tobs	= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
from en import terms
#from en.dims import essay_to_dims,  use dims local computing 

class Docfts(UserDict): 
	def	__init__(self, filename="docfts.sqlite", tablename='spacybs'): 
		self.filename =	filename
		self.tablename = tablename
		self.conn =	sqlite3.connect(self.filename, check_same_thread=False) 
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS dsk (did varchar(64) PRIMARY KEY, title text, body text, snts text, kws text, dims text, info text, memo text, score float, tm timestamp)') #did INTEGER PRIMARY KEY AUTOINCREMENT,
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS mkf (sid varchar(64) not null primary key, snt text, feedbacks text, meta text) without rowid')   
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS {self.tablename} (key varchar(512) PRIMARY KEY, value blob)')
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS stype (tag varchar(128) PRIMARY KEY, tm timestamp) without rowid') # {sid}:simple
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS spantag (tag varchar(128) PRIMARY KEY, chunk text, tm timestamp) without rowid') # {did}:{ibeg},{iend},{tag}
		self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(sid, snt, terms, columnsize=0, detail=full,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''') #self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=none,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''')
		self.conn.execute('''CREATE VIRTUAL TABLE if not exists catesnt USING fts5(cate, snt, columnsize=0, detail=full,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''') #self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=none,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_.'")''')
		self.conn.execute('PRAGMA synchronous=OFF')
		self.conn.execute('PRAGMA case_sensitive_like = 1')
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

incr	= lambda si, *names, delta = 1: [si.update({name: delta}) for name in names ] #incr(si, "one", "two")
doc_fts = lambda conn, rowid, snt, doc: conn.execute(f"insert or ignore into fts(rowid, snt,terms) values(?,?,?)", (rowid, snt, " ".join([ f"{t.pos_}_{t.lemma_}" for t in doc] + [ f"{t.tag_}_{t.lemma_}" for t in doc] + [ f"{t.dep_}_{t.head.pos_}_{t.pos_}_{t.head.lemma_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')]) ))

import json,os,uvicorn,time
from fastapi import FastAPI, File, UploadFile,Form, Body
from fastapi.responses import HTMLResponse
app			= FastAPI() 
db			= Docfts()
add_stype	= lambda sid, stype: db.conn.execute(f"insert or ignore into stype(tag) values(?)", (f"{sid}:{stype}", ))
add_tag		= lambda did, ibeg,iend, tag, chunk: db.conn.execute(f"insert or ignore into spantag(tag,chunk) values(?,?)", (f"{did}:{ibeg},{iend},{tag}",chunk ))
add_fts		= lambda sid, snt, doc:  db.conn.execute(f"insert or ignore into fts(sid, snt,terms) values(?,?,?)", (sid, snt, " ".join([ f"{t.pos_}_{t.lemma_}" for t in doc] + [ f"{t.tag_}_{t.lemma_}" for t in doc] + [ f"{t.dep_}_{t.head.pos_}_{t.pos_}_{t.head.lemma_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')]) ))
add_np		= lambda did, doc: [ add_tag(did, doc[np.start].idx, doc[np.start].idx + len(np.text), "np", np.text) for np in doc.noun_chunks if np.end - np.start > 1]
add_ap		= lambda did, doc: [ add_tag(did,doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text),"ap",doc[ibeg:iend].text) for name, ibeg,iend in terms.matchers['ap'](doc) ]
add_vp		= lambda did, doc: [ add_tag(did,doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text),"vp",doc[ibeg:iend].text) for name, ibeg,iend in terms.matchers['vp'](doc) ]

@app.get('/docfts/sql')
def feedbacks(sql:str="select * from feedbacks limit 2"):
	''' execute sql , 2022.4.2 '''
	return [row for row in db.conn.execute(sql).fetchall()]

@app.get('/')
def home(): 
	return HTMLResponse(content=f"<h2>docfts,  dsk,mkf,bs, fts </h2><a href='/docs'> docs </a> | <a href='/redoc'> redoc </a><br>uvicorn docfts:app --port 80 --host 0.0.0.0 --reload <br> <br> 2022.3.20")

@app.get('/docfts/newdoc')
def add_newdoc(title:str="Hello world", body:str="She is ready. The quick fox jumped over the lazy dog. Justice delayed is justice denied.", gecdsk:str="http://gec.jukuu.com/gecv1/dsk"):
	''' '''
	did = md5(body)  
	if db.conn.execute(f"SELECT count(*) from dsk where did ='{did}'").fetchone()[0] > 0: return "DOC already exists"
	doc = spacy.nlp(body.strip()) 
	snts = [sent.text for sent in doc.sents]

	db.conn.execute('insert or ignore into dsk (did , title,	body, snts) VALUES (?,?,?,?)', (did, title, body, json.dumps(snts)))
	rowid = db.conn.execute('SELECT LAST_INSERT_ROWID()').fetchone()[0]
	print ('rowid:', rowid, did, flush=True)

	( add_np(did,doc) , add_ap(did,doc) , add_vp(did,doc) )
	[ add_tag(did, t.idx, t.idx + len(t.text), t.pos_, t.text) for t in doc if t.pos_ in ("VERB","NOUN","ADJ","ADV") ]
	for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
		children = list(v.subtree)
		start = children[0].i  	#end = children[-1].i 
		cl = " ".join([c.text for c in v.subtree])
		add_tag(did, doc[start].idx, doc[start].idx + len(cl), v.dep_, cl)
	[ add_tag(did, t.idx, t.idx + len(t.text), "VBN", t.text) for t in doc if t.tag_ == 'VBN' ]
	for name, ibeg,iend in terms.matchers['vtov'](doc) :
		add_tag(did, doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text), "vtov", doc[ibeg:iend].text )
	for name, ibeg,iend in terms.matchers['vvbg'](doc) :
		add_tag(did, doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text), "vvbg", doc[ibeg:iend].text  )

	for i, sent in enumerate(doc.sents): 
		sid = f"{did}-{i}"
		snt = sent.text
		sdoc = sent.as_doc() # nlp(snt)
		if snt and not snt in db: db[snt] = tobs(sdoc)
		add_fts(sid, snt, sdoc)  #db.conn.execute(f"insert or ignore into fts(sid, snt,terms) values(?,?,?)", (f"{did}-{i}", snt, " ".join([ f"{t.pos_}_{t.lemma_}" for t in sdoc] + [ f"{t.tag_}_{t.lemma_}" for t in sdoc] + [ f"{t.dep_}_{t.head.pos_}_{t.pos_}_{t.head.lemma_}_{t.lemma_}" for t in sdoc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')]) ))
		add_stype(sid, "simple" if len([t for t in sdoc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "complex" )
		if len([t for t in sdoc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0: add_stype(sid, 'compound')

	dsk = requests.post(gecdsk, json={"key":str(did), "rid":"10", "essay":body, "title": title}).json()
	db.conn.execute(f"update dsk set kws = ?, dims=?, info=? where did = '{did}'", (json.dumps(dsk['kw']),json.dumps(dsk['doc']),json.dumps(dsk['info']),))
	for i,arr in enumerate(dsk['snt']): 
		meta = arr.get('meta',{})
		feedback = arr.get('feedback',{})
		db.conn.execute(f"insert or ignore into mkf(sid, snt,feedbacks, meta) values(?,?,?,?)", ( f"{did}-{i}", meta.get('snt',''), json.dumps(feedback),json.dumps(meta) ))
		for k,v in feedback.items(): 
			db.conn.execute(f"insert or ignore into catesnt(cate, snt) values(?,?)", (v.get('cate',''), meta.get('snt','') ) )
	db.conn.commit()
	return did 

@app.get('/docfts/termpos')
def term_pos(pos:str='VERB',topk:int=None):
	''' return si '''
	si = Counter()
	for row in db.conn.execute("select snts from dsk").fetchall():
		for snt in json.loads(row[0]): 
			doc = frombs(db[snt])
			[ si.update({t.lemma_:1})  for t in doc if t.pos_ == pos]
	return si.most_common(topk)	

@app.get('/docfts/feedbacks')
def feedbacks(topk:int=None, all:bool=True):
	''' return si '''
	si = Counter()
	for row in db.conn.execute("select feedbacks from mkf").fetchall():
		for k,v in json.loads(row[0]).items(): 
			if all or k.startswith("e_") or k.startswith("w_"): 
				si.update({v.get('cate',''):1})
	return si.most_common(topk)	

@app.get('/docfts/dim')
def doc_dim(name:str=None):
	''' return {did:awl} '''
	si = Counter()
	dic = { row[0]: json.loads(row[1]) for row in db.conn.execute("select did, dims from dsk").fetchall() } # did -> dims 
	return dic if not name else {did: dim[name] for did, dim in dic.items()}

@app.get('/docfts/ssi')
def db_ssi(simple:bool=True):  
	''' clec.spacybs -> clec.sqlite, 2022.2.27 '''
	ssi = defaultdict(Counter) 
	for rowid, snt, bs in db.items() :
		try:
			doc = frombs(bs)
			terms.zset_ssi(doc, ssi) # en.terms
		except Exception as e:
			print ("ex:", e, rowid, snt)
	return ssi 

from dic.word_awl import word_awl
from dic.word_gsl1 import word_gsl1
from dic.word_gsl2 import word_gsl2
word_level = {"awl": word_awl, "gsl1":word_gsl1, "gsl2":word_gsl2}
@app.get('/docfts/wordlevel')
def doc_wordlevel(level:str='awl', topk:int=None):  
	''' level: awl/gsl1/gsl2 	return Counter ''' 
	si = Counter()
	dic = word_level[level] 
	for rowid, snt, bs in db.items() :
		try:
			doc = frombs(bs)
			[ si.update({t.text.lower():1}) for t in doc if t.text.lower() in dic]
		except Exception as e:
			print ("ex:", e, rowid, snt)
	return si.most_common(topk)

@app.post('/annotate/phrase')
def annotate_phrase(text="I think that I am going to go to the cinema. The quick fox jumped over the lazy dog.", classes:dict={"NP":"NP","VP":"VP","AP":"AP"}):  
	''' {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}], ''' 
	doc = spacy.nlp(text) 
	spans = [ [doc[np.start].idx, doc[np.start].idx + len(np.text), classes["NP"]] for np in doc.noun_chunks if np.end - np.start > 1]
	for name, ibeg,iend in terms.matchers['ap'](doc) :
		spans.append( [doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text), classes["AP"] ] )
	for name, ibeg,iend in terms.matchers['vp'](doc) :
		spans.append( [doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text), classes["VP"] ] )
	return spans

@app.get('/annotate/pos')
def annotate_pos(text="I think that I am going to go to the cinema. The quick fox jumped over the lazy dog.", classes:str="VERB,NOUN,ADJ,ADV"):  
	''' {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}], ''' 
	doc = spacy.nlp(text) 
	pos = classes.strip().split(",")
	spans = [ [t.idx, t.idx + len(t.text), t.pos_] for t in doc if t.pos_ in pos]
	return spans

@app.get('/annotate/clause')
def annotate_clause(text="I think that I am going to go to the cinema. What I think is right."):  
	''' {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}], ''' 
	doc = spacy.nlp(text) 
	spans = []
	for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
		children = list(v.subtree)
		start = children[0].i  	#end = children[-1].i 
		cl = " ".join([c.text for c in v.subtree])
		spans.append ([doc[start].idx, doc[start].idx + len(cl), v.dep_])
	return spans

@app.post('/annotate/non_pred_verb')
def annotate_non_pred_verb(text="I think that I am going to go to the cinema. It is sunken.", classes:dict={"vtov":"vtov","VBN":"VBN","vvbg":"vvbg"}):  
	'''  ''' 
	doc = spacy.nlp(text) 
	spans = [ [t.idx, t.idx + len(t.text), "VBN"] for t in doc if t.tag_ == classes['VBN'] ]
	for name, ibeg,iend in matchers['vtov'](doc) :
		spans.append( [doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text), classes["vtov"] ] )
	for name, ibeg,iend in matchers['vvbg'](doc) :
		spans.append( [doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text), classes["vvbg"] ] )
	return spans

@app.get('/annotate/stype')
def annotate_stype(text="I think that I am going to go to the cinema. What I think is right."):  #, classes:str="simple,complex,compound"
	''' {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}], ''' 
	doc = spacy.nlp(text)
	stags = []
	for sent in doc.sents:
		spans = []
		sdoc = sent.as_doc()
		spans.append ("simple" if len([t for t in sdoc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "complex" )
		if len([t for t in sdoc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0:
			spans.append('compound')
		stags.append( {"start":sent.start, "end":sent.end, "sent": sent.text, "stags": spans })
	return stags

@app.get('/annotate/essay')
def annotate_essay(essay:str="I think that I am going to go to the cinema. What I think is right."): 
	'''  did=102 '''
	doc = nlp(essay) 
	ssv = defaultdict(dict) 
	[ ssv["NP"].update({f"{doc[np.start].idx},{doc[np.start].idx + len(np.text)},NP":np.text}) 	for np in doc.noun_chunks if np.end - np.start > 1]
	for name, ibeg,iend in matchers['ap'](doc) :
		ssv["AP"].update({f"{doc[ibeg].idx},{doc[ibeg].idx + len(doc[ibeg:iend].text)},AP": doc[ibeg:iend].text})
	for name, ibeg,iend in matchers['vp'](doc) :
		ssv["VP"].update({f"{doc[ibeg].idx},{doc[ibeg].idx + len(doc[ibeg:iend].text)},VP": doc[ibeg:iend].text})

	# VERB: VBD/VBP/VBG
	[ ssv[t.pos_].update({f"{t.idx},{t.idx + len(t.text)},{t.tag_}": t.text}) for t in doc if t.pos_ in ["VERB","NOUN","ADJ","ADV"] ]

	# clause
	for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
		children = list(v.subtree)
		start = children[0].i  	#end = children[-1].i 
		cl = " ".join([c.text for c in v.subtree])
		ssv["clause"].update({f"{doc[start].idx},{doc[start].idx + len(cl)},{v.dep_}": cl})

	#non_pred_verb
	#[ self.r.hset(f"non_pred_verb:{did}",f"{t.idx},{t.idx + len(t.text)},VBN", t.text) for t in doc if t.tag_ == 'VBN']
	for name, ibeg,iend in matchers['vtov'](doc) :
		ssv["non_pred_verb"].update({f"{doc[ibeg].idx},{doc[ibeg].idx + len(doc[ibeg:iend].text)},vtov": doc[ibeg:iend].text})
	for name, ibeg,iend in matchers['vvbg'](doc) :
		ssv["non_pred_verb"].update({f"{doc[ibeg].idx},{doc[ibeg].idx + len(doc[ibeg:iend].text)},vvbg": doc[ibeg:iend].text})

	# stype
	for sent in doc.sents:
		sdoc = sent.as_doc()
		if sdoc.text.strip() == '' : continue #added 2022.3.11
		stype = "simple" if len([t for t in sdoc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "complex" 
		ssv["stype"].update({f"{sent.start},{sent.end},{stype}": sent.text})
		if len([t for t in sdoc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0:
			ssv["stype"].update({f"{sent.start},{sent.end},compound": sent.text})
	return ssv

class util(object): 
	def __init__(self): pass

	def hello(self):  
		''' verb list  '''
		print (  term_pos() )

	def uvirun(self, port) : 
		''' python -m en.docfts uvirun 8000 '''
		uvicorn.run(app, host='0.0.0.0', port=port)

	def load(self, infile, idxname) : 
		''' load text file into db  '''
		with open(infile, 'r',encoding='utf-8') as fp:
			add_newdoc(infile, fp.read() )
		print ("finished:", infile ) 

if __name__ == "__main__":  
	fire.Fire(util)