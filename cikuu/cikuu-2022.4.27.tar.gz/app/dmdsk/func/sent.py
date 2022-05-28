# 2022.3.5
from app.dmdsk import *
from collections import defaultdict, Counter

def run(rid=2575450):

	st.title("rid sent search")
	#rid = st.sidebar.text_input("作文号", "2579654") #2578570
	term = st.sidebar.text_input("term", "VERB:make") #dobj_VERB_NOUN:make effort

	sntids = redis.dm.smembers(f"rid:{rid}:{term}") #'153009791-2:6',
	snts = {}
	for sid in sntids: 
		snts.update( {redis.dm.hget(f"rid:{rid}:snts", sid): sid} )
		
	st.write(snts) 

if __name__ == '__main__': run()