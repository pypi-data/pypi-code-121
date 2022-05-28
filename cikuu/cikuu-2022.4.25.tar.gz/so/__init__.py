# 2022.5.11 updated , add sqlrow for EachRowJson
# 2022.2.13 created 
import requests,json, os, math,re,traceback
from elasticsearch import Elasticsearch,helpers
from collections import	Counter
import warnings
warnings.filterwarnings("ignore")

eshost	= os.getenv("eshost", "127.0.0.1") 
esport	= int(os.getenv("esport", 9200))
#requests.put(f"http://{eshost}:{esport}/_cluster/settings", json={"persistent": {"search.max_buckets": 1000000}}).text

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
			"skenp": { "type": "text", "analyzer": "postag_ana","fielddata":"true"},
			"sentgram": { "type": "text", "analyzer": "postag_ana","fielddata":"true"}, # simple_complex_headpp compound_question_itis_svo
			"np": { "type": "text", "analyzer": "postag_ana","fielddata":"true"},
			"ske": { "type": "text", "analyzer": "postag_ana","fielddata":"true"},
			"i": { "type": "integer"},
			"start": { "type": "integer"},
			"end": { "type": "integer"},
			"score": { "type": "float"},
			"offset": { "type": "float"},
			"final_score": { "type": "float"},
			"sid": { "type": "keyword"},
			"id": { "type": "keyword"},
			"rid": { "type": "integer"},
			"did": { "type": "integer"},
			"ibeg": { "type": "integer"},
			"iend": { "type": "integer"},
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
			"term": { "type": "keyword"},

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
			"_snt": { "type": "keyword", "index": "false"},
			"_ske": { "type": "keyword", "index": "false"},
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
			"attr": { "type": "keyword"},
			"val": { "type": "keyword"}, # head, attr, val 
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
			"si": {
				   "type": "nested",
				   "properties": {
					  "s": {"type": "keyword"},
					  "i": {"type": "integer"}
				   }
				},
			 "sntvec": {
			   "type": "dense_vector",
			   "dims": 384,
			   "index": True,
			   "similarity": "l2_norm"
			 },
			 "skevec": {  # _NP jumped over _NP
			   "type": "dense_vector",
			   "dims": 384,
			   "index": True,
			   "similarity": "l2_norm"
			 },
			"vec": {
				   "type": "dense_vector",
				   "dims": 384, # use sbert 
				   "index": "true",
				   "similarity": "l2_norm"
				 },

			"err": {"type": "text",  "analyzer": "err_ana"},
			"fd": { "type": "keyword", "index": "false"},
			"short_msg": { "type": "keyword", "index": "false"},
			"arr": { "type": "keyword", "index": "false" }, # dim arr of dsk
			"info": { "type": "keyword", "index": "false" ,"store": "false"},
			"kw": { "type": "keyword", "index": "false" ,"store": "false", "ignore_above": 60},
			"meta": { "type": "keyword", "index": "false" ,"store": "false"},
			"dim": { "type": "keyword", "index": "false" },
			"tc": {"type": "integer" , "index": "false"},
			"sc": {"type": "integer" , "index": "false"},
			"isum": {"type": "integer" , "index": "false"},
			"md5": { "type": "text", "store": "false", "norms":"false"},
			"toks": { "type": "keyword", "index": "false" ,"store": "false"},
			"snts": { "type": "keyword", "index": "false" },
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
			"snt": { "type": "text", "analyzer": "standard","fielddata":"true"}
		  }
		}
	}

#if eshost: 
es		= Elasticsearch([ f"http://{eshost}:{esport}" ])  
newindex= lambda idxname : (es.indices.delete(idxname) if es.indices.exists(idxname) else None, es.indices.create(idxname, config))[1] # body=
rows	= lambda query: requests.post(f"http://{eshost}:{esport}/_sql",json={"query": query}).json().get('rows',[]) 
sql		= lambda query: requests.post(f"http://{eshost}:{esport}/_sql",json={"query": query}).json().get('rows',[]) 
sntnum	= lambda cp: sql(f"select count(*) cnt from {cp} where type = 'snt'" )[0][0] #75222
lexnum	= lambda w,cp: sql(f"select count(*) cnt from {cp} where low = '{w}' and type = 'tok'")[0][0] # opened = 70
lemnum	= lambda w,cp: sql(f"select count(*) cnt from {cp} where lem = '{w}' and type = 'tok'")[0][0] 
sqlsi	= lambda query: (si:=Counter(), [si.update({row[0]:1}) for row in sql(query)])[0]
warmup  = lambda : requests.put(f"http://{eshost}:{esport}/_cluster/settings", json={"persistent": {"search.max_buckets": 1000000}}).text

def sqlrow(query="select lem, count(*) cnt  from gzjc where type = 'tok' and pos != 'PUNCT' group by lem order by cnt desc limit 10"):
	''' {'columns': [{'name': 'lem', 'type': 'keyword'}, {'name': 'cnt', 'type': 'long'}], 'rows': [['the', 7552], ['be', 5640], ['and', 3604], ['to', 3561], ['of', 3127], ['a', 2902], ['in', 2687], ['I', 2063], ['have', 1562], ['it', 1311]]} '''
	res = requests.post(f"http://{eshost}:{esport}/_sql",json={"query": query}).json() 
	columns = [ ar['name'] for ar in res['columns'] ]
	return  [  dict(zip(columns, ar)) for ar in res['rows'] ] #[{'lem': 'the', 'cnt': 7552}, {'lem': 'be', 'cnt': 5640}, {'lem': 'and', 'cnt': 3604}, {'lem': 'to', 'cnt': 3561}, {'lem': 'of', 'cnt': 3127}, {'lem': 'a', 'cnt': 2902}, {'lem': 'in', 'cnt': 2687}, {'lem': 'I', 'cnt': 2063}, {'lem': 'have', 'cnt': 1562}, {'lem': 'it', 'cnt': 1311}]

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def likelihood(a,b,c,d, minus=None):  #from: http://ucrel.lancs.ac.uk/llwizard.html
	try:
		if a is None or a <= 0 : a = 0.000001
		if b is None or b <= 0 : b = 0.000001
		E1 = c * (a + b) / (c + d)
		E2 = d * (a + b) / (c + d)
		G2 = round(2 * ((a * math.log(a / E1)) + (b * math.log(b / E2))), 2)
		if minus or  (minus is None and a/c < b/d): G2 = 0 - G2
		return G2
	except Exception as e:
		print ("likelihood ex:",e, a,b,c,d)
		return 0

#PUT twitter/_mapping {  "properties": {  "email": { "type": "keyword"  }  }}
#"stroke": { "type": "keyword", "index": "false"},
def delete_index(cp:str='testidx'): 
	return requests.delete(f"http://{eshost}:{esport}/{cp}").text #DELETE /twitter
def new_empty_index(cp:str='testidx', delete:bool=True): 
	if delete: requests.delete(f"http://{eshost}:{esport}/{cp}").text
	return requests.put(f"http://{eshost}:{esport}/{cp}", data={}).text #PUT twitter  {}
def add_mapping_keyword(kws:list, cp:str='testidx'): 
	return [requests.put(f"http://{eshost}:{esport}/{cp}/_mapping/", data={"properties": {  f"{kw}": { "type": "keyword"  }  }}).text for kw in kws]
def add_mapping_keyword_noindex(kws:list, cp:str='testidx'): 
	return [requests.put(f"http://{eshost}:{esport}/{cp}/_mapping/", data={"properties": {  f"{kw}": { "type": "keyword", "index": "false"} }}).text for kw in kws]
def add_mapping_float(kws:list, cp:str='testidx'): 
	return [requests.put(f"http://{eshost}:{esport}/{cp}/_mapping/", data={"properties": {  f"{kw}": { "type": "float"  }  }}).text for kw in kws]
def add_mapping_integer(kws:list, cp:str='testidx'): 
	return [requests.put(f"http://{eshost}:{esport}/{cp}/_mapping/", data={"properties": {  f"{kw}": { "type": "integer"  }  }}).text for kw in kws]
def add_mapping(dic:dict, cp:str='testidx'): 
	''' {"num":"integer", "awl":"float", "tag":"keyword"} '''
	return [requests.put(f"http://{eshost}:{esport}/{cp}/_mapping/", data={"properties": {  f"{k}": { "type": "{v}"  }  }}).text for k,v in dic.items()]

def bulk(arr, batch=100000, debug=False):
	''' bulk submit , added 2022.3.27, not tested yet '''
	if not hasattr(bulk, 'actions'):	bulk.actions=[]
	bulk.actions.append(arr)  #{'_op_type':'index', '_index':idxname, '_id': did, '_source': arr}
	if len(bulk.actions) > batch : 
		try:
			helpers.bulk(client=es,actions=actions, raise_on_error=False)
			if debug: print (bulk.actions[-1], flush=True) 
			bulk.actions = []
		except Exception as ex:
			print(">>bulk ex:", ex)

	def submit(): 
		print ("bulk submit is called, un-submiited actions len: ", len(bulk.actions)) 
		if len(bulk.actions) >0 : 
			helpers.bulk(client=es,actions=bulk.actions, raise_on_error=False)
			bulk.actions = []	

def ids(_ids:list, cp:str='inau'): 
	''' ["one","two"] '''
	sql	= { 
    "query": {
        "ids" : {
            "type" : "_doc",
            "values" : _ids
			}
		}
	}
	return requests.post(f"http://{eshost}:{esport}/{cp}/_search/", json=sql).json()

def term_to_snts(sql): 
	rows = es.sql(sql) #f"select src from {cp} where type = 'trp' and gov='{gov}' and rel='{rel}' and dep='{dep}' limit {topk}"
	sql	= {
    "query": {
        "ids" : {
            "type" : "_doc",
            "values" : [row[0] for row in rows] #clec:snt-34993,  clec:snt-32678
			}
		}
	}
	return requests.post(f"http://{eshost}:{esport}/{cp}/_search/", json=sql).json()

def match_phrase(phrase:str='opened the box', cp:str='clec', topk:int=10): 
	''' '''
	sql	= {
  "query": {
    "match_phrase": {
      "snt": phrase
    }
  }
  , "size": topk
}
	return requests.post(f"http://{eshost}:{esport}/{cp}/_search/", json=sql).json()

phrase_num = lambda phrase, cp='clec', topk=10: match_phrase(phrase, cp, topk)["hits"]["total"]["value"]

addpat	= lambda s : f"{s}_[^ ]*" if not s.startswith('_') else f"[^ ]*{s}_[^ ]*"   # if the last one, add $ 
rehyb   = lambda hyb: ' '.join([ addpat(s) for s in hyb.split()])  #'the_[^ ]* [^ ]*_NNS_[^ ]* of_[^ ]*'
heads   = lambda chunk:  ' '.join([s.split('_')[0].lower() for s in chunk.split()])		#the_the_DT_DET adventures_adventure_NNS_NOUN of_of_IN_ADP
def hybchunk(hyb:str='the _NNS of', index:str='gzjc', size:int= -1, topk:int=10):
	''' the _NNS of -> {the books of: 13, the doors of: 7} , added 2021.10.13 '''
	sql= {
  "query": { 
    "bool": { 
      "must": [
        { "match_phrase": { "postag":  hyb}},
        { "match": { "type":"snt" }}
      ]
    }
  },
  "size":  size
}
	res = requests.post(f"http://{eshost}:{esport}/{index}/_search/", json=sql).json()
	si = Counter()
	repat = rehyb(hyb)
	for ar in res['hits']['hits']: 
		postag =  ar["_source"]['postag']
		m= re.search(repat,postag) #the_the_DT_DET adventures_adventure_NNS_NOUN of_of_IN_ADP
		if m : si.update({ heads(m.group()):1})
	return si.most_common(topk)

if __name__ == "__main__": 
	print(es)
	print ( sql("select lem, count(*) cnt  from gzjc where type = 'tok' and pos != 'PUNCT' group by lem order by cnt desc limit 10"))
	print ( sqlrow("show tables")) 

'''
PUT twitter/_mapping 
{
  "properties": {
    "email": {
      "type": "keyword"
    }
  }
}


PUT my_index
{
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "dense_vector",
        "dims": 4
      },
      "my_text" : {
        "type" : "keyword"
      }
    }
  }
}

GET my_index/_search
{
  "query": {
    "script_score": {
      "query": {
        "match_all": {}
      },
      "script": {
        "source": "cosineSimilarity(params.query_vector, 'my_vector') + 1.0",
        "params": {
          "query_vector": [ 1,2,3]
        }
      }
    }
  }
}


PUT my_index/_doc/1
{
  "my_text" : "text1",
  "my_vector" : [0.5, 10, 6, 3]
}

PUT my_index/_doc/2
{
  "my_text" : "text2",
  "my_vector" : [-0.5, 10, 10, 4]
}

GET /my_index/_search
{
  "query": {
    "match_all": { }
  }
}

essaydm.wrask.com 
ubuntu@VM-171-3-ubuntu:/data$ runlike es
docker run --name=es --hostname=db25101107b8 --user=elasticsearch --mac-address=02:42:ac:12:00:02 --env=discovery.type=single-node --env=PATH=/usr/local/openjdk-11/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin --env=LANG=C.UTF-8 --env=JAVA_HOME=/usr/local/openjdk-11 --env=JAVA_VERSION=11.0.9.1 --env=EK_VERSION=7.15.1 --volume=/ftp/es-9200-eevsnts:/home/elasticsearch/elasticsearch-7.15.1/data --workdir=/home/elasticsearch -p 5601:5601 -p 9200:{esport} --restart=always --label='maintainer=nshou <nshou@coronocoya.net>' --runtime=runc --detach=true nshou/elasticsearch-kibana /bin/sh -c 'elasticsearch-${EK_VERSION}/bin/elasticsearch -E http.host=0.0.0.0 --quiet & kibana-${EK_VERSION}-linux-x86_64/bin/kibana --allow-root --host 0.0.0.0 -Q'

#https://www.elastic.co/cn/blog/introducing-approximate-nearest-neighbor-search-in-elasticsearch-8-0

PUT index
{
 "mappings": {
   "properties": {
     "image-vector": {
       "type": "dense_vector",
       "dims": 128,
       "index": true,
       "similarity": "l2_norm"
     }
   }
 }
}

POST index/_doc
{
 "image-vector": [0.12, 1.34, 3.4]
}

GET index/_knn_search
{
 "knn": {
   "field": "image-vector",
   "query_vector": [-0.5, 9.4, 3],
   "k": 10,
   "num_candidates": 100
 }
}

from dic.word_awl import word_awl 
@app.get("/corpus/word_awl")
def corpus_word_awl(index:str='gzjc', topk:int=10): 
	return (si:= Counter(), [si.update({s:i}) for s,i in rows(f"select lem, count(*) from {index} where type = 'tok' group by lem") if s in word_awl ], si.most_common(topk))[-1]

'''