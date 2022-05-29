# 2022.3.27
import fire,json,os,collections, sqlite3
from tqdm import tqdm 

class util(object):
	def __init__(self, dbfile): 
		self.dbfile = dbfile 
		self.conn	= sqlite3.connect(dbfile, check_same_thread=False)  
		self.conn.execute('PRAGMA synchronous=OFF')
		self.conn.execute('PRAGMA case_sensitive_like = 1')

	def load(self) :
		''' python spider.py load --dbfile spider-ak.spacybs '''
		import redis 
		r = redis.Redis(host='127.0.0.1', port=9221, db=0, decode_responses=False)
		print ("started:", self.dbfile, r , flush=True)
		for row in self.conn.execute("select * from spacybs").fetchall(): 
			r.setnx(str.encode(row[0]), row[1])
		print ("finished:", self.dbfile)

	def save(self) :
		''' python spider.py save --dbfile spider.spacybs '''
		import redis 
		r = redis.Redis(host='127.0.0.1', port=9221, db=0, decode_responses=False)
		print ("started:", self.dbfile, r , flush=True)
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS spacybs (key varchar(512) PRIMARY KEY, value blob)')
		for key in r.scan_iter("*"):
			snt = bytes.decode(key)
			v =r.get(key)
			self.conn.execute(f"insert or ignore into spacybs(key, value) values(?,?)", (snt, v))
		self.conn.commit()
		print ("finished saving: ", self.dbfile)

	def load_doc(self, infile) :
		''' ''' 
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS doc (arr MEDIUMTEXT)') # { filename, doc,  snts , 
		for line in open(infile,'r').readlines():
			line = line.strip()
			if not line: continue
			arr = json.loads(line) 
			id = arr['id']
			self.conn.execute(f"insert or ignore into doc(rowid, arr) values(?,?)", (id, line))
		self.conn.commit()
		print("finished:", infile, dbfile, "\t | using:", time.time() - start)

	def dump_doc(self, outfile) :
		''' python spider.py dump_doc --dbfile spider-aa.spacybs spider-aa.doc-json 
		2022.3.27
		''' 
		with open(outfile,'w') as fw: 
			for row in self.conn.execute("select arr,snts from doc").fetchall():
				arr = json.loads(row[0])
				snts = json.loads(row[1])
				dic = {"id": arr[0], "domain": arr[2], "description": arr[3], "title": arr[4], "url": arr[5], "doc": arr[6], "chanel": arr[7], "tag":arr[8], "pub_date":arr[9], "snts": snts}
				fw.write(json.dumps(dic) + "\n")
		print ("fninshed:", outfile) 

if __name__ == "__main__":  
	fire.Fire(util)

'''
ubuntu@essaydm-jukuu-com:/ftp/spider$ sqlite3 spider.sqlite 
SQLite version 3.31.1 2020-01-27 19:55:54
Enter ".help" for usage hints.
sqlite> .schema
CREATE TABLE `doc` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `did` INTEGER,
  `domain` varchar(255),
  `description` text,
  `title` varchar(500),
  `url` varchar(255),
  `doc_txt` text,
  `chanel` varchar(255),
  `tag` varchar(500),
  `pub_date` varchar(100)
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE INDEX domain ON doc(domain);
CREATE INDEX url ON doc(url);

ubuntu@VM-248-3-ubuntu:/data/c4data/5$ scp *.gz ubuntu@essaydm.jukuu.com:/ftp/c4/5

CREATE TABLE spacybs (key varchar(512) PRIMARY KEY, value blob);
CREATE TABLE doc (did int PRIMARY KEY, arr text, snts text) without rowid;



'''