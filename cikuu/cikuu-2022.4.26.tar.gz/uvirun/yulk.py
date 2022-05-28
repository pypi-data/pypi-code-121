# 2022.3.3  for yulk.sentbase.com  | uvicorn yulk:app --host 0.0.0.0 --port 18001 --reload
import json,requests,hashlib,os
from uvirun import * 
#from en import nlp, snts
import en

from collections import	defaultdict, Counter
from dic.bnc_wordlist import * 
@app.get('/yulk/keyness')  #def bnc_keyness(si:dict, si_sum:int=None):
def text_keyness(text="I think that I am going to go to the cinema. The quick fox jumped over the lazy dog.", topk:int=20):  
	''' 单词超用显著性 ''' 
	doc = spacy.nlp(text) 
	si = Counter()
	[ si.update({t.lemma_:1}) for t in doc if not t.pos_ in ('PROPN','PUNCT') and not t.is_stop]
	res = bnc_keyness(dict(si), len(doc))
	res.sort(key=lambda x:x[-1], reverse=True)
	return res[0:topk]

from dic.word_idf import word_idf
wordidf = lambda txt:  (si := Counter(), [ si.update({word_idf[t.text.lower()]: 1}) for t in spacy.nlp(txt) if t.text.lower() in word_idf] )[0]
@app.get('/yulk/vs/wordidf') 
def vs_wordidf(text0="I think that I am going to go to the cinema. The quick fox jumped over the lazy dog.", text1="The reality that has blocked my path to become the typical successful student is that engineering and the liberal arts simply don't mix as easily as I assured in hight school.",):  
	''' 单词难度对比 ''' 
	si0 = wordidf(text0)
	si1 = wordidf(text1)
	return (si0, si1)

@app.post('/yulk/wordmap') 
def wordmap(snts:list=["I think that I am going to go to the cinema.","The quick fox jumped over the lazy dog."], poslist:str="VERB,NOUN,ADV,ADJ"):  
	''' 语义邻居 ''' 
	ssi = defaultdict(Counter)
	pos = poslist.strip().split(',')
	for snt in snts:
		doc = spacy.nlp(snt) 
		[ ssi[t.pos_].update({t.lemma_:1})  for t in doc if t.pos_ in pos]
	return ssi 

from en.spacybs import Spacybs
db = Spacybs("essaytag.sqlite") # support es ops # db.close()
db.conn.execute(f"CREATE TABLE IF NOT EXISTS doc (did INTEGER PRIMARY KEY AUTOINCREMENT, title varchar(256), body mediumtext not null, note text not null default '', tm timestamp )")
db.conn.execute(f"CREATE TABLE IF NOT EXISTS snt ( sid varchar(32) PRIMARY KEY, snt text )") # 1001-1, 1001-2, ...
db.conn.execute(f'''CREATE VIRTUAL TABLE if not exists fts USING fts5(sid, snt, terms, columnsize=0, detail=full,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''') #self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=none,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''')
db.conn.execute(f'CREATE TABLE IF NOT EXISTS tok (sid varchar(16), i int, text varchar(64), lem varchar(64), pos varchar(16), tag varchar(16), dep varchar(16), head int)') 
db.conn.execute(f'CREATE TABLE IF NOT EXISTS trp (sid varchar(16), i int, rel varchar(32), govlem varchar(64), govpos varchar(16), deplem varchar(64), deppos varchar(16))') 
db.conn.execute(f'CREATE TABLE IF NOT EXISTS chk (sid varchar(16), start int not null, end int not null, chunk varchar(128) , type varchar(32), lem varchar(64))') 
db.conn.execute(f"CREATE UNIQUE INDEX if not exists trpidx ON trp (sid,i)") #CREATE UNIQUE INDEX index_name on table_name (column_name);
db.conn.execute(f"CREATE UNIQUE INDEX if not exists chkidx ON chk (sid, start)")
db.conn.execute(f"CREATE UNIQUE INDEX if not exists tokidx ON tok (sid,i)")
db.conn.execute(f"CREATE TABLE IF NOT EXISTS tag_stype ( sid varchar(32),  stype varchar(32), note varhcar(256), tm timestamp)")
db.conn.execute(f"CREATE TABLE IF NOT EXISTS tag_span ( sid varchar(32), ibeg int not null, iend int not null, tag varchar(128) not null, note varhcar(256) not null default '', tm timestamp)")
db.conn.execute(f"CREATE TABLE IF NOT EXISTS tag_cate ( cate varchar(32), tag varchar(32) not null, note varhcar(256) not null default '')")
db.conn.execute(f"CREATE UNIQUE INDEX if not exists tag_stypeidx ON tag_stype (sid,stype)")
db.conn.execute(f"CREATE UNIQUE INDEX if not exists tag_spanidx ON tag_span (sid,ibeg, iend)")
db.conn.execute(f"CREATE UNIQUE INDEX if not exists tag_tagidx ON tag_cate (cate, tag)")
db.conn.commit()

@app.get("/yulk/essaytag/clear")
def essaytag_clear():
	''' '''
	for name in ("doc","snt","tok","trp","chk", "fts", "tag_stype","tag_span", "tag_cate"):
		db.conn.execute(f"drop table if exists {name}")
	return db.conn.commit()

@app.get("/yulk/essaytag/newdoc")
def add_text(text:str="The quick fox jumped over the lazy dog. The justice delayed is justice denied.", title:str=None, note:str=""):
	''' prefix: my/tag '''
	cursor=db.conn.cursor()
	docsnts = spacy.snts(text,False)
	if not title: title = docsnts[0]
	cursor.execute(f'INSERT INTO doc(title,body,note) VALUES (?,?,?)',(title, text, note))
	id = cursor.lastrowid
	for i, snt in enumerate(docsnts):
		doc = spacy.nlp(snt)
		db[snt] = tobs(doc)
		cursor.execute(f'INSERT or ignore INTO snt(sid, snt) VALUES (?,?)',(f"{id}-{i}",snt))
		for t in doc: 
			cursor.execute(f'INSERT or ignore INTO tok(sid, i, text, lem, pos, tag, dep, head) VALUES (?,?,?,?,?,?,?,?)',(f"{id}-{i}", t.i,	t.text, t.lemma_, t.pos_, t.tag_, t.dep_, t.head.i))
			cursor.execute(f'INSERT or ignore INTO trp(sid, i, rel, govpos, govlem, deppos, deplem) VALUES (?,?,?,?,?,?,?)',(f"{id}-{i}", t.i,	t.dep_, t.head.pos_, t.head.lemma_, t.pos_, t.lemma_))
		for np in doc.noun_chunks: 
			cursor.execute(f'INSERT or ignore INTO chk(sid, start, end, chunk, type, lem) VALUES (?,?,?,?,?,?)',(f"{id}-{i}", np.start, np.end, np.text, "np", doc[np.end-1].lemma_))
	db.conn.commit()
	return id 


class util(object): 
	def __init__(self): pass 

	def uvirun(self, port) : 
		''' python -m uvirun.yulk uvirun 18001 '''
		uvicorn.run(app, host='0.0.0.0', port=port)

if __name__ == '__main__':
	import fire
	fire.Fire(util)
	#print(add_text(), flush=True)
	#uvicorn.run(app, host='0.0.0.0', port=80)