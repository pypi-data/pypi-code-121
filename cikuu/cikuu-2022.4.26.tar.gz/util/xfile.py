
import redis, fire,json

def run(infile, host='127.0.0.1', port=6379, timeout=10):
	r	= redis.Redis(host=host,port=port, decode_responses=True)
	for line in open(infile, 'r').readlines():
		arr = json.loads(line.strip())
		id = r.xadd('xwps', {'essay':arr.get('doc','')})
		print ( "id:", id,flush=True)
		res	= r.blpop([f"suc:{id}",f"err:{id}"], timeout=timeout)
		print (res if res is not None else f"{id} result is None") 

if __name__ == '__main__':
	fire.Fire(run)
