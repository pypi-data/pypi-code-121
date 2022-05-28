# 2022.2.28  cp from esapi.py , | uvicorn exam-api:app --host 0.0.0.0 --port 19200 --reload | include redis-9221, sqlite corpus ,for exam project 
import json,os,re, requests,traceback,fire, time,math,collections , hashlib,sys
from collections import	defaultdict, Counter

from uvirun import * 
app.title = "Exam-api-19200, redis-pika-9221, sqlite-corpus"
app.tm = "2022.2.28"
from so import *

# hash: corpus  = exam01, exam02, ...  Hincrby 
# exam01: set  => {exam01:1
# exam01:1 hash-> {essay: id: snts: 

import redis,spacy,json
from collections import defaultdict, Counter
rhost = "es.corpusly.com"
redis.dsk	= redis.Redis(rhost, port=9221, db=0, decode_responses=True) 
redis.mkf	= redis.Redis(rhost, port=9221, db=1, decode_responses=True) 
redis.dm	= redis.Redis(rhost, port=9221, db=2, decode_responses=True) 
redis.bs	= redis.Redis(rhost, port=9221, db=3, decode_responses=False)
redis.tag	= redis.Redis(rhost, port=9221, db=4, decode_responses=True)
if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.getdoc	= lambda snt: ( bs := redis.bs.get(snt), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setnx(snt, spacy.tobs(doc)) if not bs else None )[1]

#from en import * # need 3.1.1
from en import terms,verbnet
attach = lambda doc: ( terms.attach(doc), verbnet.attach(doc), doc.user_data )[-1]  # return ssv, defaultdict(dict)

@app.get("/corpus/default_tagset")
def corpus_default_tagset(name:str='_tags'): return redis.tag.smembers(name)

@app.get("/corpus/tagtext")
def corpus_tagtext(text:str="The quick fox jumped over the lazy dog. What I think is a box."):
	''' save sent tag '''
	doc = spacy.nlp(text)
	for np in doc.noun_chunks: 
		redis.tag.hset(doc.text, json.dumps([ doc[np.start].idx, doc[np.start].idx + len(np.text), "NP"]),np.text)
		redis.tag.hset(doc[np.start].sent.text, json.dumps([doc[np.start].idx, doc[np.start].idx + len(np.text), "NP"]),np.text)
	#for sent in doc.sents:

@app.get("/corpus/tags")
def corpus_get_tags(text:str="The quick fox jumped over the lazy dog. What I think is a box."):
	''' get tag "classes":["VERB","NOUN","ADJ"] '''
	hkeys = redis.tag.hkeys(text) 
	tags = { json.loads(key)[-1] for key in hkeys if key.startswith('[') }
	#{"entities":[[67,90,"VERB"],[103,117,"NOUN"]]}
	return {"classes":list(tags), "annotations":[ [text, {"entities":[json.loads(key) for key in hkeys if key.startswith('[')]}] ]}

@app.post("/corpus/update_tags")
def corpus_update_tags(arr:dict = {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}],["Really great transaction.",{"entities":[[0,24,"NP2"]]}],["Great price.",{"entities":[[0,11,"NP2"]]}],["",{"entities":[]}]]}):
	''' output of annotator  '''
	try:
		for ann in arr.get("annotations",[]):
			text = ann[0]
			for entit in ann[1].get("entities",[]):
				if entit: 
					redis.tag.hset(text, json.dumps(entit), "")
	except Exception as ex:
		print(">>toes ex:", ex)
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)
	return arr

@app.get('/exam/add_new_essay')
def add_new_essay(topk:int=10):  
	return redis.dsk.zrevrange("rids", 0,topk, True)

@app.post('/exam/update_sent_tags')
def update_sent_tags(snt:str=""):  
	''' '''
	return redis.dsk.zrevrange("rids", 0,topk, True)

@app.get('/exam/add_sent_tag')
def add_sent_tags(snt:str="Hello world", ibeg:int=0, iend:int=1, tag:str="mytag", comment:str=""):  
	''' [1,3,"NP"]  '''
	return redis.tag.hset(snt, json.dumps([ibeg,iend, tag]), comment ) 

@app.get("/corpus/indexlist/")
def corpus_indexlist(verbose:bool=False):
	''' added 2022.2.7 '''
	names =  [name for name, type, kind in rows("show tables") if not name.startswith(".") and type == 'TABLE' and kind == 'INDEX']
	return {name: dict(rows(f"select type, count(*) cnt from {name} group by type")) for name in names} if verbose else names

@app.post('/corpus/indexdoc')
def indexdoc(arr:dict, idxname:str='testidx', essay_field:str='body', tags_commalist:str='', refresh_index:bool = False):  
	''' arr:  { 'body':, 'filename':  }, optional:  title/tag, ...  updated 2021.11.5 ''' 
	if refresh_index: es.indices.delete(idxname)
	if not es.indices.exists(idxname): es.indices.create(idxname, config) 
	filename = arr.get('filename', hashlib.md5(arr.get(essay_field,'').encode(encoding='UTF-8')).hexdigest()) 
	body = arr.get(essay_field,'')
	if not body : return f"empty, on '{essay_field}' found"

	docsnts = snts(body) 
	for idx, snt in enumerate(docsnts):
		doc = nlp(snt)
		es.index(index=idxname, id = f"{filename}-{idx}", body= {'type':'snt', 'snt':snt,
				'postag':'^ ' + ' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]) + ' $',
				'src': f"{filename}-{idx}",  'tc': len(doc)})
		ssv = attach(doc) 
		for id, sour in ssv.items():
			sour.update({"src":f"{filename}-{idx}", "filename": filename}) # sid
			es.index(index=idxname, id = f"{filename}-{idx}-{id}", body= sour)

	es.index(index = idxname,  id = filename, body = {"filename":filename, 'type':'doc',"sntnum":len(docsnts), "wordnum": sum([ len(snt.split()) for snt in docsnts]), 'tag': tags_commalist.split(',')})
	return docsnts 

@app.post("/corpus/uploadfile/")
async def create_upload_file(index:str="testidx", file: UploadFile = File(...), refresh_index:bool = False):
	''' curl -X "POST" "http://es.corpusly.com:19200/corpus/uploadfile/?index=testidx" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@skills.txt;type=text/plain"
	folder is the index name '''
	content = await file.read()
	return indexdoc({'body':content.decode().strip(), 'index':index, 'filename':file.filename}, idxname=index, refresh_index=refresh_index)  

@app.post('/docbase/newdoc')
def new_doc(body:str="There is no compression algorithm in user experience. Justice delayed is justice denied.", idxname:str='docbase', filename:str=None, tags:list=[], refresh_index:bool = False):  
	''' upload a newdoc, to store only, no indexing, 2022.2.26 ''' 
	if refresh_index: es.indices.delete(idxname)
	if not es.indices.exists(idxname): es.indices.create(idxname, config) 
	if not filename: filename = hashlib.md5(body.encode(encoding='UTF-8')).hexdigest() 
	return es.index(index = idxname,  id = filename, body = {"filename":filename, 'type':'doc',"sntnum":len(docsnts), 'tag': tags, 'snts': snts(body) })

@app.get('/sent/terms')
def snt_terms(snt:str="I think that I am going to go swimming."):  
	''' return term for stats, 2022.2.26 ''' 
	try:
		doc = nlp(snt) #doc.user_data["snt"] = snt
		doc.user_data["tok"] = [ {"i": t.i, "text":t.text, "lower":t.text.lower(), "lem":t.lemma_, "pos":t.pos_, "tag":t.tag_, "dep":t.dep_, "head":t.head.i} for t in doc]
		#doc.user_data["trp"] = [ {"i": t.i, "head":t.head.i,  "rel":f"{t.dep_}_{t.head.pos_}_{t.pos_}", "pos":t.pos_, "lem":t.lemma_, "govpos":t.head.pos_, "govlem":t.head.lemma_} for t in doc]
		#doc.user_data['np'] = [{"i":np.start, "chunk":np.text.lower(), "lem":doc[np.end-1].lemma_} for np in doc.noun_chunks] 
		attach(doc) 
		return doc.user_data
	except Exception as ex:
		return  {"ex":str(ex), "snt":snt }

@app.get('/text/doccano')
def text_doccano(text="I think that I am going to go to the cinema. The quick fox jumped over the lazy dog."):  
	''' {"text": "President Obama", "label": [ [10, 15, "PERSON"] ]} 
	https://doccano.github.io/doccano/tutorial/ 
	''' 
	doc = nlp(text) 
	return {"doccano": {"text": text, "label": [ (np.start, np.end, "NP") for np in doc.noun_chunks if np.end - np.start > 1]},
	"tok": [ {"i": t.i, "text":t.text, "text_with_ws": t.text_with_ws, "lem":t.lemma_, "pos":t.pos_, "tag":t.tag_, "dep":t.dep_, "head":t.head.i} for t in doc],
	}

@app.get("/corpus/sql")
def corpus_sql(query:str="select lem, count(*) cnt  from gzjc where type = 'tok' and pos != 'PUNCT' group by lem order by cnt desc limit 10"):
	return rows(query)

@app.post('/corpus/es_search') 
def es_search(query:dict, type:str='doc', index:str="testidx", size:int=10):  
	''' "query" =  {"match": { "type":"trp"} } , updated 2021.11.5 '''
	return es.search(index=index,  query=query if query else {"match": { "type":type} } if type  else {"match_all": {}}, size=size)

@app.post("/corpus/trp/dep/govs")
def corpus_dep_govs(corpus_list:list=["clec","gzjc"], w:str="door", rel:str="dobj_VERB_NOUN"):
	''' ["clec","gzjc"] 
	* door/dobj_VERB_NOUN -> open, close , ...,  2022.2.7	'''
	return { cp: rows(f"select gov, count(*) cnt from {cp} where type ='trp' and rel='{rel}' and dep='{w}' group by gov order by cnt desc") for cp in corpus_list }
@app.post("/corpus/trp/gov/deps")
def corpus_gov_deps(corpus_list:list=["clec","gzjc"], w:str="open", rel:str="dobj_VERB_NOUN"):
	''' ["clec","gzjc"] '''
	return {cp: rows(f"select dep, count(*) cnt from {cp} where type ='trp' and rel='{rel}' and gov='{w}' group by dep order by cnt desc") for cp in corpus_list }

@app.get("/corpus/chunk")
def corpus_chunk(lem:str="book", segtype:str='np', cp:str="clec", topk:int=10):
	''' segtype: np/vp/adjp/advp/vtov/vvbg '''
	return rows(f"select chunk, count(*) cnt from {cp} where type = '{segtype}' and lem = '{lem}' group by chunk order by cnt desc limit {topk}")

@app.post("/corpus/lemma/pos")
def corpus_lemma_pos(corpus_list:list, lem:str="book"):
	''' ["clec","gzjc"] '''
	return {cp: rows(f"select pos, count(*) cnt from {cp} where type = 'tok' and lem ='{lem}' and pos != 'PROPN' group by pos") for cp in corpus_list }
	# rows.query(query="select count(*) from gzjc")

@app.post("/corpus/lemma/lex")
def corpus_lemma_lex(corpus_list:list, lem:str="book"):
	''' ["clec","gzjc"] '''
	return {cp: rows(f"select low, count(*) cnt from {cp} where type = 'tok' and low ='{lem}' group by low") for cp in corpus_list }

@app.get("/corpus/tok_head/by_dep")
def corpus_tok_by_dep(cp:str="gzjc", dep:str="dative", topk:int=10):
	''' 'dative' head '''
	return rows(f"select head, count(*) cnt  from {cp} where type = 'tok' and dep = '{dep}' group by head order by cnt desc limit {topk}")

@app.get("/corpus/sum/by_dep")
def corpus_sntsum_by_dep(cp:str="gzjc", dep:str="dative"):
	''' how many 'dative' in current corpus? 
	dep:  dative/xcomp/ccomp/relcl/vprd/csubj/nsubjpass
	'''
	return rows(f"select count(*)  from {cp} where type = 'tok' and dep = '{dep}'" )

@app.get("/corpus/pos/rank")
def corpus_pos_rank(cp:str='clec', pos:str="VERB", topk:int=50):
	''' set pos=None when return all lemmas , POS:VERB/NOUN/ADJ/ADV/None '''
	return rows(f"select lem, count(*) cnt from {cp} where type = 'tok' and pos = '{pos}' group by lem order by cnt desc limit {topk}" ) if pos else rows(f"select lem, count(*) cnt from {cp} where type = 'tok' and pos != 'PUNCT' group by lem order by cnt desc limit {topk}")
@app.post("/corpus/lemmas/cnt")
def corpus_lemmas_cnt(lemmas:list, cp:str='clec', pos:str="VERB"):
	''' ["be","have","get"] '''
	words = ",".join([f"'{lem}'" for lem in lemmas] )
	return rows(f"select lem, count(*) cnt from {cp} where type = 'tok' and pos = 'VERB' and lem in ({words}) group by lem") if pos else rows(f"select lem, count(*) cnt from {cp} where type = 'tok' and lem in ({words}) group by lem")
 
@app.get("/corpus/word/rank")
def corpus_word_rank(cp:str='clec', topk:int=50): return rows(f"select low, count(*) cnt from {cp} where type = 'tok' group by low order by cnt desc limit {topk}" )
@app.get("/corpus/trp/rank")
def corpus_trp_rank(cp:str='clec', rel:str="dobj_VERB_NOUN", topk:int=10): return rows(f"select gov, dep, count(*) cnt from {cp} where type = 'trp' and rel= '{rel}' group by gov,dep order by cnt desc limit {topk}" )
@app.get("/corpus/kwic")
def corpus_kwic(cp:str='clec', w:str="opened", topk:int=10): return rows(f"select snt, postag from {cp} where type = 'snt' and match (snt, '{w}') limit {topk}" )

@app.post("/{cp}/ids")
def corpus_ids(_ids:list, cp:str='gzjc'):  return ids(_ids, cp),

@app.get("/corpus/trp/snts")
def corpus_trp_snts(gov:str='open', rel:str='dobj_VERB_NOUN', dep:str='door', cp:str='clec', topk:int=10): 
	''' snts of trp '''
	rows = rows(f"select src from {cp} where type = 'trp' and gov='{gov}' and rel='{rel}' and dep='{dep}' limit {topk}")
	sql	= {
    "query": {
        "ids" : {
            "type" : "_doc",
            "values" : [row[0] for row in rows] #clec:snt-34993,  clec:snt-32678
			}
		}
	}
	return requests.post(f"http://{eshost}:{esport}/{cp}/_search/", json=sql).json()

@app.get("/corpus/match_phrase")
def corpus_match_phrase(phrase:str='opened the box', cp:str='clec', topk:int=10):  return match_phrase(phrase, cp, topk)
@app.get("/corpus/match_phrase_num")
def corpus_phrase_num(phrase:str='opened the box', cp:str='clec', topk:int=10): return phrase_num(phrase, cp, topk)["hits"]["total"]["value"]

@app.post("/corpus/mf")
def corpus_mf(corpus_list:list, input:str="consider", type:str='lemma'):
	''' ["gzjc","clec"] ,  type:lemma/phrase '''
	return {cp: round(1000000 * es.lemnum(input, cp) / (es.sntnum(cp)+0.1), 2 ) for cp in corpus_list} if type =='lemma' else {cp: round(1000000 * es.phrase_num(input, cp) / (es.sntnum(cp)+0.1), 2 ) for cp in corpus_list}

@app.get("/corpus/nearby")
def corpus_nearby(lem:str="environment", corpus:str='spin', poslist:str="'NOUN','ADJ','VERB'", topk:int=20):
	''' words nearby '''
	rows = requests.post(f"http://{eshost}:{esport}/_sql",json={"query": f"select src from {corpus} where type = 'tok' and lem = '{lem}'"}).json()['rows']
	snts = "','".join([row[0] for row in rows])
	res = requests.post(f"http://{eshost}:{esport}/_sql",json={"query": f"select lem from {corpus} where type = 'tok'  and pos in ({poslist}) and src in ('{snts}')" }).json()['rows']
	si = Counter() 
	[si.update({row[0]:1}) for row in res if row[0] != lem and not row[0] in spacy.stoplist ]
	return Counter({ s:i * spacy.wordidf.get(s, 0) for s,i in si.items()}).most_common(topk)

import dic 
word_level = dic.word_level() 
@app.get("/corpus/wordlevel")
def corpus_wordlevel(index:str='gzjc', tag:str=None, topk:int=10): 
	''' wordlevel:  awl/gsl1/gsl2/others , added 2021.11.5 '''
	rows = rows(f"select low, count(*) from {index} where type = 'tok' group by low")
	return [ (s,i, word_level.get(s.lower(), "others"))  for s,i in rows] if not tag else Counter(dict([ (s,i) for s,i in rows if tag == word_level.get(s.lower(), "others")])).most_common(topk)

@app.get("/text/wordidf")
def text_wordidf(text:str="The quick fox jumped over the lazy dog. Justice delayed is justice denied."): 
	''' 2022.2.26 '''
	from dic import word_idf 
	doc = nlp(text)
	si = Counter()
	[si.update({t.text.lower():1}) for t in doc if t.text.lower() in word_idf.word_idf]
	return [ (s, i, word_idf.word_idf[s])  for s,i in si.items()]

@app.get('/corpus/hybchunk')
def corpus_hybchunk(hyb:str='the _NNS of', index:str='gzjc', size:int=-1, topk:int=10):
	''' the _NNS of -> {the books of: 13, the doors of: 7} , added 2021.10.13 '''
	return hybchunk(hyb, index, size, topk)

@app.get('/corpus/truncate_index')
def truncate_index(index:str='testidx'):
	return requests.post(f"http://{eshost}:{esport}/{index}/_delete_by_query?conflicts=proceed", json={"query": { "match_all": {} }}).json()
@app.get('/corpus/delete_file')
def delete_file(filename:str, index:str='testidx'):
	return requests.post(f"http://{eshost}:{esport}/{index}/_delete_by_query?conflicts=proceed", json={"query": { "match": { "filename": filename} }}).json()

@app.post('/corpus/dualarr_keyness')
def dualarr_keyness(src:dict, tgt:dict, sum1:float=None, sum2:float=None, threshold:float=0.0, leftonly:bool=False): 
	'''  "src": {"one":2, "two":12}, "tgt": {"three":3, "one":1}, added 2021.10.24  '''
	if not sum1: sum1 = sum([i for s,i in src.items()])
	if not sum2: sum2 = sum([i for s,i in tgt.items()])
	words = set(src.keys()) | set(tgt.keys()) if not leftonly else set(src.keys())
	res  = [(w, src.get(w,0), tgt.get(w,0), sum1, sum2, likelihood(src.get(w,0.01), tgt.get(w,0.01), sum1, sum2))  for w in words]
	res.sort(key=lambda a:a[-1], reverse=True)
	return [ar for ar in res if abs(ar[-1]) > threshold ]

@app.post('/corpus/txtkeyness')
def text_keyness(txt:str= Form(...), pos:str='VERB', corpus:str='inau', skip_NNP:bool=True, threshold:float=0.0): 
	''' keyness of (txt, corpus), pos:LEX/VERB/NOUN, added 2021.10.16  '''
	src = dict(requests.post(f"http://spacy.wrask.com/nlp/lexcnt", json={'txt':txt, 'pos':pos,'skip_NNP':skip_NNP}).json())
	tgt = dict(requests.post(f"http://{eshost}:{esport}/_sql",json={"query": f"select lem, count(*) from {corpus} where type = 'tok' and pos='{pos}' group by lem"}).json()['rows'])
	return dualarr_keyness(src, tgt, threshold) 

@app.get('/corpus/dualsql_keyness')
def text_keyness(sql1:str= "select lem,  count(*) from inau where type = 'tok' and pos='VERB' and filename in ('1989-Bush.txt')  group by lem", sql2:str="select lem,  count(*) from inau where type = 'tok' and pos='VERB' group by lem", threshold:float=0.0): 
	''' keyness of sql1, sql2, added 2021.10.24  '''
	src = dict(requests.post(f"http://{eshost}:{esport}/_sql",json={"query": sql1}).json()['rows'])
	tgt = dict(requests.post(f"http://{eshost}:{esport}/_sql",json={"query": sql2}).json()['rows'])
	return dualarr_keyness(src, tgt, threshold) 

@app.get('/sqles/count_of_item')
def sqles_si_group(q:str="SELECT triple.gov FROM sentnest where corpus='gzjc' and triple.rel = 'dobj_VERB_NOUN' and triple.dep='door'", es_host:str="127.0.0.1:{esport}", topk:int=None):
	''' SELECT tok.pos FROM sentnest where tok.lem = 'sound' ,2021.10.18 '''
	si = Counter()
	res = requests.post(f"http://{es_host}:{esport}/_sql", json={"query":q}).json()
	[ si.update({word:1}) for word, in res['rows'] ]
	return si.most_common(topk)

@app.get('/corpus/init_index')
def init_index(idxname:str='testidx'):  newindex(idxname)

if __name__ == "__main__":  
	uvicorn.run(app, host='0.0.0.0', port=19200)

'''
conn.execute(f'CREATE TABLE IF NOT EXISTS {self.tablename} (key varchar(512) PRIMARY KEY, value blob)')
conn.execute('REPLACE	INTO spacybs (key,	value) VALUES (?,?)' % self.tablename,	(key, value))

conn.execute(f'CREATE TABLE IF NOT EXISTS ssi (s varchar(128) PRIMARY KEY, i int)')

stype ( ID INTEGER PRIMARY KEY   AUTOINCREMENT, sid integer, tag varchar(100), comment varhcar(256)  
spantag ( ID INTEGER PRIMARY KEY   AUTOINCREMENT, sid integer,  ibeg int, iend int , tag varchar(128), comment varhcar(256) )
doc (did INTEGER PRIMARY KEY   AUTOINCREMENT, title varchar(256), doc mediumtext not null, tags varchar(256), tm timestamp ) without rowid
snt ( sid INTEGER PRIMARY KEY   AUTOINCREMENT, did integer,  snt text )   

'''

@app.get("/corpus/default_tagset")
def corpus_default_tagset(name:str='_tags'): return redis.tag.smembers(name)

@app.get("/corpus/tagtext")
def corpus_tagtext(text:str="The quick fox jumped over the lazy dog. What I think is a box."):
	''' save sent tag '''
	doc = spacy.nlp(text)
	for np in doc.noun_chunks: 
		redis.tag.hset(doc.text, json.dumps([ doc[np.start].idx, doc[np.start].idx + len(np.text), "NP"]),np.text)
		redis.tag.hset(doc[np.start].sent.text, json.dumps([doc[np.start].idx, doc[np.start].idx + len(np.text), "NP"]),np.text)
	#for sent in doc.sents:

@app.get("/corpus/tags")
def corpus_get_tags(text:str="The quick fox jumped over the lazy dog. What I think is a box."):
	''' get tag "classes":["VERB","NOUN","ADJ"] '''
	hkeys = redis.tag.hkeys(text) 
	tags = { json.loads(key)[-1] for key in hkeys if key.startswith('[') }
	#{"entities":[[67,90,"VERB"],[103,117,"NOUN"]]}
	return {"classes":list(tags), "annotations":[ [text, {"entities":[json.loads(key) for key in hkeys if key.startswith('[')]}] ]}

@app.post("/corpus/update_tags")
def corpus_update_tags(arr:dict = {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}],["Really great transaction.",{"entities":[[0,24,"NP2"]]}],["Great price.",{"entities":[[0,11,"NP2"]]}],["",{"entities":[]}]]}):
	''' output of annotator  '''
	try:
		for ann in arr.get("annotations",[]):
			text = ann[0]
			for entit in ann[1].get("entities",[]):
				if entit: 
					redis.tag.hset(text, json.dumps(entit), "")
	except Exception as ex:
		print(">>toes ex:", ex)
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)
	return arr
