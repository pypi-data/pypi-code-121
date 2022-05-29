# 2022.2.9, http://verbs.colorado.edu/verb-index/vn/consider-29.9.php#consider-29.9-1-1-1
import spacy, traceback, sys
from spacy.matcher import Matcher
if not hasattr(spacy,'nlp'): spacy.nlp	= spacy.load('en_core_web_sm') #if not 'nlp' in dir(): nlp	= spacy.load('en_core_web_sm')  

matcher	 = Matcher(spacy.nlp.vocab)  # :1 , verb's offset 
NP_start = {"ENT_TYPE": "NP", "IS_SENT_START": True}
VERB	 = {"POS": {"IN": ["VERB"]}}
NOUN	 = {"POS": {"IN": ["NOUN","PRON","PROPN"]}}
PUNCT	 = {"IS_PUNCT": True}

matcher.add("NP V:1", [[NP_start,VERB, PUNCT]])
matcher.add("NP of NP V:3", [[ NP_start,{"LEMMA": "of"}, {"ENT_TYPE": "NP"}, VERB,PUNCT]], greedy ='LONGEST')

matcher.add("NP V NP:1", [[NOUN,VERB, NOUN,{"POS": {"IN": ["PUNCT"]}}]], greedy ='LONGEST')
matcher.add("NP V NP ADJ:1", [[NOUN,VERB, NOUN,{"POS": {"IN": ["ADJ"]}}]], greedy ='LONGEST')
matcher.add("NP V NP NP:1", [[NOUN,VERB, NOUN,NOUN]], greedy ='LONGEST')
matcher.add("NP V NP-Dative NP:1", [[NOUN,VERB, {"DEP": {"IN": ["dative"]}},NOUN]], greedy ='LONGEST')

matcher.add("NP V NP PP:1", [[NOUN,VERB, NOUN,{"DEP": {"IN": ["prep"]}}]], greedy ='LONGEST')
matcher.add("NP V NP PP PP:1", [[NOUN,VERB, NOUN,{"DEP": {"IN": ["prep"]}}, NOUN,{"DEP": {"IN": ["prep"]}}, NOUN]], greedy ='LONGEST')

matcher.add("NP V S_ING:1", [[NOUN,VERB, {"TAG": {"IN": ["VBG"]}}]], greedy ='LONGEST')
matcher.add("NP V whether/how S_INF:1", [[NOUN,VERB, {"LEMMA": {"IN": ["whether","how"]}}, {"LEMMA": {"IN": ["to"]}}, VERB]], greedy ='LONGEST')
matcher.add("NP V NP to be NP:1", [[NOUN,VERB, {"LEMMA": {"IN": ["to"]}}, {"LEMMA": {"IN": ["be"]}}, NOUN]], greedy ='LONGEST')
matcher.add("NP V that/how S:1", [[NOUN,VERB, {"LEMMA": {"IN": ["that","how"]}, "OP":"*"}, NOUN, {"POS": {"IN": ["AUX","PART"]}, "OP":"*"},{"DEP": {"IN": ["ccomp"]}}]], greedy ='LONGEST') #They considered that he was the professor.
matcher.add("NP V whether/if S:1", [[NOUN,VERB, {"LEMMA": {"IN": ["whether","if"]}}, NOUN,{"POS": {"IN": ["AUX","PART"]}, "OP":"*"}, {"DEP": {"IN": ["ccomp"]}}]], greedy ='LONGEST') #He considered whether he should come.
matcher.add("NP V what S:1", [[NOUN,VERB, {"LEMMA": {"IN": ["what"]}}, NOUN,{"POS": {"IN": ["AUX","PART"]}, "OP":"*"}, {"DEP": {"IN": ["ccomp"]}}]], greedy ='LONGEST') 
matcher.add("NP V what S_INF:1", [[NOUN,VERB, {"LEMMA": {"IN": ["what"]}}, {"LEMMA": {"IN": ["to"]}},VERB]], greedy ='LONGEST') 

def merge_np(doc):
	with doc.retokenize() as retokenizer:
		for np in doc.noun_chunks:
			attrs = {"tag": np.root.tag, "dep": np.root.dep, "ent_type": "NP"}
			retokenizer.merge(np, attrs=attrs) 
	return doc

def skenp(doc, tag="_NP"): # added 2022.3.22, for skevec
	merge_np(doc) # transform doc , finally to be called 
	return " ".join([tag if t.ent_type_ == 'NP' else t.text for t in doc])

def merge_n_of_n(doc):
	if not hasattr(merge_n_of_n, 'matcher'):
		merge_n_of_n.matcher = Matcher(spacy.nlp.vocab)
		merge_n_of_n.matcher.add("n-of-n", [[{"ENT_TYPE": "NP"}, {"LEMMA":"of"},{"ENT_TYPE": "NP"}], [{"ENT_TYPE": "NP"}, {"LEMMA":"of"},{"POS": "NOUN"}]], greedy ='LONGEST')
	with doc.retokenize() as retokenizer:
		for name, start, end in merge_n_of_n.matcher(doc):
			if end - start > 1: 
				try:
					i = doc[start].head.i
					attrs = {"pos": doc[i].pos, "tag": doc[i].tag, "dep": doc[i].dep, "lemma":doc[i].lemma, "ent_type": "NP"}
					retokenizer.merge(doc[start : end], attrs=attrs)
				except Exception as e:
					print ( "merge_n_of_n ex:", e , start, end)
	return doc

def merge_vp(doc):
	if not hasattr(merge_vp, 'matcher'):
		merge_vp.matcher = Matcher(spacy.nlp.vocab)
		merge_vp.matcher.add("vp", [[{"POS": {"IN":["AUX","PART"]}, "op": "*"}, {"POS":"VERB"},{"POS": "ADV", "op": "*"}]], greedy ='LONGEST')
	with doc.retokenize() as retokenizer:
		for name, start, end in merge_vp.matcher(doc):
			if end - start > 1: 
				try:
					i = doc[start].head.i
					attrs = {"pos": doc[i].pos, "tag": doc[i].tag, "dep": doc[i].dep, "lemma":doc[i].lemma, "ent_type": "VP"}
					retokenizer.merge(doc[start : end], attrs=attrs)
				except Exception as e:
					print ( "merge_vp ex:", e , start, end)
	return doc

def merge_pp(doc): 
	if not hasattr(merge_pp, 'matcher'):
		merge_pp.matcher = Matcher(spacy.nlp.vocab)
		merge_pp.matcher.add("pp", [[{"POS": {"IN":["ADP"]}, "op": "+"}, {"ENT_TYPE":"NP", "op": "+"}]], greedy ='LONGEST')
	with doc.retokenize() as retokenizer:
		for name, start, end in merge_pp.matcher(doc):
			if end - start > 1: 
				try:
					i = doc[start].head.i
					attrs = {"pos": doc[i].pos, "tag": doc[i].tag, "dep": doc[i].dep, "lemma":doc[i].lemma, "ent_type": "PP"}
					retokenizer.merge(doc[start : end], attrs=attrs)
				except Exception as e:
					print ( "merge_pp ex:", e , start, end)
	return doc

def skepp(doc, tag="_PP"): # added 2022.3.24,  | From the book, this is also difficult to .. 
	merge_pp(doc) # transform doc , finally to be called 
	return " ".join([tag if t.ent_type_ == 'PP' else t.text for t in doc])

def merge_clause(doc): # subtree of a verb is the clause , https://subscription.packtpub.com/book/data/9781838987312/2/ch02lvl1sec13/splitting-sentences-into-clauses
	with doc.retokenize() as retokenizer:
		for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
			try:
				children = list(v.subtree)
				start = children[0].i  	
				end = children[-1].i 
				attrs = {"pos": v.pos, "tag": v.tag, "dep": v.dep, "lemma":v.lemma, "ent_type": "S." + v.dep_ } # S.advcl ,  S.conj 
				retokenizer.merge(doc[start : end+1], attrs=attrs)
			except Exception as e:
				print ( "merge_clause ex:", e, v )
	return doc

def verbnet(doc):
	merge_np(doc)
	merge_vp(doc)
	for name, ibeg, iend in matcher(doc):
		arr = spacy.nlp.vocab[name].text.split(':') 
		i = ibeg + int(arr[-1]) 
		doc.user_data[f"verbnet-{i}"] = {"type":"verbnet", "start": ibeg, "end": iend, "lem":doc[i].lemma_,"chunk":arr[0].strip()}

simple_sent		= lambda doc: len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 
complex_sent	= lambda doc: len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) > 0
compound_sent	= lambda doc: len([t for t in doc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0  # S.conj 
pred_offset		= lambda doc:  (ar := [ t.i for t in doc if t.dep_ == "ROOT"], offset := ar[0] if len(ar) > 0 else 0,  offset/( len(doc) + 0.1) )[-1]

def stype(doc): 
	doc.user_data["stype"] = {"type": "simple_sent" if len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "complex_sent" }
	if len([t for t in doc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0  : # S.conj 
		doc.user_data["compound_sent"] = {"type": "compound_sent" }

skeleton = lambda doc:  " ".join([ t.ent_type_ if t.ent_type_ else t.text if t.is_punct or t.dep_ == 'ROOT' else t.pos_ for t in doc ])
def ske(doc): 
	merge_clause(doc)
	doc.user_data["ske"] = {"type":"ske","lem": ','.join([t.lemma_ for t in doc if t.dep_ == 'ROOT']),"chunk": skeleton(doc)}

def clause(doc):  # {'S.prep-0': {'type': 'S.prep', 'start': 0, 'end': 2, 'lem': 'consider', 'chunk': 'Considering the possibility'}, 'S.conj-9': {'type': 'S.conj', 'start': 9, 'end': 12, 'lem': 'be', 'chunk': 'she is ok .'}}
	for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
		children = list(v.subtree)
		start = children[0].i  	#end = children[-1].i 
		type = "S." + v.dep_   # S.advcl ,  S.conj 
		doc.user_data[f"{type}-{start}"] = {"type":type, "start": start, "end":children[-1].i + 1, "lem":v.lemma_,"chunk": " ".join([c.text for c in v.subtree])}

def attach(doc):
	verbnet(doc)
	stype(doc)
	clause(doc) 
	#ske(doc)

	# last to be called , added 2022.3.24,   in ES:  skenp:postag , to searh "_^ _IN _NP ," , in paper ratio
	merge_np(doc) 
	doc.user_data["skenp"] = {"type":"skenp", "snt": doc.text, "skenp": "_^ " + " ".join([ "_NP" if t.ent_type_ == 'NP' else f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]) + " _$"}

if __name__ == "__main__":  
	doc = spacy.nlp("Considering the possibility, it was ok, and she is ok.")
	clause(doc) 
	verbnet(doc)
	stype(doc)
	ske(doc)
	print (doc.user_data)

'''
	ssv = defaultdict(dict) 
	add_clause(101, doc, ssv)
	print (ssv)
	merge_np(doc)
	merge_clause(doc)
	print(doc[0].text)
	print ( skeleton(doc))

from collections import	defaultdict
def doc_to_verbnet(doc):
	merge_np(doc)
	merge_vp(doc)
	for name, ibeg, iend in matcher(doc):
		arr = spacy.nlp.vocab[name].text.split(':') 
		offset = int(arr[-1]) 
		yield (ibeg + offset, doc[ibeg+offset].lemma_, arr[0].strip() )

def submit_verbnet(sid, doc, ssv): 	#ssv = defaultdict(dict)
	for ibeg, lem, chunk in doc_to_verbnet(doc): 
		ssv[f"{sid}-verbnet-{ibeg}"].update ({"type":"verbnet","lem":lem,"chunk":chunk})

[['S.conj', 2423],
 ['S.relcl', 2058],
 ['S.advcl', 1982],
 ['S.ccomp', 1294],
 ['S.xcomp', 1196],
 ['S.acl', 1101],
 ['S.pcomp', 585],
 ['S.csubj', 66],
 ['S.dep', 38],
 ['S.acomp', 31],
 ['S.parataxis', 31],
 ['S.prep', 31],
 ['S.pobj', 27],
 ['S.amod', 19],
 ['S.nmod', 9],
 ['S.csubjpass', 7],
 ['S.dobj', 6],
 ['S.oprd', 5],
 ['S.attr', 4],
 ['S.nsubj', 4],
 ['S.nsubjpass', 3],
 ['S.appos', 1]]

	doc.user_data["snt"] = {'type':'snt', 'snt':doc.text, 	'pred_offset': pred_offset(doc), 
				'postag':'_^ ' + ' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]) + ' _$',
			   'tc': len(doc)} #'sid': rowid, 'src': rowid,
'''