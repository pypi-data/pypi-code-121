# 2022.3.5
from app.dmdsk import *
from collections import Counter

def run(rid=2575450):
	
	st.title("rid trplist")
	pos = st.sidebar.selectbox('搭配',    ('dobj_VERB_NOUN', 'amod_NOUN_ADJ', 'nsubj_VERB_NOUN'))

	si  = Counter()
	rel,gov,dep = pos.strip().split("_")[0:3]
	for eidv in eidv_list(int(rid)):
		for doc in eidv_docs(eidv):
			[ si.update({f"{t.head.lemma_} {t.lemma_}":1}) for t in doc if t.dep_ == rel and t.pos_ == dep and t.head.pos_ == gov ]

	df = pd.DataFrame([(s,i) for s, i in si.most_common()],columns=["collocation","freq"]) 
	st.write(df) 

if __name__ == '__main__': run()