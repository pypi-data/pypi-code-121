# 2022.3.5
from app.dmdsk import *
from collections import Counter
import requests

@st.cache
def ref_sum(pos):
	return  requests.get(f"http://dic.werror.com/kpssi/si?key=SUM%3A{pos}").json() #1203699

def run(rid=2575450):

	st.title("rid wordlist")
	pos = st.sidebar.selectbox('词性',    ('VERB', 'NOUN', 'ADJ','ADV'))

	si  = Counter()
	for eidv in eidv_list(int(rid)):
		for doc in eidv_docs(eidv):
			[ si.update({t.lemma_:1}) for t in doc if t.pos_ == pos ]
	st.sidebar.write(si)
	st.write(si)
	
	res = requests.post("http://dic.werror.com/kpssi/keyness", json={ f"{pos}:{s}":i for s,i in si.items()}, params={"ref_sum": ref_sum(pos)}).json()
	
	#df = pd.DataFrame(res,columns=["word","freq","corpus_freq", "keyness"]) 
	#st.write(df) 

if __name__ == '__main__': run()