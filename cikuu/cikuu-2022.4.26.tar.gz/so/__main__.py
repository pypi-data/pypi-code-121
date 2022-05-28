# 2022-2-13  cp from cikuu/bin/es.py 
import json,fire,sys, os, hashlib ,time 
import warnings
warnings.filterwarnings("ignore")

def index_doc(did, doc):  
	''' arr: additional attr, such as filename , '''
	import en  
	from en import terms,verbnet
	from en.dims import docs_to_dims
	attach = lambda doc: ( terms.attach(doc), verbnet.attach(doc), doc.user_data )[-1]  # return ssv, defaultdict(dict)

	arr  = {} #{"did": did}
	snts = [snt.text for snt in doc.sents]
	docs = [snt.as_doc() for snt in doc.sents] #spacy.getdoc(snt)

	if len(docs) > 1 : # at least 2 snts will be treated as a document
		dims = docs_to_dims(snts, docs)
		dims.update({'type':'doc', "sntnum":len(snts), "wordnum": sum([ len(snt) for snt in snts]), 'tm': time.time()})
		arr[did] = dims 

	for idx, sdoc in enumerate(docs):
		arr[f"{did}-{idx}"] = {'type':'snt', 'snt':snts[idx], 'pred_offset': en.pred_offset(sdoc), 
				'postag':' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in sdoc]),
				'src': f"{did}-{idx}",  'tc': len(sdoc)} # src = sentid 
		ssv = attach(sdoc) 
		for id, sour in ssv.items():
			sour.update({"src":f"{did}-{idx}"}) # sid
			arr[f"{did}-{idx}-{id}"] = sour
	return arr

from so import * 
class ES(object):
	def __init__(self, host='127.0.0.1',port=9200): 
		self.es = Elasticsearch([ f"http://{host}:{port}" ])  

	def addfolder(self, folder:str, pattern=".txt", idxname=None): 
		''' folder -> docbase, 2022.1.23 '''
		if idxname is None : idxname=  folder
		print("addfolder started:", folder, idxname, self.es, flush=True)
		if not self.es.indices.exists(index=idxname): self.es.indices.create(index=idxname, body=config)
		for root, dirs, files in os.walk(folder):
			for file in files: 
				if file.endswith(pattern):
					self.add(f"{folder}/{file}", idxname = idxname) 
					print (f"{folder}/{file}", flush=True)
		print("addfolder finished:", folder, idxname, self.es, flush=True)

	def annotate(self, infile, idxname): 
		''' 2022.3.24 '''
		from en import esjson
		print("annotate started:", infile, idxname, self.es, flush=True)
		if not self.es.indices.exists(idxname): self.es.indices.create(idxname, config)

		text = open(infile,'r').read().strip()
		ssv  = esjson.annotate(text ) 
		for id, sv in ssv.items(): 
			self.es.index(index = idxname, id = id, body = sv)
		print("annotate finished:", infile,idxname)

	def add(self, infile, idxname="testdoc"):
		''' add doc only , 2022.3.25 '''
		if not self.es.indices.exists(index=idxname): self.es.indices.create(index=idxname, body=config)
		start = time.time()
		text = open(infile, 'r').read().strip() 
		did	 = hashlib.md5(text.encode("utf8")).hexdigest()
		self.es.index(index=idxname, body={"doc":text,  "filename": infile, 'type':'doc'}, id = did)
		ssv  = index_doc(did, spacy.nlp(text))
		for id, sv in ssv.items(): 
			try:
				self.es.index(index = idxname, id = id, body = sv)
			except Exception as ex:
				print(">>add ex:", ex, id, sv)
		print(f"{infile} is finished, \t| using: ", time.time() - start) 

	def loadsnt(self, infile, idxname=None):
		''' add doc only , 2022.3.25 '''
		if idxname is None : idxname = infile.split('.')[0] 
		if not self.es.indices.exists(index=idxname): self.es.indices.create(index=idxname, body=config)
		start = time.time()
		for idx, line in enumerate(open(infile, 'r').readlines()): 
			ssv  = index_doc(idx, spacy.nlp(line.strip()))
			for id, sv in ssv.items(): 
				try:
					self.es.index(index = idxname, id = id, document = sv) #https://github.com/elastic/elasticsearch-py/issues/1698
				except Exception as ex:
					print(">>add ex:", ex, id, sv)
		print(f"{infile} is finished, \t| using: ", time.time() - start) 

	def sntvec(self, idxname): 
		''' add snt vec into snt, 2022.3.25 
		python -m so sntvec testdoc
		pip install -U sentence-transformers
		'''
		from sentence_transformers import SentenceTransformer
		if not hasattr(fire, 'model'): 
			fire.model = SentenceTransformer('all-MiniLM-L6-v2')
			print ("model loaded:", fire.model, flush=True)

		print("sntvec started:", idxname, flush=True) 
		for doc in helpers.scan(client=self.es, query={"query" : {"match" : {"type":"snt"}} }, index=idxname):
			sid	= doc['_id']
			snt	= doc['_source']['snt']
			vec	= fire.model.encode(snt.strip()).tolist()
			print (sid, snt, len(vec))
			self.es.index(index=idxname, body={"_snt":snt,  "sntvec": vec, 'type':'sntvec'}, id = f"{sid}-sntvec")
		print("sntvec finished:", idxname) 

	def vecso(self, idxname, snt): 
		''' search with snt vec, 2022.3.27	'''
		from sentence_transformers import SentenceTransformer
		if not hasattr(fire, 'model'):  fire.model = SentenceTransformer('all-MiniLM-L6-v2')
		vec	= fire.model.encode(snt.strip()).tolist()
		res = self.es.search(index=idxname, body={
  "query": {
    "script_score": {
      "query": {
        "match_all": {}
      },
      "script": {
        "source": "cosineSimilarity(params.query_vector, 'sntvec') + 1.0",
        "params": {
          "query_vector": vec
        }
      }
    }
  }
}
)
		print (res) 

	def propbank(self, idxname): 
		'''  add flair semantic tag into snt, 2022.3.25
		python -m so propbank testdoc
		'''
		from flair.models import SequenceTagger
		from flair.tokenization import SegtokSentenceSplitter
		from flair.data import Sentence
		if not hasattr(fire, 'tagger'): 
			fire.tagger = SequenceTagger.load('frame-fast')  # 115M 
			print ("flair tagger loaded:", fire.tagger, flush=True)

		print("propbank started:", idxname, flush=True) 
		for doc in helpers.scan(client=self.es, query={"query" : {"match" : {"type":"snt"}} }, index=idxname):
			try:
				sid	= doc['_id']
				snt = Sentence(doc['_source']['snt']) #George returned to Berlin to return his hat.
				fire.tagger.predict(snt)
				self.es.index(index=idxname, body={"src":sid, 'chunk': snt.to_tagged_string(), 'type':'propbank-snt'}, id = f"{sid}-propbank")
				for sp in snt.get_spans():  # tag = return.01 
					self.es.index(index=idxname, body={"src":sid,  "lem": sp.tag.split('.')[0],  "tag": sp.tag, 'lex': sp.text, 'ibeg':sp.start_pos, 'iend': sp.end_pos, 'offset': int(sp.position_string), 'type':'propbank'}, id = f"{sid}-propbank-{sp.position_string}")
			except Exception as ex:
				print ("propbank ex:", ex, doc )
		print("propbank finished:", idxname) 
	
	def init(self, idxname):
		''' init a new index '''
		if self.es.indices.exists(index=idxname):self.es.indices.delete(index=idxname)
		self.es.indices.create(index=idxname, body=config) #, body=snt_mapping
		print(">>finished " + idxname )

	def clear(self,idxname): self.es.delete_by_query(index=idxname, body={"query": {"match_all": {}}})
	def dumpid(self, idxname): [print (doc['_id'] + "\t" + json.dumps(doc['_source']))  for doc in helpers.scan(self.es,query={"query": {"match_all": {}}}, index=idxname)]
	def dump(self, idxname): [print (json.dumps(doc))  for doc in helpers.scan(self.es,query={"query": {"match_all": {}}}, index=idxname)]
	def keys(self, idxname): [print(resp['_id']) for resp in  helpers.scan(client=self.es, query={"query" : {"match_all" : {}}}, scroll= "10m", index= idxname , timeout="10m") ]
	def hello(self): print (self.es)

	def load(self, infile, idxname, batch=100000): 
		''' python3 -m so load essaydm.json essaydm 
		load id-source-file into index, 2022.4.2 '''
		print(">>started: " , infile, idxname, flush=True )
		actions=[]
		for line in readline(infile): 
			try:
				arr = json.loads(line) 
				#arr.update({'_op_type':'index', '_index':idxname,}) 
				actions.append( {'_op_type':'index', '_index':idxname, '_id': arr.get('_id',None), '_source': arr.get('_source',{}) } )
				if len(actions) > batch: 
					helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
					print ( actions[-1], flush=True)
					actions = []
			except Exception as e:
				print("ex:", e)	
		if actions : helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
		print(">>finished " , infile, idxname )

if __name__ == '__main__':
	fire.Fire(ES)

def test(): #https://elasticsearch-py.readthedocs.io/en/master/
	doc = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    'timestamp': '2020-6-24',}
	res = es.index(index="test-index", id=2, body=doc)
	print("result", res['result'])

	res = es.get(index="test-index", id=1)
	print(res['_source'])

	es.indices.refresh(index="test-index")

	res = es.search(index="test-index", body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total']['value'])
	for hit in res['hits']['hits']:
		print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])


def submit(jsonfile, idxname ='docsim', host='127.0.0.1', id='eid'):
	''' {"eid": "1", "rid": "1419931", "uid": "19704146", "snts": ["Next Monday, a foreign friend will come to meet me.", "I want to give him some representative gifts.", "The 
first thing I want to send is tea.", "The tea culture in Sichuan is very deep.", "On the one hand, Sichuan tea has a strong aroma and a good taste.", "On the other hand
, tea also reflects the relaxed and elegant life culture of Sichuan people.", "The second thing I want to send is the hot pot bottom.", "It is a very symbolic symbol of
 Sichuan.", "Also reflects the food culture of Scihua"]} '''
	print(r, infile, host, idxname, flush=True)
	es = Elasticsearch([host]) 
	file = open(infile, 'r')
	while True:
		line = file.readline()
		if not line: break; 
		try:
			arr = json.loads(line.strip())
			eid = arr[id]
			del arr[id]
			es.index(index=idxname, id=eid, body=arr)
		except Exception as e:# skip those speical keys 
			print("ex:", e)	
	file.close()
	print(">> finished:", infile, flush=True)

def submit_batch(jsonfile, idxname ='sntsim', es_host='127.0.0.1', id='eid', batch=100000):
	from elasticsearch import helpers
	print(r, infile, es_host, idxname, flush=True)
	es = Elasticsearch([es_host]) 
	actions=[]
	file = open(infile, 'r')
	while True:
		line = file.readline()
		if not line: break; 
		try:
			arr = json.loads(line.strip())
			eid = arr[id]
			del arr[id]
			actions.append({'_op_type':'index', '_index':idxname, '_id':eid , '_source':d})
			if len(actions) > 0  : 
				helpers.bulk(client=es,actions=actions, raise_on_error=False)
				actions=[]					
		except Exception as e:# skip those speical keys 
			print("ex:", e)	
	file.close()
	if len(actions) > 0  : 
		helpers.bulk(client=es,actions=actions, raise_on_error=False)
	print(">> finished:", infile, flush=True)


'''
 "mappings": {
    "_source": {
      "includes": [
        "*.count",
        "meta.*"
      ],
      "excludes": [
        "meta.description",
        "meta.other.*"
      ]
    }
  }

	def bulk_submit(self, actions):
		helpers.bulk(client=self.es,actions=actions) #, raise_on_error=False

PUT my_index/_doc/1
{
  "name": "Some binary blob",
  "blob": "U29tZSBiaW5hcnkgYmxvYg==" 
}


PUT maptest/_mapping/test
{
    "dynamic_templates": [
        {
            "en": {
                "match": "*_json",
                "match_mapping_type": "keyword",
                "mapping": {
                    "type": "keyword",
                    "store": "yes",
                    "index": "not_analyzed"
                }
            }
        }
    ]
}

PUT /my_index
{
    "mappings": {
        "my_type": {
            "dynamic_templates": [
                { "es": {
                      "match":              "*_es", 
                      "match_mapping_type": "string",
                      "mapping": {
                          "type":           "string",
                          "analyzer":       "spanish"
                      }
                }},
                { "en": {
                      "match":              "*", 
                      "match_mapping_type": "string",
                      "mapping": {
                          "type":           "string",
                          "analyzer":       "english"
                      }
                }}
            ]
}}}
https://www.elastic.co/guide/cn/elasticsearch/guide/current/custom-dynamic-mapping.html

GET /eevsim/_search
{
  "query": {
    "bool": {
    "must_not":{"term" : {"uid": "123"} },  
    "should": [
        {
          "match": {
            "md5": {
              "query": "201f2e517903766f7c41b90ef27f346f",
              "boost": 2
            }
          }
        },
        {
          "match": {
            "md5": {
              "query": "35179a54ea587953021400eb0cd23201", 
              "boost": 3
            }
          }
        }
      ],
       
      "minimum_should_match": "90%"
    }
  }
}

{"_id": "3-20", "_source": {"rid": 11386, "uid": 21, "sc": 13, "md5": "0f4d9831fee517c2b4223e4ebf6d0930 bfd2f212e4fdbc1b4b9e3c4d14fa42b1 20b30ac261d74904e7b9b3e2cf313728 a0
04c0a2b3e048968cea61002c71b1c6 83f565eac47ede4b022a77cd08d85bc5 a269cf9ee7c15792566a9c4953aed1a6 f380b022b086b477e6f1f6882fcf3b07 fa74e6c1cded62fad1c99999b6d613e0 c4da8d100
6203cb7ba6103ec55c12edc 7af1c8021855d7605e6e7b3d1c370372 d33a962163197dda27c395925a2d1d48 232d21f3b22d6d6fbb6b7fd035e03053 c9dbf1351587627236c0893aac2d1573"}}

12.2 , wrong program's id range 
127.0.0.1:9221[2]> zrevrange ids 0 10
 1) "811997267"
 2) "811997259"
 3) "811997255"
 4) "811997251"
 5) "811997231"
 6) "811997229"
 7) "811997215"
 8) "811997213"
 9) "811997195"
10) "811997191"
11) "811997185"

if spacy: 
	from spacy.lang import en
	spacy.sntbr		= (inst := en.English(), inst.add_pipe("sentencizer"))[0]
	spacy.snts		= lambda essay: [ snt.text.strip() for snt in  spacy.sntbr(essay).sents]
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.vplem		= lambda doc,ibeg,iend: doc[ibeg].lemma_ + " " + doc[ibeg+1:iend].text.lower()
	spacy.getdoc	= lambda snt: ( bs := redis.bs.get(snt), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setnx(snt, spacy.tobs(doc)) if not bs else None )[1]
	spacy.sntdocs	= lambda hkey: [spacy.getdoc(snt) for snt in json.loads(redis.r.hget(hkey,'snts'))] #'doc:inau:inau/1893-Cleveland.txt'

2021.12.12
ubuntu@ubuntu:/ftp/esmd5$ nohup python3 -m cikuu.bin.es loadjson eev2021.esmd5 eevsim & 
[1] 47096

 "_doc": {
				  "dynamic_templates": [
					{
					  "strings_as_keywords": { # only map string to keyword, not text 
						"match_mapping_type": "string",
						"mapping": {
						  "type": "keyword"
						}
					  }
					}
				  ]
				},
			
		print(">>finished " , idxname, file=sys.stderr)

self.es.index(index=idxname,id = f"{corpus}-{file}",  body = {"filename":file,'corpus':corpus,'body':open(f"{folder}/{file}",'r', encoding='utf-8').read().strip() })
'''