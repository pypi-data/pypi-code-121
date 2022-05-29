# 2022.3.4  /home/ubuntu/.local/lib/python3.8/site-packages/uvirun/nlp.py
import json,fire,os
from uvirun import * 
import en #from en import nlp,snts

@app.get("/nlp/terms")
def nlp_terms(text:str="The quick fox jumped over the lazy dog. The justice delayed is justice denied."):
	''' for sqlite indexing, 2022.3.4 '''
	tdoc = spacy.nlp(text)
	arr = []
	for sent in tdoc.sents: 
		doc = sent.as_doc()
		arr.append( { "snt": sent.text, 
		"tokens": [ {"id": t.i,"offset":t.idx, "word": t.text, "lemma":t.lemma_, "is_stop":t.is_stop, "parent": -1, "np_root": False, "pos": t.pos_, "tag": t.tag_, "dep": t.dep_,"text_with_ws": t.text_with_ws, "head": t.head.i , "sent_start": t.is_sent_start, "sent_end":t.is_sent_end}  for t in doc], 
		"triples": [ {"id":t.i,"offset":t.idx, "rel": t.dep_, "govlem":t.head.lemma_, "govpos": t.head.pos_, "deplem": t.lemma_, "deppos": t.pos_} for t in doc], 
		"chunk": [ {"id": np.start, "offset": doc[np.start].idx, "lem": doc[np.end-1].lemma_, "chunk":np.text, "end":np.end} for np in doc.noun_chunks], 
		} )
	return arr 

@app.get("/nlp/sntbr")
def nlp_sntbr(text:str="The quick fox jumped over the lazy dog. The justice delayed is justice denied.", trim:bool=True):
	'''  '''
	return spacy.snts(text, trim) 

@app.post("/nlp/wordidf")
def nlp_wordidf(words:list=["niche","dilemma","consider","consider**"], default_idf:float=0):
	'''  '''
	from dic.word_idf import word_idf 
	return  { w: word_idf.get(w, default_idf) for w in words}

def run(port):
	uvicorn.run(app, host='0.0.0.0', port=port)

if __name__ == "__main__":  
	fire.Fire(run)
	#uvicorn.run(app, host='0.0.0.0', port=18002)