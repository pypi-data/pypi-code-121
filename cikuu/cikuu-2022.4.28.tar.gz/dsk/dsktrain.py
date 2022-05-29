# 22-4-12  train essay -> dsk 
import json, fire, en 
from collections import Counter

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def getgecs(snts, host="127.0.0.1", port=6379, timeout=5): # put into the ufw white ip list 
	''' '''
	import redis
	if not hasattr(getgecs, 'r'): getgecs.r = redis.Redis(host=host,port=port, decode_responses=True)
	id  = getgecs.r.xadd("xsnts", {"snts":json.dumps(snts)})
	res	= getgecs.r.blpop([f"suc:{id}",f"err:{id}"], timeout=timeout)
	return {} if res is None else json.loads(res[1])

def train(infile, outfile=None, dskhost='127.0.0.1:7095'): 
	''' train essay -> dsk , 2022.4.12  '''
	from dsk import mkf 
	if not outfile: outfile = infile + ".dsk" 
	print ("start to load:", infile, flush=True) 
	with open(outfile, 'w') as fw: 
		for line in readline(infile): 
			try:
				arr = json.loads(line.strip().replace(", null,", ", '',") )
				if not arr : continue 
				essay = arr.get('essay','') 
				snts =  spacy.snts(essay) 
				sntgec = getgecs(snts) 
				dsk	 = mkf.sntsmkf( [(snt, sntgec.get(snt,snt)) for snt in snts], dskhost=dskhost, asdsk=True )
				fw.write(json.dumps(dsk) + "\n") 
			except Exception as e:
				print("ex:", e, line)
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)
	print ("finished:", infile, outfile,  flush=True) 

if __name__ == '__main__': 
	fire.Fire(train) 

def parse(infile, outfile=None, gechost="127.0.0.1:7002", dskhost='127.0.0.1:7095'): 
	# parse eev dumped file, one line, one json 
	if not outfile: outfile = infile + ".dsk" 
	print ("start to load:", infile, flush=True) 
	with open(outfile, 'w') as fw: 
		for line in readline(infile): 
			try:
				arr = json.loads(line.strip().replace(", null,", ", '',") )
				if not arr : continue 
				arr['rid'] = arr.get('request_id',0)
				dsk = requests.post(f"http://{gechost}/gec/dsk?dskhost={dskhost}", json=arr).json()
				fw.write(json.dumps(dsk) + "\n") 
				#submit_hdsk(dsk, arr.get('request_id',0), arr.get("user_id",0), arr.get('essay_id',0), arr.get('version',0) ) 
			except Exception as e:
				print("ex:", e, line)
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)

	print ("finished:", infile, outfile,  flush=True) 