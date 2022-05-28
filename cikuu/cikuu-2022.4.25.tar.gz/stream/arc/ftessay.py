# 2022.4.10 python __main__.py xessay --group ftessay 
import json, time, sys, redis, socket, en, os,hashlib
md5text	= lambda text: hashlib.md5(text.strip().encode("utf-8")).hexdigest()

def submit(xid, arr:dict={"rid":100876, "uid":1001, "tid":0, "type":"essay", "essay":"She has ready. It are ok."}): 
	''' xadd   {label = text, rid, uid,  tm , snts(json.dumps), tid, type='essay' }   -- xid  ''' 

	rid,uid,essay	= arr.get('rid', '0'), arr.get('uid', '0'),arr.get('essay','')
	essaymd5		= md5text(essay) 
	borntm			= int( int(xid.split('-')[0])/1000 )

	#if redis.r.hget('realtime', rid):  # rid is realtime type, submit essay every 5 seconds , need check duplicated
	latest			= redis.r.hget(f"rid-{rid}:uid_latest", uid) #rid=100876:uid_xid  hash    {uid: xid}    xid = 1649487647926-3,  a tm value , last updated, xid -> snts   |  NOT add duplicated items 
	if latest is not None and latest.startswith(essaymd5): return  # unchanged  	if latest is None  or  latest != essaymd5: 
	redis.r.hset(f"rid-{rid}:uid_latest", uid, f"{essaymd5},{xid}")
	if latest: redis.r.hset(f"essay:rid-{rid}:{latest.split(',')[-1]}", "latest", 0) # only one is marked as 'latest' 

	snts = spacy.snts(essay)
	arr.update({'borntm':borntm, 'latest':1})
	redis.r.hset(f"essay:rid-{rid}:{xid}", "snts", json.dumps(snts), arr ) # hash mirror of xrid-{rid}, ftessay
	redis.r.zadd(f"rid-{rid}:zlogs", {f"{uid},{len(snts)}": float(xid.split('-')[0])}) #rid=100876:logs	 zadd    {f"{uid}-{action}": tm }
	
	[ redis.r.xadd('xsnt', {'snt':snt, 'uid':uid,'rid':rid, 'xid':xid, 'borntm':borntm}) for snt in snts ]  # notify: ftsnt
	redis.r.xadd('xsnts', {'snts': json.dumps(snts), 'uid':uid,'rid':rid, 'xid':xid, 'borntm':borntm})  # gecsnts, with rid/uid

def process(item): #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
	''' 2022.4.10 '''
	for stm_arr in item : #[['xsnt', [('1583928357124-0', {'snt': 'hello worlds'})]]]
		if stm_arr[0].startswith('xessay'): # xsnt, xsntspacy
			for id,arr in stm_arr[1]: 
				try:
					submit(id, arr) 
				except Exception as e:
					print ("parse err:", e, id, arr) 

if __name__ == '__main__':
	redis.r		= redis.Redis(decode_responses=True) 
	redis.bs	= redis.Redis(decode_responses=False) 
	redis.ttl	= 7200
	process([['xessay', [('1583928357124-0', {"eid": 4011628, "rid": 230537, "author_id": 0, "internal_idx": 0, "title": "The important day", "essay": "My birthday is important to me when I was 15 years old. \n That day, I got up early due to the very looking forward to a happy day, I made three bowl of noodles and eggs to every one in my family. My father and mother finished eating and didn't say a word, I was very sad. After went home at noon. I watched my favorite TV show as usual, but my parents robbed my remote control, I was really very sad, I wanted to say today was my birthday. You not only don't Send me gift, still do this to me, I asked them what day is today, my mother said that today is the weekend. I was angry to go to classmates's house to play. I silently drop down of tears. I went home until parents call me, they said something happened. So I ran home in a hurry, when I opened the door, a beautiful cake appeared in front of me. A table of delicious food and a great bottle of red wine. My mother set me down and Dad showed me a very beautiful teddy bear with a mobile phone in its hands. Suddenly, my anger subsided entirely on them. \n This is the most important day to me. me. Parents gave me too much surprise and gave my childhood of precious memories. I love my parents.", "essay_html": "", "tm": "", "uid": 913292, "sent_cnt": 0, "token_cnt": 0, "len": 1151, "ctime": 1369563574, "stu_number": "2012020714", "stu_name": "\u59dc\u71d5", "stu_class": "1226", "type": 0, "score": 78.1673, "qw_score": 0.0, "sy_score": 0.0, "pigai": "", "pigai_time": 0, "gram_score": 0.0, "is_pigai": 1, "version": 2, "cate": 0, "src": "", "tid": 0, "fid": 0, "tag": "", "is_chang": 0, "jianyi": "", "anly_cnt": 1, "mp3": ""})]]])
