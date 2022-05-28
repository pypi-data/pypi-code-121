# 2022.5.8 
#CREATE TABLE lempostag ( cp varchar(16) not null default '', lem varchar(64) not null default '',  pos varchar(32) not null default '',  tag varchar(64) not null default '', count int not null default 0, unique key uk(cp,lem,pos,tag), index attrs(cp,pos,tag)) engine=myisam;

def _submit(cp, si, cursor): 
	''' submit gzjc.clasi '''
	for k,cnt in si.items(): 
		try:
			arr = k.strip().split("\t")
			if len(arr) >= 3: cursor.execute("insert ignore into lempostag(cp,lem,pos,tag,count) values(%s,%s,%s,%s,%s)", (cp,arr[0],arr[1],arr[2],cnt))
		except Exception as ex:
			print(">>ex:", ex, k, cnt)

incr = lambda si, *tups, delta = 1: [si.update({f"{tup[0]}\t{tup[1]}\t{tup[2]}": delta}) for tup in tups ] #incr(si ,("booked", "VERB","VBD"), )

def index(dbfile, host='192.168.1.56',port=3306,user='cikuu',password='cikuutest!',db='kp'):  
	''' clec.spacybs -> lempostag, 2022.5.8 '''
	import json, pymysql,  traceback,sys, time
	from collections import	Counter,defaultdict
	from tqdm import tqdm
	import en
	from en import terms
	from en.spacybs import Spacybs

	name = dbfile.split('.')[0]
	conn = pymysql.connect(host=host,port=port,user=user,password=password,db=db)
	cursor= conn.cursor()
	si = Counter()
	sntnum,wordnum = 0,0
	for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
		try:
			doc = spacy.frombs(bs)
			kps = " ".join([ f"{t.pos_}_{t.lemma_}" for t in doc] + [ f"{t.tag_}_{t.lemma_}" for t in doc] + [ f"{t.dep_}_{t.head.pos_}_{t.pos_}_{t.head.lemma_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')])
			cursor.execute("insert ignore into ftsnt(snt, kps, src) values(%s,%s,%s)", (snt,kps, name))
			conn.commit()
			sntnum = sntnum + 1 #incr(si, ("SUM_SNT", "", "") )
			wordnum = wordnum + len(doc) #incr(si, ("SUM_WORD", "", ""), delta=len(doc) )
			for t in doc:
				incr(si, (t.lemma_, t.pos_, t.tag_), (t.lemma_, "LEX", t.text) )
				if t.pos_ not in ("PROPN","PUNCT"): 
					incr(si, (t.lemma_, "POS", t.pos_), (t.head.lemma_, f"{t.dep_}_{t.head.pos_}_{t.pos_}", t.lemma_) , (t.lemma_, f"~{t.dep_}_{t.head.pos_}_{t.pos_}", t.head.lemma_) 
					#,(f"#{t.pos_}", "", ""),(f"#{t.tag_}", "", ""),(f"#{t.dep_}", "", "")
					, (t.head.lemma_, t.head.pos_, t.dep_)  # open VERB  dobj 
					, (t.lemma_, t.pos_, "~" + t.dep_) )  # door NOUN ~dobj 
			for sp in doc.noun_chunks:
				incr(si, (sp.root.lemma_.lower(), "NOUN", "NP") )
				incr(si, (sp.root.lemma_.lower(), "NP", sp.text.lower()),(f"#NP", "", "") )

			terms.attach(doc)
			for k,ar in doc.user_data.items(): 
				if ar.get('type','') not in ('','tok','trp') and 'lem' in ar and 'chunk' in ar:
					incr(si, (ar["lem"], ar["type"], ar["chunk"]),(f"#{ar['type']}", "", "") )  # enjoy / vvbg / enjoy swimming 
					if ar["type"].startswith('v') : incr(si, (ar["lem"], "VERB", ar["type"]))
				
		except Exception as e:
			print ("ex:", e, rowid, snt)

	_submit(name, si, cursor) 
	conn.commit()
	cursor.execute(f"insert ignore into lempostag(cp, lem, count) values('{name}', '#SNT', {sntnum})")
	cursor.execute(f"insert ignore into lempostag(cp, lem, count) values('{name}', '#WORD', {wordnum})")
	cursor.execute(f"insert ignore into lempostag(cp, lem, count) select cp, concat('#',tag), sum(count) from lempostag where cp = '{name}' and pos = 'POS'  group by tag ")
	for s in ('VERB','NOUN','ADJ','ADV'): # * VERB  /avgVERB
		cursor.execute(f"insert ignore into lempostag(cp, lem, pos,tag,count) select cp, '*', pos, tag, sum(count) from lempostag where cp= '{name}' and pos='{s}' group by tag ")
	conn.commit()
	print ("finished submitting:", name, flush=True) 

if __name__	== '__main__':
	import fire 
	fire.Fire(index)

'''
CREATE TABLE ftsnt (
    id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    snt VARCHAR(256) not null default '',
    kps TEXT not null default '',
    src varchar(16) not null default '', 
    unique key snt (snt),
    FULLTEXT (snt, kps));

CREATE TABLE lempostag ( cp varchar(16) not null default '', lem varchar(64) not null default '',  pos varchar(32) not null default '',  tag varchar(64) not null default '', count int not null default 0, unique key uk(cp,lem,pos,tag), index attrs(cp,pos,tag)) engine=myisam;
'''