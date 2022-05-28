#2022.4.16  xstream consumers 
# docker run --name redis --restart=always -d -p 172.17.0.1:6379:6379 -v $PWD/redis-data:/data redis redis-server --notify-keyspace-events KEA --save ""  --appendonly no
# docker run -d --name redis -p 172.17.0.1:6379:6379 redislabs/redisearch:2.4.3
# docker run -d --name redis -p 172.17.0.1:6379:6379 redislabs/redismod
# docker run -d --restart=always --name=webdis --env=REDIS_HOST=172.17.0.1 --env=REDIS_PORT=6379 -e VIRTUAL_PORT=7379 -p 7379:7379 wrask/webdis
# docker run -d --rm --name redisUI -e REDIS_1_HOST=172.17.0.1 -e REDIS_1_NAME=rft -e REDIS_1_PORT=6379 -p 26379:80 erikdubbelboer/phpredisadmin:v1.13.2
# cola, move redis consumer insider
# docker swarm , start multiple instance, without using supervisor
# python -m stream 
import json,os,time,redis, socket,requests,en, hashlib,traceback,sys
md5text	= lambda text: hashlib.md5(text.strip().encode("utf-8")).hexdigest()
getdoc	= lambda snt:  ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setex(f"bs:{snt}", redis.ttl, spacy.tobs(doc)) if bs is None else None )[1]

def spacybs(id, arr): #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
	''' python -m stream xsnt spacybs '''
	if 'snt' in arr:
		snt = arr.get('snt','') 
		bs  = redis.bs.get(f"bs:{snt}")
		if bs is None: 
			doc = spacy.nlp(snt)
			redis.bs.setex(f"bs:{snt}", redis.ttl, spacy.tobs(doc))
		else:
			redis.r.expire(f"bs:{snt}", redis.ttl) 
		redis.r.publish('sntbs-is-ready', json.dumps(arr)) # notify bs is parsed ready 

def init(): # for debug only 
	import platform
	redis.ttl	= 7200
	redis.debug = True
	if platform.system().lower() == 'windows':
		redis.r		= redis.Redis(decode_responses=True) 
		redis.bs	= redis.Redis(decode_responses=False) 
	else: 
		redis.r		= redis.Redis("172.17.0.1", decode_responses=True) 
		redis.bs	= redis.Redis("172.17.0.1", decode_responses=False) 

def wordidf(msg): # listen: sntbs-is-ready
	''' python -m stream sntbs-is-ready wordidf '''
	from dic import word_idf 
	xarr = json.loads(msg) 
	if 'rid' in xarr and 'snt' in xarr: 
		rid = xarr['rid'] 
		doc = getdoc(xarr['snt'])
		for t in doc: 
			if t.text.lower() in word_idf.word_idf:  
				redis.r.zadd(f"rid-{rid}:word_idf", { t.text.lower(): word_idf.word_idf[t.text.lower()] })
			if t.lemma_ in word_idf.word_idf:  # add vp later 
				redis.r.zadd(f"rid-{rid}:{t.pos_}", { t.lemma_: word_idf.word_idf[t.lemma_] })

def terms(msg):
	''' added 2022.4.16 '''
	xarr = json.loads(msg) 
	if 'rid' in xarr and 'uid' in xarr and  'snt' in xarr:  #if not redis.r.hexists(f"snt:rid-{rid}:uid-{uid}={snt}", "lems"):
		rid,uid, doc = xarr['rid'], xarr['uid'], getdoc(xarr['snt'])
		lems = [ f"{t.pos_}_{t.lemma_}" for t in doc  if t.pos_ not in ('PUNCT')]
		trps = [ f"{t.dep_}_{t.head.pos_}_{t.pos_}:{t.head.lemma_} {t.lemma_}" for t in doc if t.pos_ not in ('PUNCT')]
		stype = "simple" if len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "complex" 
		if len([t for t in doc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0 : stype = stype + ",compound"
		xarr.update({"rid": rid, "uid": uid, "snt": doc.text, "lems": ','.join(lems), "trps": ','.join(trps), "tags": stype})
		redis.r.hset(f"snt:rid-{rid}:uid-{uid}={doc.text}", "rid", rid, xarr )

def cola(xid, xarr):
	''' '''
	if 'rid' in xarr and 'uid' in xarr and  'snt' in xarr:  
		rid,uid, snt = xarr['rid'], xarr['uid'], xarr['snt']
		if not snt: return 
		res = requests.get("http://cola.werror.com/cola/get", params={"snt":snt}).json()
		redis.r.hset(f"snt:rid-{rid}:uid-{uid}={snt}", "cola", float(res))
		redis.r.zadd(f"rid-{rid}:snt_cola", { f"{uid},{xid}:{snt}": float(res) })  # xid = tm 

def essay_plusone(xid, arr:dict={"rid":100876, "uid":1001, "tid":0, "type":"essay", "essay":"She has ready. It are ok."}): 
	''' xadd   {label = text, rid, uid,  tm , snts(json.dumps), tid, type='essay' }   -- xid  ''' 
	rid,uid,essay	= arr.get('rid', '0'), arr.get('uid', '0'),arr.get('essay','')
	essaymd5		= md5text(essay) 
	borntm			= int( int(xid.split('-')[0])/1000 )

	latest			= redis.r.hget(f"rid-{rid}:uid_latest", uid) #rid=100876:uid_xid  hash    {uid: xid}    xid = 1649487647926-3,  a tm value , last updated, xid -> snts   |  NOT add duplicated items 
	if latest is not None and latest.startswith(essaymd5): 
		print(f"duplicated content: {essay}")
		return  # unchanged  	if latest is None  or  latest != essaymd5: 
	redis.r.hset(f"rid-{rid}:uid_latest", uid, f"{essaymd5},{xid}")
	if latest: redis.r.hset(f"essay:rid-{rid}:{latest.split(',')[-1]}", "latest", 0) # only one is marked as 'latest' 

	snts = spacy.snts(essay)
	arr.update({'borntm':borntm, 'latest':1})
	redis.r.hset(f"essay:rid-{rid}:{xid}", "snts", json.dumps(snts), arr ) # hash mirror of xrid-{rid}, ftessay
	redis.r.zadd(f"rid-{rid}:zlogs", {f"{uid},{len(snts)}": float(xid.split('-')[0])}) #rid=100876:logs	 zadd    {f"{uid}-{action}": tm }
	
	[ redis.r.xadd('xsnt', {'snt':snt, 'uid':uid,'rid':rid, 'xid':xid, 'borntm':borntm}) for snt in snts ]  # notify: ftsnt
	redis.r.xadd('xsnts', {'snts': json.dumps(snts), 'uid':uid,'rid':rid, 'xid':xid, 'borntm':borntm})  # gecsnts, with rid/uid
	print ("finished:", snts) 

def getgecs(snts, host="gpu120.wrask.com", port=6379, timeout=5): # put into the ufw white ip list 
	''' '''
	if not hasattr(getgecs, 'r'): getgecs.r = redis.Redis(host=host,port=port, decode_responses=True)
	id  = getgecs.r.xadd("xsnts", {"snts":json.dumps(snts)})
	res	= getgecs.r.blpop([f"suc:{id}",f"err:{id}"], timeout=timeout)
	return {} if res is None else json.loads(res[1])

def todsk(id, arr): 
	''' 2022.4.11 '''
	from dsk import mkf
	snts	= json.loads(arr.get('snts','[]'))
	gecs	= redis.r.mget( [f"gec:{snt}" for snt in snts])
	newsnts = [snt for snt, gec in zip(snts, gecs) if gec is None ]
	sntgec  = getgecs(newsnts) 
	[ redis.r.setex(f"gec:{snt}", redis.ttl, gec) for snt, gec in sntgec.items()]

	rid,uid,xid	= arr.get('rid','0'),  arr.get('uid','0'),  arr.get('xid','0')
	dsk	 = mkf.sntsmkf( [ (snt,gec) for snt,gec in sntgec.items()], dskhost=redis.dskhost, asdsk=True, getdoc= lambda snt: ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt))[1] )
	redis.r.setex(f"dsk:{xid}", redis.ttl, json.dumps(dsk)) 

	score = float(dsk.get('info',{}).get("final_score",0))
	redis.r.hset(f"essay:{xid}", "score", score , dsk.get('doc',{}) ) # awl, ast, .. 
	redis.r.zadd(f"rid-{rid}:essay_score", {uid: score} ) # overwriting 

	for mkf in dsk.get('snt',[]):  #for snt, mkf in sntgec_mkfs(sntgec, arr):
		snt = mkf.get('meta',{}).get('snt','')
		redis.r.setex(f"mkf:{snt}", redis.ttl, json.dumps(mkf))
		if not redis.r.hexists(f"snt:rid-{rid}:uid-{uid}={snt}", "cates"):
			cates = [ v['cate'][2:] for k,v in mkf.get('feedback',{}).items() if v['cate'].startswith("e_") or v['cate'].startswith("w_") ]
			redis.r.hset(f"snt:rid-{rid}:uid-{uid}={snt}", "cates", ','.join(cates))
			for cate in cates: 
				redis.r.zincrby(f"rid-{rid}:cate", 1, cate) # snt.nv_agree
				redis.r.zincrby(f"rid-{rid}:catetop", 1, cate.split('.')[0]) # snt

def item(xid, arr:dict={"rid":"230537", "uid":'1001', "tid":0, "type":"fill", "label":"open the door"}): 
	'''  ''' 
	rid,uid,tid,label	= arr.get('rid', '0'), arr.get('uid', '0'),arr.get('tid','0'),arr.get('label','')
	borntm			= float( int(xid.split('-')[0])/1000 )
	xidlatest		= redis.r.hget(f"rid-{rid}:xid_latest", f"{uid},{tid}") 
	if xidlatest: redis.r.hset(f"item:{xidlatest}", "latest", 0) # only one is marked as 'latest' 
	redis.r.hset(f"rid-{rid}:xid_latest", f"{uid},{tid}", xid)

	score = redis.r.hget(f"rid-{rid}:tid-{tid}", label)
	if score is None: score = 0

	arr.update({'borntm':borntm, 'latest':1, "score": float(score)})
	redis.r.hset(f"item:{xid}", "borntm", borntm, arr )  # mirror data of the xitem 
	redis.r.zadd(f"rid-{rid}:zlogs", {json.dumps(arr): borntm}) 
	# cache , for a quicker show 
	redis.r.hset(f"rid-{rid}:uid-{uid}:tid_label", tid,  label )
	redis.r.hset(f"rid-{rid}:tid-{tid}:uid_label", uid,  label )

if __name__ == '__main__':
	init()
	essay_plusone('1583928357124-0')