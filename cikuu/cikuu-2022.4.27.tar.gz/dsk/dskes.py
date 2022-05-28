# 22-4-12
import json, sys, time, fire,traceback, os,spacy
from elasticsearch import Elasticsearch,helpers

def readline(infile, sepa=None):
	with open(infile, 'r') as fp: #,encoding='utf-8'
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]

def index_dsk(dsk, index) : 
	info = dsk.get("info", {})
	snts  = [ ar['meta']['snt'].strip() for ar in dsk['snt']] 
	eid = int( info.get('essay_id',0) )
	rid = int( info.get('rid',0) )
	uid = int( info.get('uid',0) )
	ver = int( info.get('e_version',0) )
	final_score = float( info.get('final_score',0) ) # added 2022.2.15

	#if ver <= get_eid_ver(eid): return 
	#fire.es.delete_by_query(index=fire.index, conflicts='proceed', body={"query":{"match":{"eid":eid}}}) #"query": "select src, kp, cate from essaydm where rid = 2589013 and type='feedback' and cate like 'w_punct%'  limit 3 "

	actions=[]
	dim = dsk.get("doc", {})
	dim.update({'type':'doc', 'eid': eid, 'rid': rid , 'uid': uid, 'ver':ver, 'final_score':final_score})
	actions.append({'_op_type':'index', '_index':index, '_id': eid, '_source':dim})
	for idx, snt in enumerate(snts) : 
		doc = spacy.nlp(snt.strip())	
		sntlen = len(doc)
		if not sntlen : continue
		actions.append({'_op_type':'index', '_index':index,  '_id': f"{eid}-{idx}",  '_source': {'snt':doc.text, "eid":eid, 'rid': rid , 'uid': uid, 'tc':sntlen, 'awl': sum([ len(t.text) for t in doc])/sntlen ,  'type':'snt',	'postag':' '.join(['^'] + [f"{t.text}_{t.lemma_}_{t.tag_}_{t.pos_}" for t in doc] + ['$']) }})
		[actions.append({'_op_type':'index', '_index':index, '_id': f"{eid}-{idx}:trp-{t.i}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'trp', 'src': f"{eid}-{idx}", 'gov': t.head.lemma_, 'rel': f"{t.dep_}_{t.head.pos_}_{t.pos_}", 'dep': t.lemma_ }}) for t in doc if t.dep_ not in ('punct')]
		[actions.append({'_op_type':'index', '_index':index, '_id': f"{eid}-{idx}:tok-{t.i}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'tok', 'src': f"{eid}-{idx}", 'lex': t.text, 'low': t.text.lower(), 'lem': t.lemma_, 'pos': t.pos_, 'tag': t.tag_, 'i':t.i, 'head': t.head.i }}) for t in doc]
		[actions.append({'_op_type':'index', '_index':index, '_id': f"{eid}-{idx}:np-{np.start}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid,'type':'np', 'src': f"{eid}-{idx}", 'lem': doc[np.end-1].lemma_, 'chunk': np.text, }}) for np in doc.noun_chunks]
	
		for ar in dsk['snt']:
			for kp, v in ar['feedback'].items():
				actions.append({'_op_type':'index', '_index':index,  '_id': f"{eid}-{idx}:kp-{v['ibeg']}",  '_source': {"eid":eid, 'rid': rid , 'uid': uid, 'type':'feedback',
				'src': f"{eid}-{idx}",  'kp':v.get('kp',''), 'cate': v.get('cate',''), 'short_msg': v.get('short_msg','') }})

	helpers.bulk(client=fire.es,actions=actions, raise_on_error=False)
	if fire.debug: print ("eid:", eid, 'ver:', ver, "rid:", rid, "uid:", uid)
	return {'eid':eid, 'ver':ver }

def run(infile, eshost='127.0.0.1', esport=9200, idxname='essaydm', debug=False): 
	''' dsk -> essaydm, 2022.4.12 '''
	fire.es		= Elasticsearch([ f"http://{eshost}:{esport}" ]) 
	fire.index  = idxname
	fire.debug	= debug

	for line in readline(infile): 
		try: 
			dsk = json.loads(line.strip()) 
			index_dsk(dsk, idxname) 
		except Exception as ex:
			print ('ex:', ex, "\t", line) 
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)

if __name__ == '__main__': 
	fire.Fire(run)