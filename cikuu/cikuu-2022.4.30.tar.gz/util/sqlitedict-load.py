# 2022.3.13
import json, fire 
import zlib, pickle, sqlite3
from sqlitedict import SqliteDict

# The database is automatically closed when leaving the with section.
# Uncommited objects are not saved on close. REMEMBER TO COMMIT!

def readline(infile, sepa=None):
	with open(infile, 'r') as fp: #,encoding='utf-8'
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def my_encode(obj):
	return sqlite3.Binary(zlib.compress(pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)))

def my_decode(obj):
	return pickle.loads(zlib.decompress(bytes(obj)))

def run(infile, outfile): 
	''' '''
	with SqliteDict(outfile, encode=my_encode, decode=my_decode) as db:
		for line in readline(infile): 
			arr = line.strip().split("\t")
			if len(arr) == 2 : 
				db[ arr[0] ] = arr[1] 
		db.commit() 
	print ("finished", infile, outfile)

if __name__ == '__main__': 
	fire.Fire(run) 