# 2022.5.24  clickhouse | clickhouse-client --query="INSERT INTO shav FORMAT TSV" < gzjc.shav
#create table shav ( sid FixedString(32), head String, attr String, val String ) engine = MergeTree() order by (sid,head,attr,val);
#create table gzjc ( sid UInt32, head String, attr String, val String ) engine = MergeTree() order by (sid,head,attr,val);
import json, traceback,sys, time
import en
from en import terms
from en.spacybs import Spacybs
import hashlib
sntmd5		= lambda s: hashlib.md5(s.encode("utf8")).hexdigest()
incr = lambda si, *tups, delta = 1: [si.update({f"{tup[0]}\t{tup[1]}\t{tup[2]}": delta}) for tup in tups ] #incr(si ,("booked", "VERB","VBD"), )

def index(dbfile, outfile=None):  
	''' clec.spacybs -> clec.shav, 2022.5.24 '''
	name = dbfile.split('.')[0]
	if not outfile : outfile = name + '.shav' 
	with open(outfile, 'w') as fw: 
		for rowid, snt, bs in Spacybs(dbfile).items() :
			try:
				doc = spacy.frombs(bs) 
				sid = rowid #sid = sntmd5(snt)
				snthead = json.dumps({"tc": len(doc)})
				fw.write(f'{sid}\t{snthead}\tSNT\t{snt}\n')
				for t in doc:
					fw.write(f"{sid}\t{t.lemma_}\tPOS\t{t.pos_}\n")
					fw.write(f"{sid}\t{t.lemma_}\tLEX\t{t.text.lower()}\n")
					fw.write(f"{sid}\t{t.lemma_}\t{t.pos_}\t{t.tag_}\n")
					fw.write(f"{sid}\t{t.lemma_}/{t.pos_}\t{t.tag_}\t{t.text.lower()}\n")
					if t.pos_ not in ("PROPN","PUNCT"): 
						fw.write(f"{sid}\t{t.head.lemma_}/{t.head.pos_}\t{t.dep_}_{t.pos_}\t{t.lemma_}\n") # open/VERB  dobj_NOUN door
						fw.write(f"{sid}\t{t.lemma_}/{t.pos_}\t{t.head.pos_}~{t.dep_}\t{t.head.lemma_}\n") # door/NOUN  VERB~dobj open 
				for sp in doc.noun_chunks:
					fw.write(f"{sid}\t{sp.root.lemma_.lower()}/NOUN\tNP\t{sp.text.lower()}\n")

				terms.attach(doc)
				for k,ar in doc.user_data.items(): 
					if ar.get('type','') not in ('','tok','trp') and 'lem' in ar and 'chunk' in ar and ar["type"].startswith('v'):
						fw.write(f"{sid}\t{ar['lem']}/VERB\t{ar['type']}\t{ar['chunk']}\n")
			except Exception as e:
				print ("ex:", e, rowid, snt)
	print ("finished submitting:", name, flush=True) 

if __name__	== '__main__':
	import fire 
	fire.Fire(index)
