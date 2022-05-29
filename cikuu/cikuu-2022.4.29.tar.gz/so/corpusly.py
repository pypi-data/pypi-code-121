# 2022.3.20 cp from corpusly-es.py ,  for  python -m so.corpusly uvirun ,   load , ..  support both cmd and restapi 
# 2022.2.6  cp from corpusly.py ,  only ES, no redis  | uvicorn corpusly-es:app --host 0.0.0.0 --port 19200 --reload
import json,os,re, requests,traceback,fire, time,math,collections , hashlib
from collections import	defaultdict, Counter

from fastapi import FastAPI, File, UploadFile,Form, Body
from uvirun import * 
app.title = "corpusly-ES"
app.tm = "2022.2.26"

os.environ['eshost'] = 'es.corpusly.com' # tmp , to be removed later 
from so import * 
import en  #from en import * #import en # need 3.1.1
from en import terms,verbnet
from en.dims import essay_to_dims
attach = lambda doc: ( terms.attach(doc), verbnet.attach(doc), doc.user_data )[-1]  # return ssv, defaultdict(dict)

@app.get("/corpus/warmup")
def corpus_warmup():
	return requests.put(f"http://{eshost}:{esport}/_cluster/settings", json={"persistent": {"search.max_buckets": 1000000}}).text

@app.get("/corpus/indexlist/")
def corpus_indexlist(verbose:bool=False):
	''' added 2022.2.7 '''
	names =  [name for name, type, kind in sql("show tables") if not name.startswith(".") and type == 'TABLE' and kind == 'INDEX']
	return {name: dict(sql(f"select type, count(*) cnt from {name} group by type")) for name in names} if verbose else names

@app.post('/corpus/indexdoc')
def indexdoc(arr:dict={"body":"The quick fox jumped over the lazy dog. Justice delayed is justice denied.", "filename":"a.txt"}, idxname:str='testidx', essay_field:str='body', tags_commalist:str='', refresh_index:bool = False):  
	''' arr:  { 'body':, 'filename':  }, optional:  title/tag, ...  updated 2021.11.5 ''' 
	if refresh_index: es.indices.delete(index=idxname)
	if not es.indices.exists(index=idxname): es.indices.create(index=idxname, body=config) 
	filename = arr.get('filename', hashlib.md5(arr.get(essay_field,'').encode(encoding='UTF-8')).hexdigest()) 
	body = arr.get(essay_field,'')
	if not body : return f"empty, on '{essay_field}' found"

	docsnts = spacy.snts(body) 
	for idx, snt in enumerate(docsnts):
		doc = spacy.nlp(snt)
		es.index(index=idxname, id = f"{filename}-{idx}", body= {'type':'snt', 'snt':snt,
				'postag':' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]),
				'src': f"{filename}-{idx}",  'tc': len(doc)})
		ssv = attach(doc) 
		for id, sour in ssv.items():
			sour.update({"src":f"{filename}-{idx}", "filename": filename}) # sid
			es.index(index=idxname, id = f"{filename}-{idx}-{id}", body= sour)

	arr.update( essay_to_dims(body)) # duplicated computing doc 
	arr.update({'type':'doc', "sntnum":len(docsnts), "wordnum": sum([ len(snt) for snt in docsnts]), 'tag': tags_commalist.split(','), 'tm': time.time()})
	es.index(index = idxname,  id = filename, body = arr)
	return docsnts 

@app.post("/corpus/uploadfile/")
async def create_upload_file(index:str="testidx", file: UploadFile = File(...), refresh_index:bool = False):
	''' folder is the index name '''
	content = await file.read()
	return indexdoc({'body':content.decode().strip(), 'index':index, 'filename':file.filename}, idxname=index, refresh_index=refresh_index)  

@app.get("/corpus/sql")
def corpus_sql(query:str="select lem, count(*) cnt  from gzjc where type = 'tok' and pos != 'PUNCT' group by lem order by cnt desc limit 10"):
	return sql(query)

@app.post('/corpus/es_search') 
def es_search(query:dict, type:str='doc', index:str="testidx", size:int=10):  
	''' "query" =  {"match": { "type":"trp"} } , updated 2021.11.5 '''
	return es.search(index=index,  query=query if query else {"match": { "type":type} } if type  else {"match_all": {}}, size=size)

@app.post("/corpus/trp/dep/govs")
def corpus_dep_govs(corpus_list:list, w:str="door", rel:str="dobj_VERB_NOUN"):
	''' ["clec","gzjc"] 
	* door/dobj_VERB_NOUN -> open, close , ...,  2022.2.7	'''
	return { cp: sql(f"select gov, count(*) cnt from {cp} where type ='trp' and rel='{rel}' and dep='{w}' group by gov order by cnt desc") for cp in corpus_list }
@app.post("/corpus/trp/gov/deps")
def corpus_gov_deps(corpus_list:list, w:str="open", rel:str="dobj_VERB_NOUN"):
	''' ["clec","gzjc"] '''
	return {cp: sql(f"select dep, count(*) cnt from {cp} where type ='trp' and rel='{rel}' and gov='{w}' group by dep order by cnt desc") for cp in corpus_list }

@app.get("/corpus/chunk")
def corpus_chunk(lem:str="book", segtype:str='np', cp:str="clec", topk:int=10):
	''' segtype: np/vp/adjp/advp/vtov/vvbg '''
	return sql(f"select chunk, count(*) cnt from {cp} where type = '{segtype}' and lem = '{lem}' group by chunk order by cnt desc limit {topk}")

@app.post("/corpus/lemma/pos")
def corpus_lemma_pos(corpus_list:list, lem:str="book"):
	''' ["clec","gzjc"] '''
	return {cp: sql(f"select pos, count(*) cnt from {cp} where type = 'tok' and lem ='{lem}' and pos != 'PROPN' group by pos") for cp in corpus_list }
@app.post("/corpus/lemma/lex")
def corpus_lemma_lex(corpus_list:list, lem:str="book"):
	''' ["clec","gzjc"] '''
	return {cp: sql(f"select low, count(*) cnt from {cp} where type = 'tok' and low ='{lem}' group by low") for cp in corpus_list }

@app.get("/corpus/tok_head/by_dep")
def corpus_tok_by_dep(cp:str="gzjc", dep:str="dative", topk:int=10):
	''' 'dative' head '''
	return sql(f"select head, count(*) cnt  from {cp} where type = 'tok' and dep = '{dep}' group by head order by cnt desc limit {topk}")

@app.get("/corpus/sum/by_dep")
def corpus_sntsum_by_dep(cp:str="gzjc", dep:str="dative"):
	''' how many 'dative' in current corpus? 
	dep:  dative/xcomp/ccomp/relcl/vprd/csubj/nsubjpass
	'''
	return sql(f"select count(*)  from {cp} where type = 'tok' and dep = '{dep}'" )

@app.get("/corpus/pos/rank")
def corpus_pos_rank(cp:str='clec', pos:str="VERB", topk:int=50):
	''' set pos=None when return all lemmas , POS:VERB/NOUN/ADJ/ADV/None '''
	return sql(f"select lem, count(*) cnt from {cp} where type = 'tok' and pos = '{pos}' group by lem order by cnt desc limit {topk}" ) if pos else sql(f"select lem, count(*) cnt from {cp} where type = 'tok' and pos != 'PUNCT' group by lem order by cnt desc limit {topk}")
@app.post("/corpus/lemmas/cnt")
def corpus_lemmas_cnt(lemmas:list, cp:str='clec', pos:str="VERB"):
	''' ["be","have","get"] '''
	words = ",".join([f"'{lem}'" for lem in lemmas] )
	return sql(f"select lem, count(*) cnt from {cp} where type = 'tok' and pos = 'VERB' and lem in ({words}) group by lem") if pos else sql(f"select lem, count(*) cnt from {cp} where type = 'tok' and lem in ({words}) group by lem")
 
@app.get("/corpus/word/rank")
def corpus_word_rank(cp:str='clec', topk:int=50): return sql(f"select low, count(*) cnt from {cp} where type = 'tok' group by low order by cnt desc limit {topk}" )
@app.get("/corpus/trp/rank")
def corpus_trp_rank(cp:str='clec', rel:str="dobj_VERB_NOUN", topk:int=10): return sql(f"select gov, dep, count(*) cnt from {cp} where type = 'trp' and rel= '{rel}' group by gov,dep order by cnt desc limit {topk}" )
@app.get("/corpus/kwic")
def corpus_kwic(cp:str='clec', w:str="opened", topk:int=10): return sql(f"select snt, postag from {cp} where type = 'snt' and match (snt, '{w}') limit {topk}" )

@app.post("/{cp}/ids")
def corpus_ids(_ids:list, cp:str='gzjc'):  return ids(_ids, cp),

@app.get("/corpus/trp/snts")
def corpus_trp_snts(gov:str='open', rel:str='dobj_VERB_NOUN', dep:str='door', cp:str='clec', topk:int=10): 
	''' snts of trp '''
	rows = sql(f"select src from {cp} where type = 'trp' and gov='{gov}' and rel='{rel}' and dep='{dep}' limit {topk}")
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

@app.get("/corpus/wordlevel")
def corpus_wordlevel(index:str='gzjc', tag:str=None, topk:int=10): 
	''' wordlevel:  awl/gsl1/gsl2/others , added 2021.11.5 '''
	import dic 
	if not hasattr(corpus_wordlevel, 'wordlevel'): corpus_wordlevel.word_level = dic.word_level() 
	rows = sql(f"select low, count(*) from {index} where type = 'tok' group by low")
	return [ (s,i, word_level.get(s.lower(), "others"))  for s,i in rows] if not tag else Counter(dict([ (s,i) for s,i in rows if tag == corpus_wordlevel.word_level.get(s.lower(), "others")])).most_common(topk)

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

class util(object): 
	def __init__(self): pass

	def hello(self):  
		''' show corpuslist '''
		print (  corpus_indexlist() )

	def init(self, idxname):  
		''' init an index '''
		newindex(idxname) 

	def uvirun(self, port) : 
		''' python -m so.corpusly uvirun 80 '''
		uvicorn.run(app, host='0.0.0.0', port=port)

	def load(self, infile, idxname) : 
		''' load text file into index, 
		find . -name "*.txt" -exec python -m so.corpusly load {} inau \;   '''
		with open(infile, 'r',encoding='utf-8') as fp:
			indexdoc({"body": fp.read(), 'filename': infile}, idxname = idxname) 
		print ("finished:", infile ) 

if __name__ == "__main__":  
	fire.Fire(util) 
	#print (indexdoc())