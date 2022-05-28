# 2022.5.2
import streamlit as st
import redis,platform,time,json, random

if not hasattr(redis, 'r'): redis.r	= redis.Redis(host='127.0.0.1' if platform.system().lower() == 'windows' else '172.17.0.1', port=6379, decode_responses=True) 

def run():
	st.header("data mocking")
	st.sidebar.write( "select") 
	rids = st.text_input('rids', '10086,230537').strip().split(',')
	uids = st.text_input('uids', 'AA,BB,CC,DD,EE,FF,GG,HH,II,JJ,KK,LL,MM,NN').strip().split(',')
	tids = st.text_input('tids', '1,2,3,4,5,6,7,8,9,10').strip().split(',')
	labels = st.text_input('labels', 'A,B,C,D').strip().split(',')
	name = st.sidebar.text_input('xname', 'xrid:test')
	key = st.sidebar.text_input('key', 'label')

	sleep = st.sidebar.slider("sleeping time", 0, 10, 0)
	loop = st.sidebar.slider("loop count", 0, 100, 20)
	reset = st.sidebar.checkbox('reset', True)

	if reset: [ redis.r.delete(k) for rid in rids for k in redis.r.keys(f"rid-{rid}:tid-*")] # keep config
	nrid, ntid, nuid, nlabel = len( rids),len( tids), len( uids ) , len(labels) 
	
	res = st.empty() 
	if st.sidebar.button("submit"):
		for i in range(loop):
			rid = rids[random.randint(0, nrid - 1)]
			tid = tids[random.randint(0, ntid - 1)] 
			uid = uids[random.randint(0, nuid - 1)] 
			label = labels[random.randint(0, nlabel -1 )] 
			xid = redis.r.xadd(name, {"rid":rid, "tid":tid, 'uid':uid, key: label})
			if sleep > 0: time.sleep( random.random() * sleep) 
			res.write({"xid":xid, "rid":rid, "tid":tid, "uid":uid, key:label})

	# added 2022.5.26
	st.sidebar.markdown('''---''')
	span = st.sidebar.slider("sleep span seconds", 0, 10, 5)
	xname = st.sidebar.text_input('essay xname', 'xtodsk:rid-tid-uid')
	if st.sidebar.button("mock essay"): #xadd xtodsk:rid-tid-uid * essay_or_snts "She has ready. It are ok."
		from dic.essays import essays 
		import en 
		sntslist = [ spacy.snts(d['essay']) for d in essays]
		for i in range(loop): 
			for d, snts in zip(essays, sntslist):
				id = redis.r.xadd(xname, {"rid": d.get('rid', 0), "uid": d.get('uid', 0), "essay_or_snts":" ".join( snts[0:i+1])})
			res.write(f"** loop={i}, {id}, " + time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time())) )
			time.sleep(span)
		st.sidebar.write("finished")

if __name__ == '__main__': run()