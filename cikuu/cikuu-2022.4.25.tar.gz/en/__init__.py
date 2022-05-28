# 2022.3.20, usage:  import en |  spacy.snts("hello") 
import json,spacy,os,builtins
from spacy.tokens import DocBin,Doc,Token
from spacy.tokenizer import Tokenizer
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex

def custom_tokenizer(nlp): #https://stackoverflow.com/questions/58105967/spacy-tokenization-of-hyphenated-words
	infixes = (
		LIST_ELLIPSES
		+ LIST_ICONS
		+ [
			r"(?<=[0-9])[+\-\*^](?=[0-9-])",
			r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
				al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
			),
			r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
			#r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
			r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
		]
	)
	infix_re = compile_infix_regex(infixes)
	return Tokenizer(nlp.vocab, prefix_search=nlp.tokenizer.prefix_search,
								suffix_search=nlp.tokenizer.suffix_search,
								infix_finditer=infix_re.finditer,
								token_match=nlp.tokenizer.token_match,
								rules=nlp.Defaults.tokenizer_exceptions)

def spacydoc(snt, use_cache=True): 
	''' added 2022.3.20 '''
	from en.spacybs import Spacybs
	if not use_cache: return spacy.nlp(snt)
	if not hasattr(spacydoc, 'db'): spacydoc.db = Spacybs("spacy311.sqlite")
	bs = spacydoc.db[snt]
	if bs is not None : return spacy.frombs(bs)
	doc = spacy.nlp(snt) 
	spacydoc.db[snt] = spacy.tobs(doc) 
	spacydoc.db.conn.commit()
	return doc 

def sqlitedoc(snt, table): 
	'''multiple tables supported,  added 2022.3.27 '''
	import sqlite3
	if not hasattr(sqlitedoc, 'conn'): 
		sqlitedoc.conn =	sqlite3.connect("spacy311.sntbs", check_same_thread=False) 
		sqlitedoc.conn.execute('PRAGMA synchronous=OFF')

	sqlitedoc.conn.execute(f'CREATE TABLE IF NOT EXISTS {table} (key varchar(512) PRIMARY KEY, value blob)')
	item = sqlitedoc.conn.execute(f'SELECT value FROM "{table}" WHERE key = ? limit 1', (key,)).fetchone()
	if item	is not None: return spacy.frombs(item[0]) 

	doc = spacy.nlp(snt) 
	sqlitedoc.conn.execute(f'REPLACE	INTO {table} (key,	value) VALUES (?,?)',	(snt, spacy.tobs(doc) ))
	sqlitedoc.conn.commit()
	return doc 

if not hasattr(spacy, 'nlp'):
	from spacy.lang import en
	spacy.sntbr		= (inst := en.English(), inst.add_pipe("sentencizer"))[0]
	spacy.snts		= lambda essay, trim=True: [ snt.text.strip() if trim else snt.text for snt in  spacy.sntbr(essay).sents]
	spacy.sntpid	= lambda essay: (pid:=0, [ ( pid := pid + 1 if "\n" in snt.text else pid,  (snt.text, pid))[-1] for snt in  spacy.sntbr(essay).sents] )[-1]
	spacy.sntpidoff	= lambda essay: (pid:=0, doc:=spacy.sntbr(essay), [ ( pid := pid + 1 if "\n" in snt.text else pid,  (snt.text, pid, doc[snt.start].idx))[-1] for snt in  doc.sents] )[-1]
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.tok		= lambda doc: ' '.join([t.text.strip() for t in doc])
	spacy.nps		= lambda doc : {f"{doc[np.end-1].lemma_}/np:{np.text.lower()}" for np in doc.noun_chunks} #book/np:a book
	spacy.trps		= lambda doc : {f"{t.dep_}_{t.head.pos_}_{t.pos_}:{t.head.lemma_} {t.lemma_}" for t in doc if t.pos_ not in ("PUNCT","PROPN","NUM","SPACE") and t.text.isalpha()} #'dobj_VERB_NOUN:open door';
	spacy.getdoc	= lambda snt, getf=lambda snt: None : ( res := getf(snt), res if res else spacy.nlp(snt))[1] 
	spacy.redisdoc	= lambda snt, r, prefix="": ( bs := r.get(prefix+snt), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), r.setnx(prefix+snt, spacy.tobs(doc)) if not bs else None )[1] # added 2022.3.29
	spacy.merge_nps	= spacy.nlp.create_pipe("merge_noun_chunks")
	spacy.nlp.tokenizer = custom_tokenizer(spacy.nlp)	#nlp.tokenizer.infix_finditer = infix_re.finditer
	#print([t.text for t in nlp("It's 1.50, up-scaled haven't")])
	# ['It', "'s", "'", '1.50', "'", ',', 'up-scaled', 'have', "n't"]

pred_offset		= lambda doc:  (ar := [ t.i for t in doc if t.dep_ == "ROOT"], offset := ar[0] if len(ar) > 0 else 0,  offset/( len(doc) + 0.1) )[-1]
postag			= lambda doc:  "_^ " + " ".join([ f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]) + " _$"
non_root_verbs	= lambda doc:  [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT'] 
simple_sent		= lambda doc:  len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 # else is complex sent 
compound_snt	= lambda doc:  len([t for t in doc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0
snt_source		= lambda sid, doc: {'type':'snt', 'src': sid, 'snt':doc.text, 'pred_offset': pred_offset(doc), 
				'postag':'_^ ' + ' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]) + ' _$',
			   'tc': len(doc)}

def parse(snt, merge_np= False):
	''' used in the notebook, for debug '''
	import pandas as pd
	doc = spacy.nlp(snt)
	if merge_np : spacy.merge_nps(doc)
	return pd.DataFrame({'word': [t.text for t in doc], 'tag': [t.tag_ for t in doc],'pos': [t.pos_ for t in doc],'head': [t.head.orth_ for t in doc],'dep': [t.dep_ for t in doc], 'lemma': [t.text.lower() if t.lemma_ == '-PRON-' else t.lemma_ for t in doc],
	'n_lefts': [ t.n_lefts for t in doc], 'left_edge': [ t.left_edge.text for t in doc], 
	'n_rights': [ t.n_rights for t in doc], 'right_edge': [ t.right_edge.text for t in doc],
	'subtree': str([ list(t.subtree) for t in doc]),'children': str([ list(t.children) for t in doc]),
	}) 

trp_rel		= lambda t:  f"{t.dep_}_{t.head.pos_}_{t.pos_}"  # dobj_VERB_NOUN
trp_reverse = set({"amod_NOUN_ADJ","nsubj_VERB_NOUN"})
trp_tok		= lambda doc, arr:  [ t for t in doc if [ t.dep_, t.head.pos_, t.pos_, t.head.lemma_, t.lemma_ ] == arr ] # arr is exactly 5 list 
gov_dep		= lambda rel, arr : (arr[0], arr[1]) if lemma_order.get(rel, True) else (arr[1], arr[0])  # open door
hit_trp		= lambda t, _rel, _gov_dep:   _rel == trp_rel(t) and _gov_dep == (t.head.lemma_, t.lemma_)
trp_high	= lambda doc, i, ihead :   "".join([ f"<b>{t.text_with_ws}</b>" if t.i in (i, ihead) else t.text_with_ws for t in doc ])
lem_high	= lambda doc, lem :   "".join([ f"<b>{t.text_with_ws}</b>" if t.lemma_ == lem else t.text_with_ws for t in doc ]) # highlight the first lemma 


def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

[ setattr(builtins, k, v) for k, v in globals().items() if not k.startswith("_") and not '.' in k and not hasattr(builtins,k) ]
#setattr(builtins, "spacy", spacy)
			
if __name__	== '__main__': 
	print(spacy.sntpidoff("   English   is a internationaly language which becomes importantly for modern world.  In China, English is took to be."))

#c:\users\zhang\appdata\local\programs\python\python38\lib\site-packages  
#/home/ubuntu/.local/lib/python3.8/site-packages/en
