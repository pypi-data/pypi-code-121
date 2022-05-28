# 2022.3.5
from app.dmdsk import *
from collections import defaultdict, Counter

def run(rid=2575450):

	st.title("rid feedback lists")
	si  = Counter()
	for mkf in rid_mkfs( int(rid)):
		for k,v in mkf['feedback'].items():
			if v["cate"].startswith("e_") or v["cate"].startswith("w_"):
				si.update({v["cate"]:1})

	df = pd.DataFrame([(s,i) for s, i in si.most_common()],columns=["feedback","freq"]) 
	st.write(df) 

if __name__ == '__main__': run()