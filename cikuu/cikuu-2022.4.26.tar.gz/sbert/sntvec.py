# 2022.3.27
#pip install -U sentence-transformers   | uvicorn sntvec:app --host 0.0.0.0 --port 19200 --reload
import fire ,json, requests, hashlib
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

config = {  
		"settings" : {
			"refresh_interval": "1s",
			"number_of_shards": "3",
			"max_result_window":"2147483647",
			"index.mapping.ignore_malformed": "true",
			"analysis": {
			  "filter": {
				"postag_filter": {
				  "type": "pattern_capture",
				  "preserve_original": "false",
				  "patterns": [
					"(^([^_]+)_[a-z]+[,\\.$]?)",
					"(_[a-z\\-\\.\\'\\$0-9]+)$",
					"(_[a-z\\-\\.\\'\\$]+)",
					"(_[^\\w]+)_",
					"([^\\w])_"
				  ]
				},
				"postag_filter2": {
				  "type": "word_delimiter",
				  "type_table": [
					"^ => ALPHA",
					", => ALPHA",
					"$ => ALPHA",
					"_ => ALPHA",
					". => ALPHA",
					"- => ALPHA",
					"! => ALPHA",
					"? => ALPHA",
					"' => ALPHA",
					"0 => ALPHA",
					"1 => ALPHA",
					"2 => ALPHA",
					"3 => ALPHA",
					"4 => ALPHA",
					"5 => ALPHA",
					"6 => ALPHA",
					"7 => ALPHA",
					"8 => ALPHA",
					"9 => ALPHA"
				  ]
				},
				"unique_filter": {
				  "type": "unique",
				  "only_on_same_position": "true"
				}
			  },
			  "analyzer": {
				"postag_ana": {"filter": ["lowercase","postag_filter", "postag_filter2", "unique_filter"], "type": "custom", "tokenizer": "whitespace" },
				"path_ana": {"type": "custom", "tokenizer": "path-tokenizer"},
				"feedback_ana": {"type": "custom", "tokenizer": "feedback-tokenizer"},
				"err_ana": {"type": "custom",  "tokenizer": "path-tokenizer1"  },
				"chunk_ana": {"type": "custom", "tokenizer": "path-tokenizer2" },
				"kp_ana": { "filter": ["lowercase"], "type": "custom", "tokenizer": "keyword"}
			  },
			  "tokenizer": {
				"path-tokenizer": { "type": "path_hierarchy",  "delimiter": "/" },
				"path-tokenizer1": {"type": "path_hierarchy",  "delimiter": "|" },
				"path-tokenizer2": {"type": "path_hierarchy",  "delimiter": "/" },
				"feedback-tokenizer": { "type": "path_hierarchy",  "delimiter": "." }
				}
			},
			"number_of_replicas": "0"
		},
		"mappings" : {
			"_source": {"excludes": ["md5"]},
			"properties": {
			 "@timestamp":{"format":"strict_date_optional_time||epoch_millis", "type":"date"},
			"errs": { "type": "text", "analyzer": "path_ana" ,"fielddata":"true" },
			"feedback": { "type": "text", "analyzer": "feedback_ana" ,"fielddata":"true" },
			"kps": { "type": "text", "analyzer": "path_ana" ,"fielddata":"true" },
			"postag": { "type": "text", "analyzer": "postag_ana","fielddata":"true"},
			"np": { "type": "text", "analyzer": "postag_ana","fielddata":"true"},
			"i": { "type": "integer"},
			"score": { "type": "float"},
			"offset": { "type": "float"},
			"final_score": { "type": "float"},
			"sid": { "type": "keyword"},
			"id": { "type": "keyword"},
			"rid": { "type": "integer"},
			"did": { "type": "integer"},
			"docid": { "type": "keyword"},
			"uid": { "type": "integer"},
			"eid": { "type": "integer"},
			"sntnum": { "type": "integer"},
			"wordnum": { "type": "integer"},
			"awl": { "type": "float"},
			"cnt": { "type": "long"},
			"vers": { "type": "integer"},
			"ver": { "type": "integer"},
			"ct": { "type": "integer"},
			"lem": { "type": "keyword"},
			"lex": { "type": "keyword"},
			"low": { "type": "keyword"},
			"pos": { "type": "keyword"},
			"tag": { "type": "keyword"},

			"ap": { "type": "keyword"},
			"page": { "type": "keyword"},
			"pen": { "type": "keyword"},
			"label": { "type": "keyword"},
			"item": { "type": "keyword"},
			"lang": { "type": "keyword"},
			"key": { "type": "keyword"},
			"item_key": { "type": "keyword"},
			"score": { "type": "float"},
			"tmf": { "type": "float"},
			"stroke": { "type": "keyword", "index": "false"},
			"strokes": { "type": "keyword", "index": "false"},

			"en": { "type": "text", "analyzer": "standard","fielddata":"true"},
			"content": { "type": "text", "analyzer": "standard","fielddata":"true"},
			"zhseg": { "type": "text", "analyzer": "standard"},
			"zh": { "type": "text", "index": "false"},

			"src": { "type": "keyword"},
			"srcsnt": { "type": "keyword"},
			"segtype": { "type": "keyword"},
			"filename": { "type": "keyword"},
			"fullname": { "type": "keyword"},
			"sect": { "type": "keyword"},
			"index": { "type": "keyword"},
			"corpus": { "type": "keyword"},
			"folder": { "type": "keyword"},
			"head": { "type": "keyword"},
			"chunk": { "type": "keyword"},
			"type": { "type": "keyword"},
			"fn": { "type": "keyword"},
			"cat": { "type": "keyword"},
			"rel": { "type": "keyword"},
			"gov": { "type": "keyword"},
			"dep": { "type": "keyword"},
			"vp": { "type": "keyword"},
			"ap": { "type": "keyword"},
			"dp": { "type": "keyword"},
			"kp": { "type": "keyword"},
			"cate": { "type": "keyword"},
			"feedback": { "type": "keyword"},
			"tail":{ "type": "keyword"},
			"govpos":{ "type": "keyword"},
			"deppos":{ "type": "keyword"},
			"fd": { "type": "keyword"},
			"err": {"type": "text",  "analyzer": "err_ana"},
			"fd": { "type": "keyword"},
			"short_msg": { "type": "keyword"},
			"arr": { "type": "keyword", "index": "false" }, # dim arr of dsk
			"info": { "type": "keyword", "index": "false" ,"store": "false"},
			"kw": { "type": "keyword", "index": "false" ,"store": "false", "ignore_above": 60},
			"meta": { "type": "keyword", "index": "false" ,"store": "false"},
			"tc": {"type": "integer" , "index": "false"},
			"sc": {"type": "integer" , "index": "false"},
			"isum": {"type": "integer" , "index": "false"},
			"md5": { "type": "text", "store": "false", "norms":"false"},
			"toks": { "type": "keyword", "index": "false" ,"store": "false"},
			"snts": { "type": "keyword", "index": "false" ,"store": "false"},
			"blob": { "type": "binary", "store": "false"},
			"zlib": { "type": "binary", "store": "false"},
			"title": { "type": "text", "analyzer": "standard"},
			"essay": { "type": "text", "analyzer": "standard"},
			"body": { "type": "text", "index": "false" },
			"doc": { "type": "text", "index": "false" },#"doc": { "type": "keyword", "index": "false" ,"store": "false"}, # dim arr of dsk
			"tm": { "type": "date"}, #"format": "yyyy-MM-dd HH:mm:ss || yyyy-MM-dd || yyyy/MM/dd HH:mm:ss|| yyyy/MM/dd ||epoch_millis"
			"sdate": { "type": "date",  "format": "yyyy-MM-dd"},
			"csv": { "type": "keyword",  "index": "false"},
			"tsv": { "type": "keyword",  "index": "false"},
			"pair": { "type": "keyword",  "index": "false"},
			"json": { "type": "keyword",  "index": "false"},
			"v": { "type": "keyword",  "index": "false"},
			"n": { "type": "keyword",  "index": "false"},
			"adj": { "type": "keyword",  "index": "false"},
			"snt": { "type": "text", "analyzer": "standard","fielddata":"true"},
			"ske": { "type": "text", "analyzer": "standard"},
			"sntvec": {
				   "type": "dense_vector",
				   "dims": 384, 
				   "index": "true",
				   "similarity": "l2_norm"
				 },
			"skevec": {
				   "type": "dense_vector",
				   "dims": 384, 
				   "index": "true",
				   "similarity": "l2_norm"
				 },
			"vec": {
				   "type": "dense_vector",
				   "dims": 384, # use sbert 
				   "index": "true",
				   "similarity": "l2_norm"
				 }
		  }
		}
	}

from elasticsearch import Elasticsearch,helpers
es = Elasticsearch(  
    "https://localhost:9200", 
    ca_certs="/home/ubuntu/http_ca.crt",
	http_auth=('elastic', 'cikuutest!'), timeout=3600 )

from uvirun import * 
app.title = "snt vec search" 
app.tm = "2022.2.18"

@app.get('/sntvec/snt')
def snt_search(snt:str="I'm glad to meet you.", index:str='testidx', topk:int=10): 
	''' search sent with nearest semantic '''
	vec = model.encode(snt.strip())
	res = es.knn_search(index=index, source=['snt'],knn={ 
	"field": "vec",
   "query_vector": vec,
   "k": 10,
   "num_candidates": topk})
	return res

@app.get('/sntvec/query')
def sntvec_query(query:str="I'm glad to meet you.", index:str='testidx', field:str='sntvec', topk:int=10): 
	''' field: sntvec/skevec , added 2022.3.21 '''
	vec = model.encode(query.strip())
	res = es.knn_search(index=index, source=['snt','ske'], knn={ 
	"field": field,
   "query_vector": vec,
   "k": 10,
   "num_candidates": topk})
	return res

@app.get('/sntvec/newindex')
def newindex(idxname:str='testidx'):  
	''' '''
	if es.indices.exists(index = idxname): es.indices.delete(index = idxname) 
	return es.indices.create(index=idxname, body=config)

@app.get('/sntvec/tovec')
def snt_tovec(snt:str="I'm glad to meet you."): 
	''' search sent with nearest semantic '''
	vec = model.encode(snt.strip())
	return vec.tolist()

@app.get('/sntvec/indexlist')
def index_list(): 
	''' show tables '''
	return es.sql.query(query = "show tables").get('rows',[])

@app.get('/sntvec/delete_by_id')
def delete_by_id(index:str='testidx', id:str='xxx'): 
	''' delete_by_id '''
	return es.delete(index=index, id=id)

@app.get('/sntvec/add_new_snt')
def add_new_snt(idxname:str='testidx', snt:str='Justice delayed is justice denied.'): 
	'''  '''
	if not es.indices.exists(index = idxname):  es.indices.create(index=idxname, body=config)
	md5 = hashlib.md5(snt.encode(encoding='UTF-8')).hexdigest()
	vec = model.encode(snt.strip())
	return es.index(index=idxname, id=md5, document={"snt":snt, "vec": vec.tolist()})

@app.get('/sntvec/add_new_snt_with_ske')
def add_new_snt_with_ske(idxname:str='testidx', snt:str='Justice delayed is justice denied.', ske:str="_NP delayed is _NP denied ."): 
	'''  '''
	if not es.indices.exists(index = idxname):  es.indices.create(index=idxname, body=config)
	md5 = hashlib.md5(snt.encode(encoding='UTF-8')).hexdigest()
	sntvec = model.encode(snt.strip())
	skevec = model.encode(ske.strip())
	return es.index(index=idxname, id=md5, document={"snt":snt, "ske":ske,  "sntvec": sntvec.tolist(), "skevec": skevec.tolist()})

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

class util(object):
	def __init__(self): pass 

	def vec(self, infile, outfile=None): 
		''' gzjc.snt -> gzjc.vec_source  '''
		if not outfile : outfile = infile.split('.')[0] + ".vec"
		print ("started:", infile, flush=True)
		with open(outfile, 'w') as fw: 
			for line in readline(infile): 
				vec = model.encode(line.strip())
				arr = {'snt': line.strip(), 'vec': vec.tolist()}
				fw.write(json.dumps(arr) + "\n")
		print ("finished:", infile)

	def idsource(self, infile, idxname=None, batch=100000, refresh:bool=True): 
		''' {"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33"}}'''
		if not idxname : idxname = infile.split('.')[0] 
		print("idsource started:", infile, idxname, es, flush=True)
		if refresh and es.indices.exists(index=idxname): es.indices.delete(index=idxname)
		if not es.indices.exists(index=idxname): es.indices.create(index=idxname, body=config)
		actions=[]
		for line in readline(infile):  
			try:
				arr = json.loads(line) # 
				if not '_source' in arr : arr = {"_source": arr} # source only njson 
				arr.update({'_op_type':'index', '_index':idxname})
				actions.append(arr)
				if len(actions) > batch : 
					helpers.bulk(client=es,actions=actions, raise_on_error=False)
					actions=[]
					print(arr["_id"], flush=True) 
			except Exception as ex:
				print(">>callback ex:", ex, line)
		helpers.bulk(client=es,actions=actions, raise_on_error=False)
		print("idsource finished:", infile,idxname)

if __name__ == '__main__':
	fire.Fire(util)

'''
uvicorn sntvec:app --host 0.0.0.0 --port 19200 --reload

python sntvec.py idsource gzjc.source  gzjc1

GET gzjc/_knn_search
{
 "knn": {
   "field": "image-vector",
   "query_vector": [-0.5, 9.4, 1,2],
   "k": 10,
   "num_candidates": 100
 }
}

PUT gzjc
{
 "mappings": {
   "properties": {
     "snt":{"type":"text"},
     "vec": {
       "type": "dense_vector",
       "dims": 384,
       "index": true,
       "similarity": "l2_norm"
     }
   }
 }
}

>>> es.get(index='twitter', id='wTxqC38BopRXpF5veeGm')
ObjectApiResponse({'_index': 'twitter', '_id': 'wTxqC38BopRXpF5veeGm', '_version': 1, '_seq_no': 0, '_primary_term': 1, 'found': True, '_source': {'one': 'wo'}})
>>>

>>> res.body
{'_index': 'twitter', '_id': 'wTxqC38BopRXpF5veeGm', '_version': 1, '_seq_no': 0, '_primary_term': 1, 'found': True, '_source': {'one': 'wo'}}

certificate_path = os.path.join(CERT_PATH, 'cacert.pem')
certificate_key_path = os.path.join(CERT_PATH, 'cacert.key')
response = requests.get(url, cert=(certificate_path, certificate_key_path))
'''