#2022.2.17   python -m en.annotate uvirun 8000
import json, spacy, fastapi,uvicorn , os, fire,hashlib,time
from collections import	Counter,defaultdict

app	= fastapi.FastAPI()
@app.get('/')
def home(): return fastapi.responses.HTMLResponse(content=f"<h2>wps api</h2><a href='/docs'> docs </a> | <a href='/redoc'> redoc </a><br>uvicorn wps:app --port 80 --host 0.0.0.0 --reload <br><br>2022.3.23")

@app.get("/en/sntbr")
def en_sntbr(text:str="The quick fox jumped over the lazy dog. It is ok.", trim:bool=True):	return spacy.snts(text, trim) 

@app.get('/en/esdoc')
def esdoc(text:str="The quick fox jumped over the lazy dog. Justice delayed is justice denied.", did:str=None):  
	''' arr:  { 'body':, 'filename':  }, optional:  title/tag, ...  updated 2021.11.5 ''' 
	if did is None : did = hashlib.md5(text.encode("utf-8")).hexdigest()
	doc = spacy.nlp(text)
	return index_doc(did, doc) 

def annotate_doc(did, doc): 
	'''  return ssv '''
	ssv = defaultdict(dict) 
	for np in doc.noun_chunks:
		ssv[f"{did}-NP-{doc[np.start].idx}"].update({"type":"span-NP", "ibeg": doc[np.start].idx, "iend": doc[np.start].idx + len(np.text), "tag": "NP", "chunk": np.text})
	for name, ibeg,iend in terms.matchers['ap'](doc) :
		ssv[f"{did}-AP-{doc[ibeg].idx}"].update({"type":"span-AP", "ibeg": doc[ibeg].idx, "iend": doc[ibeg].idx + len(doc[ibeg:iend].text), "tag": "AP", "chunk": doc[ibeg:iend].text})
	for name, ibeg,iend in terms.matchers['vp'](doc) :
		ssv[f"{did}-VP-{doc[ibeg].idx}"].update({"type":"span-VP", "ibeg": doc[ibeg].idx, "iend": doc[ibeg].idx + len(doc[ibeg:iend].text), "tag": "VP", "chunk": doc[ibeg:iend].text})

	# VERB: VBD/VBP/VBG
	[ ssv[f"{did}-{t.pos_}-{t.idx}"].update({"type":f"span-{t.pos_}", "ibeg": t.idx, "iend": t.idx + len(t.text), "tag": t.pos_, "chunk": t.text}) for t in doc if t.pos_ in ["VERB","NOUN","ADJ","ADV"] ]

	# clause
	for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
		children = list(v.subtree)
		start = children[0].i  	#end = children[-1].i 
		cl = " ".join([c.text for c in v.subtree])
		ssv[f"{did}-clause-{doc[start].idx}"].update({"type":"span-clause", "ibeg": doc[start].idx, "iend":doc[start].idx + len(cl), "tag":v.dep_, "chunk":cl})

	#non_pred_verb
	[ ssv[f"{did}-non_pred_verb-{t.tag_}-{t.idx}"].update({"type":f"span-non_pred_verb","ibeg": t.idx , "iend": t.idx + len(t.text) , "tag": t.tag_, "chunk": t.text}) for t in doc if t.tag_ == 'VBN']
	for name, ibeg,iend in terms.matchers['vtov'](doc) :
		ssv["{did}-non_pred_verb-vtov-{doc[ibeg].idx}"].update({"type":f"span-non_pred_verb-vtov","ibeg": doc[ibeg].idx, "iend":doc[ibeg].idx + len(doc[ibeg:iend].text), "tag":"vtov", "chunk": doc[ibeg:iend].text})
	for name, ibeg,iend in terms.matchers['vvbg'](doc) :
		ssv["{did}-non_pred_verb-vvbg-{doc[ibeg].idx}"].update({"type":f"span-non_pred_verb-vvbg","ibeg": doc[ibeg].idx, "iend":doc[ibeg].idx + len(doc[ibeg:iend].text),"tag": "vvbg","chunk":doc[ibeg:iend].text})

	# stype
	for idx, sent in enumerate(doc.sents):
		sdoc = sent.as_doc()
		if sdoc.text.strip() == '' : continue #added 2022.3.11
		stype = "simple" if len([t for t in sdoc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "complex" 
		ssv["{did}-stype-{idx}-simple-or-complex"].update({"i": idx, "type":"span-stype", "ibeg":doc[sent.start].idx, "iend":doc[sent.start].idx+ len(sent.text), "tag": stype, "chunk": sent.text})
		if len([t for t in sdoc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0:
			ssv["{did}-stype-{idx}-compound"].update({"i": idx, "type":"span-stype", "ibeg":doc[sent.start].idx, "iend":doc[sent.start].idx + len(sent.text), "tag": "compound", "chunk": sent.text})
	return ssv

@app.get('/en/annotate') # use ES to store the tag data 
def annotate(text:str="Tom thinks that he will go to the cinema. What I think is right.", did:str=None): 
	'''  return ssv '''
	if did is None : did = hashlib.md5(text.encode("utf-8")).hexdigest()
	doc = spacy.nlp(text) 
	return annotate_doc(did, doc) 

class util(object): 
	def __init__(self): pass 

	def hello(self):
		print (annotate()) 

	def uvirun(self, port) : 
		''' python -m en uvirun 19000 '''
		uvicorn.run(app, host='0.0.0.0', port=port)

	def load(self, infile, idxname) : 
		''' load text file into db  '''
		with open(infile, 'r',encoding='utf-8') as fp:
			add_newdoc(infile, fp.read() )
		print ("finished:", infile ) 

if __name__ == '__main__':
	fire.Fire(util)

'''
https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html

curl -X POST "localhost:9200/_bulk?pretty" -H 'Content-Type: application/json' -d '
{ "index" : { "_index" : "test", "_id" : "1" } }
{ "field1" : "value1" }
{ "delete" : { "_index" : "test", "_id" : "2" } }
{ "create" : { "_index" : "test", "_id" : "3" } }
{ "field1" : "value3" }
{ "update" : {"_id" : "1", "_index" : "test"} }
{ "doc" : {"field2" : "value2"} }
'

PUT my-index-000001/_doc/1
{
  "@timestamp": "2099-11-15T13:12:00",
  "message": "GET /search HTTP/1.1 200 1070000",
  "user": {
    "id": "kimchy"
  }
}

@app.get('/en/esdoc')
def esdoc(text:str="The quick fox jumped over the lazy dog. Justice delayed is justice denied.", did:str=None):  
	# arr:  { 'body':, 'filename':  }, optional:  title/tag, ...  updated 2021.11.5 
	if did is None : did = hashlib.md5(text.encode("utf-8")).hexdigest()
	dic = {}
	snts = spacy.snts(text)
	docs = [spacy.getdoc(snt) for snt in snts]
	dims = docs_to_dims(snts, docs)
	dims.update({'type':'doc', "sntnum":len(snts), "wordnum": sum([ len(snt) for snt in snts]), 'tm': time.time()})
	dic[did] = dims 

	for idx, doc in enumerate(docs):
		dic[f"{did}-{idx}"] = {'type':'snt', 'snt':snts[idx], 'pred_offset': en.pred_offset(doc), 
				'postag':' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]),
				'src': f"{did}-{idx}",  'tc': len(doc)} # src = sentid 
		ssv = attach(doc) 
		for id, sour in ssv.items():
			sour.update({"src":f"{did}-{idx}"}) # sid
			dic[f"{did}-{idx}-{id}"] = sour
	return dic

'''