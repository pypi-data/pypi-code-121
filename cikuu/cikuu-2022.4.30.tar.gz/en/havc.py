# 2022.5.29  cp from shav.py   clickhouse | clickhouse-client --query="INSERT INTO shav FORMAT TSV" < gzjc.shav
#create table shav ( sid UInt32, head String, attr String, val String ) engine = MergeTree() order by (sid,head,attr,val);
#create table gzjc ( head String, attr String, val String, cnt UInt32, sids Array(UInt32) ) engine = MergeTree() order by (head,attr,val);
# insert into gzjc select head, attr, val, count(*), groupArray(sid) from shav group by head, attr, val ;
import json, traceback,sys, time, en, sqlite3
from en import terms
from en.spacybs import Spacybs

def _add(sid, head, attr, val, conn): 
	conn.execute(f"insert into shav(sid, head, attr, val) values(?,?,?,?)", (sid, head, attr, val))

def index(dbfile, outfile=None):  
	''' clec.spacybs -> clec.havc, 2022.5.29 '''
	name = dbfile.split('.')[0]
	if not outfile : outfile = name + '.havc' 
	conn =	sqlite3.connect(outfile, check_same_thread=False) 
	conn.execute(f'CREATE TABLE IF NOT EXISTS snt (sid int PRIMARY KEY, snt varchar(512), bs blob) without rowid') # need toks json? 
	conn.execute(f'drop TABLE IF EXISTS shav')
	conn.execute(f'CREATE TABLE shav (sid int , head varchar(64), attr varchar(64), val varchar(64) )')
	conn.execute('PRAGMA synchronous=OFF')

	print ("start to walk:", dbfile, flush=True) 
	for sid, snt, bs in Spacybs(dbfile).items() :
		try:
			conn.execute(f"insert or ignore into snt(sid, snt, bs) values(?,?,?)", (sid, snt, bs))
			doc = spacy.frombs(bs) 
			for t in doc:
				_add(sid, t.lemma_, 'POS', t.pos_, conn)
				_add(sid, t.lemma_, 'LEX', t.text.lower(), conn)
				_add(sid, t.lemma_, t.pos_, t.tag_, conn)
				_add(sid, f"{t.lemma_}/{t.pos_}", t.tag_, t.text.lower(), conn)  # happen/VERB  VBG  happening
				if t.pos_ not in ("PROPN","PUNCT"): 
					_add(sid, "{t.head.lemma_}/{t.head.pos_}", f"{t.dep_}_{t.pos_}", t.lemma_, conn) # open/VERB  dobj_NOUN door
					_add(sid, "{t.lemma_}/{t.pos_}", f"{t.dep_}~{t.head.pos_}", t.head.lemma_, conn) # door/NOUN  VERB~dobj open 
			for sp in doc.noun_chunks:
				_add(sid, sp.root.lemma_.lower() +"/NOUN", "NP" , sp.text.lower(), conn)

			terms.attach(doc)
			for k,ar in doc.user_data.items(): 
				if ar.get('type','') not in ('','tok','trp') and 'lem' in ar and 'chunk' in ar and ar["type"].startswith('v'):
					_add(sid, ar['lem'] + "/VERB", ar['type'], ar['chunk'], conn)
		except Exception as e:
			print ("ex:", e, sid, snt)
	print ("start to group",flush=True) 
	conn.execute(f'drop TABLE IF EXISTS havc')
	conn.execute(f'CREATE TABLE havc (head varchar(64), attr varchar(64), val varchar(64), cnt int , sids mediumtext, primary key(head, attr,val) )')
	conn.execute("insert or ignore into havc select head, attr, val, count(*) , '[' || group_concat(sid) || ']' from shav group by head, attr, val")
	conn.execute("insert into havc(head, cnt ) select '_SUM_SNT' , count(*) from snt") #select sum(cnt) from havc where attr = 'LEX';
	conn.execute("drop table shav")
	conn.commit() 
	conn.execute("vacuum")
	conn.close()
	print ("finished submitting:", dbfile, flush=True) 

if __name__	== '__main__':
	import fire 
	fire.Fire(index)

def index_to_tsv(dbfile, outfile=None):  
	''' clec.spacybs -> clec.havc, 2022.5.29 '''
	name = dbfile.split('.')[0]
	if not outfile : outfile = name + '.shav' 
	with open(outfile, 'w') as fw: 
		for rowid, snt, bs in Spacybs(dbfile).items() :
			try:
				doc = spacy.frombs(bs) 
				sid = rowid #sid = sntmd5(snt)
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