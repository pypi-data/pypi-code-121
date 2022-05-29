# 2022.4.7 cp from util/xwps.py    2022.5.27, add ratio 
import json, time, traceback, fire,sys, redis, hashlib ,socket,os,requests,re

rhost		= os.getenv("rhost", "172.17.0.1")
rport		= int(os.getenv('rport', 6379))
rdb			= int(os.getenv('rdb', 0))
redis.r		= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=True) 
redis.bs	= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=False) 
redis.ttl	= int (os.getenv("ttl", 7200) )
redis.timeout= int (os.getenv("timeout", 3) )
redis.dskhost= os.getenv("dskhost", "172.17.0.1:7095")
now			= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
trantab		= str.maketrans("，　。！“”‘’；：？％＄＠＆＊（）［］＋－ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ１２３４５６７８９０ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ", ", .!\"\"'';:?%$@&*()[]+-ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz") #str.translate(trantab)
#is_ascii    = lambda snt: ( res:=snt.translate(trantab).strip(), res.isascii() if res else False)[-1] 
valid_ratio	= lambda snt: len(re.sub(r'[\u4e00-\u9fa5]', '', snt.translate(trantab) ) ) / ( len(snt) + 0.01)  #<= ratio  # at least 70% is English

import spacy
if not hasattr(spacy, 'nlp'):
	from spacy.lang import en
	spacy.sntbr		= (inst := en.English(), inst.add_pipe("sentencizer"))[0]
	spacy.sntpid	= lambda essay: (pid:=0, [ ( pid := pid + 1 if "\n" in snt.text else pid,  (snt.text, pid))[-1] for snt in  spacy.sntbr(essay).sents] )[-1]
	spacy.sntpidoff	= lambda essay: (pid:=0, doc:=spacy.sntbr(essay), [ ( pid := pid + 1 if "\n" in snt.text else pid,  (snt.text, pid, doc[snt.start].idx))[-1] for snt in  doc.sents] )[-1]
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]

import mkf, xgecv1,score, pingyu
from en.dims import docs_to_dims
def xessay(arr:dict={"essay":"English is a internationaly language which becomes importantly for modern world. 中文In China, English is took to be a foreigh language which many student choosed to learn. They begin to studying English at a early age. They use at least one hour to learn English knowledges a day. Even kids in kindergarten have begun learning simple words. That's a good phenomenan, for English is essential nowadays. In addition to, some people think English is superior than Chinese. In me opinion, though English is for great significance, but English is after all a foreign language. it is hard for people to see eye to eye. English do help us read English original works, but Chinese helps us learn a true China. Only by characters Chinese literature can send off its brilliance. Learning a country's culture, especial its classic culture, the first thing is learn its language. Because of we are Chinese, why do we give up our mother tongue and learn our owne culture through a foreign language?"}):  
	''' asdsk:bool=True, diffmerge:bool=False,  topk:int=0, mkfbatch:int=0, gecoff:bool=True, dskhost:str="172.17.0.1:7095",  '''
	try:
		start	= time.time()
		id		= arr.get('id',arr.get('key','0'))
		essay	= arr.get("essay", arr.get('doc','')) #.strip()
		redis.r.zadd(f"tim:{id}", {'start':start})
		if not essay: return {"failed":"empty essay"}

		sntpids = spacy.sntpid(essay)  # [(snt,pid) ]
		snts	= [snt for snt,pid in sntpids ] 	#cleans  = [snt.translate(trantab) for snt in snts] # keep the same length
		ratios  = [ valid_ratio(snt) for snt in snts ]
		valids  = [ snt for snt, ratio in zip(snts, ratios) if ratio >= float(arr.get('ratio',0.6)) ] # at least 60% is English
		redis.r.zadd(f"tim:{id}", {'sntbr':time.time()}) 
		[redis.r.xadd('xsnt', {'snt':snt}) for snt in valids]  # notify:  spacy/gec 

		sntdic  = xgecv1.redis_gecsnts(valids, topk =int(arr.get('topk',0)), timeout=int(arr.get('timeout',redis.timeout) ) ) if not 'gecoff' in arr else {}
		redis.r.zadd(f"tim:{id}", {'gec':time.time()})
		if 'debug' in arr: 
			hitted_snts = [ snt for snt in valids if redis.bs.exists(f'bs:{snt}')] # pre-set by xsnt-spacy
			redis.r.hset(f"debug:{id}", "hitted-spacy-cnt", len(hitted_snts), {"id": id, "length": len(essay), "len_snts": len(snts), "len_valids": len(valids), 'ratios': json.dumps(ratios)
			, "hitted-spacy-ratio": len(hitted_snts)/(len(valids)+0.1), "hitted-gec-cnt": len([ snt for snt in valids if redis.bs.exists(f'gec:{snt}')])})

		docs	= [ ( bs := redis.bs.get(f"bs:{snt}"), doc := spacy.frombs(bs) if bs else spacy.nlp(snt))[1] for snt in valids ] 
		redis.r.zadd(f"tim:{id}", {'spacy':time.time()})
		
		sntmkf = mkf.snt_mkf(valids, docs, sntdic, ibeg_byte='ibeg_byte' in arr, diffmerge = arr.get('diffmerge', False), batch=int(arr.get('mkfbatch',0)), dskhost=redis.dskhost) 
		redis.r.zadd(f"tim:{id}", {'sntmkf':time.time()})
		[redis.r.expire(f"{name}:{id}", redis.ttl) for name in ('tim','debug')]
		
		if valids and not 'noscore' in arr: 
			score_snts = int(arr.get('score_snts', 32))
			dims = docs_to_dims(valids[0:score_snts], docs[0:score_snts]) # only top [0:score_snts] considered for scoring 
			if not 'internal_sim' in dims: dims['internal_sim'] = 0.2
			arr.update(score.dims_score(dims))
			arr['pingyu'] = pingyu.get_pingyu(dims)
			redis.r.zadd(f"tim:{id}", {'score':time.time()})

		fds = [ sntmkf.get(snt, {'feedback':{}, 'meta':{'snt':snt}}) for snt in snts ] 
		[ fd['meta'].update({"sid":i}) for i, fd in enumerate(fds) ]
		[ fd['meta'].update({"pid":sntpid[1], "snt_ori": sntpid[0]}) for sntpid, fd in zip(sntpids,fds) ]
		redis.r.zadd(f"tim:{id}", {'feedback':time.time()})
		arr["timing"] = time.time() - start

		res = {'snt': fds, "info": arr}
		if 'dims' in dir() and dims: res.update({'doc': dims})
		return res

	except Exception as ex:
		print(">>gecv1_dsk Ex:", ex, "\t|", arr)
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)
		redis.r.hset(f"debug:{id}", "ex:gecv1_dsk", json.dumps([ str(ex), traceback.format_tb(exc_traceback_obj)]) )
		#return ("exception:", ex, exc_type, exc_value, exc_traceback_obj )

def xwps(arr:dict={"essay":"English is a internationaly language which becomes importantly for modern world. 中文In China, English is took to be a foreigh language which many student choosed to learn. They begin to studying English at a early age. They use at least one hour to learn English knowledges a day. Even kids in kindergarten have begun learning simple words. That's a good phenomenan, for English is essential nowadays. In addition to, some people think English is superior than Chinese. In me opinion, though English is for great significance, but English is after all a foreign language. it is hard for people to see eye to eye. English do help us read English original works, but Chinese helps us learn a true China. Only by characters Chinese literature can send off its brilliance. Learning a country's culture, especial its classic culture, the first thing is learn its language. Because of we are Chinese, why do we give up our mother tongue and learn our owne culture through a foreign language?"}):  
	''' special for wps, 2022.4.7 '''
	arr['ibeg_byte'] = 1
	return xessay(arr) 

def xconsume(stream, group, maxlen=100000, waitms=3600000):  # dsk/mkfs , as different group , different policy, to be a more general engine version, xessay
	'''rhost=192.168.201.120 python xessay.py xconsume xessay/xwps dsk'''
	mapf = {'xessay': xessay, 'xwps': xwps}
	if not stream in mapf: 
		print (f"No func of {stream}", flush=True)
		return 
	f = mapf[stream]
	print( f(), flush=True) # warmup, to init gpu , if any 

	try:
		redis.r.xgroup_create(stream, group,  mkstream=True)
	except Exception as e:
		print(e)
		
	redis.r.xtrim(stream, maxlen) #XTRIM mystream MAXLEN ~ 1000

	consumer_name = f'consumer_{socket.gethostname()}_{os.getpid()}'
	print(f"xpws redis consumer started: {consumer_name}|{stream}|{group}| ", redis.r, flush=True)
	while True:
		item = redis.r.xreadgroup(group, consumer_name, {stream: '>'}, count=1, noack=True, block= waitms )
		try:
			if not item: break
			id,arr = item[0][1][0]  #[['_new_snt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
			redis.r.hset(f"debug:{id}", "arrkeys", len(arr), {'in_time': now()})
			redis.r.expire(f"debug:{id}", redis.ttl)

			try:
				arr['id'] = id 
				dsk = f(arr)
				res = json.dumps(dsk)
				if 'pub' in arr: redis.r.publish(arr['pub'], res)
				redis.r.lpush(f"suc:{id}", res )
				redis.r.expire(f"suc:{id}", redis.ttl) 
			except Exception as e1:
				print ("parse err:", e1, arr) 
				redis.r.lpush(f"err:{id}", json.dumps(arr))
				redis.r.expire(f"err:{id}", redis.ttl) 
				redis.r.setex(f"exception:{id}", redis.ttl, str(e1))

		except Exception as e:
			print(">>[xconsumeEx]", e, "\t|", item, "\t|",  now())

	redis.r.xgroup_delconsumer(stream, group, consumer_name)
	redis.r.close()
	print ("Quitted:", consumer_name, "\t",now())

if __name__ == '__main__':
	fire.Fire({"xconsume":xconsume, 
	'hello': lambda: xessay(), 
	'gecsnts': lambda: xgecv1.redis_gecsnts(),
	'testgec': lambda: ( redis.r.delete('gec:She has ready.'),  xgecv1.redis_gecsnts(['gec:She has ready.']) )[-1],  #rhost=192.168.201.120 python xwps.py testgec  | gec:She has ready.: She is ready.
	})