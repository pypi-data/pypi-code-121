# 2022-3-6 docker run -it --rm -e file=gram2.marisa -p 8080:80 wrask/grami uvicorn grami:app --host 0.0.0.0 --port 80 --reload
import uvicorn,json,os,collections, marisa_trie
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

file	= os.getenv('file', "gram2.marisa") # 1,2,3,4,5
model	= marisa_trie.BytesTrie().load( file )
toint	= lambda bs:  int.from_bytes(bs, byteorder='little', signed=True)
gram2i	= lambda gram: int.from_bytes(model.get(gram, [b'\x00\x00\x00\x00'])[0], byteorder='little', signed=True)
app		= FastAPI()

@app.get('/')
def home(): return HTMLResponse(content=f"<h2> grami api, i=1,2,3,4,5 </h2> <a href='/docs'> docs </a> | <a href='/redoc'> redoc </a> <br>2022-3-6 ")
@app.get('/grami/gramcnt')
def grami_gramcnt(gram: str = 'overcome difficulty'): return gram2i(gram)

@app.post('/grami/gramscnt')
def grami_gramscnt(grams: list = ['overcome difficulty','overcame difficulty','overcame difficulty***']): 
	return { gram.strip(): gram2i(gram.strip()) for gram in grams }

@app.get('/grami/startswith')
def grami_startswith(prefix: str = 'overcome diffi', topk:int=10): 
	words = [ (k,toint(v)) for k,v in list(model.iteritems(prefix))] # iterkeys
	return collections.Counter(dict(words)).most_common(topk)

if __name__ == '__main__': 
	print (grami_gramscnt())
	print ( grami_startswith()) 

'''
docker run -it --name tt --rm python:3.8-slim  /bin/bash 

# 2021-10-24  docker run -e VIRTUAL_HOST=gramx.wrask.com -e pymain=http://cikuu.werror.com/app/gramx/gramx.py -v /cikuu/model/gramx/:/cikuu/model/gramx/ --rm --name gramx wrask/spacy:3.0.1
# docker run -it -e VIRTUAL_HOST=gram2.wrask.com -v /cikuu/model/gramx:/gramx --rm --name gram2 wrask/grami python /grami.py 80 --channel sntarr --redis_host 172.17.0.1  --redis_port 6664 --redis_db 0 --i 2 --path gramx --toks_field toks --snt_field snt

def run( wwwport, channel='sntarr', redis_host=None,  redis_port=6664, redis_db=0, i=2, path='gramx', toks_field='toks', snt_field='snt'):

	redis.gram	= marisa_trie.BytesTrie().load(f"/{path}/gram{i}.marisa")
	redis.i		=  i
	redis.toks_field = 'toks'
	redis.snt_field = 'snt'
	if redis_host: 
		redis.r	= redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True) 
		print (f'start to listen: {channel}', redis.r, redis.gram, flush=True)
		ps = redis.r.pubsub(ignore_subscribe_messages=True)  #https://pypi.org/project/redis/
		ps.subscribe(**{channel:func})
		thread = ps.run_in_thread(sleep_time=0.001) #thread.stop()
	else: 
		redis.r = None

	print(gramcnt("hello world"), flush=True)
	uvicorn.run(app, host='0.0.0.0', port=wwwport) #	uvicorn.run(app, host='0.0.0.0', port=80)
'''