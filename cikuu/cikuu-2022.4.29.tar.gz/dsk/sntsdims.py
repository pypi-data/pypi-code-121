# 2022.4.11,  cp from en/dims.py,  coding=utf-8, 2022.1.11 uvicorn dims-fastapi:app --host 0.0.0.0 --port 7072 --reload
import collections,math, marisa_trie, re,itertools,logging,fire,base64
import numpy as np
import en
from dic.word_idf	import word_idf
from dic.word_awl	import word_awl
from dic.word_gsl1	import word_gsl1
from dic.mwe_pv		import mwe_pv
from dic.mwe_disconj import mwe_disconj

trie_mwe_pv			= marisa_trie.Trie(mwe_pv)
trie_mwe_disconj	= marisa_trie.Trie(mwe_disconj)
hit_mwe_pv			= lambda t: trie_mwe_pv.prefixes(t.doc[t.i:t.i+5].text) #['key1', 'key12']
hit_mwe_disconj		= lambda t: trie_mwe_disconj.prefixes(t.doc[t.i:t.i+5].text) #['key1', 'key12']
has_cl				= lambda d: any([t for t in d if t.dep_ in ('xcomp','ccomp','mark','csubj','relcl','pcomp')])
cl_num				= lambda ess: len([d for d in ess['docs'] if has_cl(d)])
is_simple_sent		= lambda d: len([t for t in d if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 #len([t for t in d if t.dep_ in ('ccomp','mark','csubj','relcl') or t.text in [','] ]) <= 0 
first_int			= lambda arr, default_v : arr[0] if len(arr) > 0 else default_v 
root_offset			= lambda d: first_int([t.i for t in d if t.dep_ == 'ROOT'], -1)
sort_value			= lambda arr: sorted(arr, key=lambda x:x[1], reverse=True) #d.items()

dim_func = { 
"word_gt7"			: lambda ess: len([t for d in ess['docs'] for t in d if len(t.text) >= 7]) / ess['tc'],
"b3"				: lambda ess: len([t for d in ess['docs'] for t in d if t.lemma_ in word_awl]) / ess['tc'],
"b3_b1"				: lambda ess: (len([t for d in ess['docs'] for t in d if t.lemma_ in word_awl]) + 0.1 ) / (len([t for d in ess['docs'] for t in d if t.lemma_ in word_gsl1]) + 0.1),
"ttr"				: lambda ess: 100 * ess['word_type'] / (ess['word_num'] + 0.01),
"ttr1"				: lambda ess: ess['word_type'] / math.sqrt( ess['word_num'] * 2.0),
"ttr2"				: lambda ess: ess['word_type'] * ess['word_type'] / ( ess['word_num'] + 0.01),
"doc_tc"			: lambda ess: len([t for d in ess['docs'] for t in d if t.tag_ not in {'_SP'}]),
"cl_sum"			: lambda ess: len([d for d in ess['docs'] if has_cl(d)]),
"cl_dens"			: lambda ess: cl_num(ess)/ ess['snt_num'],
"cl_ratio"			: lambda ess: cl_num(ess)/ ess['snt_num'],
"awl"				: lambda ess: np.mean([len(t.text) for d in ess['docs'] for t in d]),
"awl_sd"			: lambda ess: 0 if dim_func['awl'](ess) <= 1 else math.sqrt(sum([ math.pow(len(w.text) - dim_func['awl'](ess), 2) for d in ess['docs'] for w in d])/(ess['tc'])),
"ast"				: lambda ess: np.mean([len(d) for d in ess['docs']]),
"asl"				: lambda ess: np.mean([len(d.text) for d in ess['docs']]),
"ast_sd"			: lambda ess: 0 if ess['snt_num'] <= 1 else math.sqrt(sum([ math.pow(len(d) - 1 - dim_func['ast'](ess), 2) for d in ess['docs']]))/(ess['snt_num']-1),
"mwe_pv"			: lambda ess: len([t for d in ess['docs'] for t in d if len(hit_mwe_pv(t)) > 0 ])/ ess['snt_num'],
"mwe_disconj"		: lambda ess: len([t for d in ess['docs'] for t in d if len(hit_mwe_disconj(t)) > 0 ])/ ess['snt_num'],
"pv_dens"			: lambda ess: dim_func["mwe_pv"](ess),
"disconj_dens"		: lambda ess: dim_func["mwe_disconj"](ess),
"v_ratio"			: lambda ess: len([t for d in ess['docs'] for t in d if t.tag_.startswith("V")])/ ess['tc'],
"n_ratio"			: lambda ess: len([t for d in ess['docs'] for t in d if t.tag_.startswith("N")])/ ess['tc'],
"jj_ratio"			: lambda ess: len([t for d in ess['docs'] for t in d if t.tag_.startswith("JJ")])/ ess['tc'],
"rb_ratio"			: lambda ess: len([t for d in ess['docs'] for t in d if t.tag_.startswith("RB")])/ ess['tc'],
"cc_ratio"			: lambda ess: len([t for d in ess['docs'] for t in d if t.tag_.startswith("CC")])/ ess['tc'],
"comma_ratio"		: lambda ess: len([t for d in ess['docs'] for t in d if t.text in (',')])/ ess['tc'],
"art_ratio"			: lambda ess: len([t for d in ess['docs'] for t in d if t.text.lower() in ('a','an','the')])/ ess['tc'],
"simple_sent_ratio"	: lambda ess: len([sp for sp in ess['docs'] if is_simple_sent(sp)])/ess['snt_num'],
"simple_sent_ri"	: lambda ess: 1.0 / ( 1.0 + dim_func['simple_sent_ratio'](ess)),
"word_diff_avg"		: lambda ess: np.mean([6.607] + [word_idf[t.text.lower()] for d in ess['docs'] for t in d if t.text.lower() in word_idf and len(t.text) > 1]),  # avg(idf) = 6.607, to avoid empty list
"pred_diff_max3"	: lambda ess: 0 if len(ess['pred_verbs']) <= 0 else np.mean(sorted([word_idf.get(v, 6.607) for v in ess['pred_verbs']], reverse=True)[0:3]) ,
"prmods_tc"			: lambda ess: np.mean([3.0] + [root_offset(snt) for snt in ess['docs'] if root_offset(snt) > 0]) ,
"prmods_ratio"		: lambda ess: np.mean([0.15] + [root_offset(snt)/len(snt) for snt in ess['docs'] if root_offset(snt) > 0])  ,
}

def get_dims(ess): 
	'''  '''
	map = {}
	for name, f in dim_func.items(): 
		try:
			map[name]= f(ess)
		except Exception as ex:
			print("dim_func ex:", ex, "\t|", name) 
			map[name]= 0
	return map

def docs_to_dims(snts:list, docs:list):
	''' updated 2022.3.20 '''
	ess = {'snts': snts, 'docs': docs, 'tc': sum([len(d) for d in docs]), 'snt_num': len(docs), 
		'pred_verbs':{ t.lemma_ for d in docs for t in d if t.dep_ == 'ROOT' and t.tag_.startswith('V') and t.lemma_ in word_idf},
		'word_num': sum([len(d) for d in docs]), 
		'word_type': len({t.text.lower() for d in docs for t in d}) }

	dims = get_dims(ess)
	dims.update({"tc": ess['tc'], "snt_num": ess['snt_num'], "word_num": ess['word_num'], "word_type": ess['word_type']})
	return dims

def uvirun(port) : 
	''' python -m en.dims uvirun 8000 '''
	import uvicorn,fastapi
	app	= fastapi.FastAPI() 
	
	@app.get('/')
	def home(): return fastapi.responses.HTMLResponse(content=f"<h2>snts_dims</h2> <a href='/docs'> docs </a> | <a href='/redoc'> redoc </a> <br> last update: 2022-1-12 <hr>")

	@app.post('/dims/snts')
	def snts_to_dims(snts:list=["She has ready.","I believe I can do it."], use_cache:bool=True):
		''' updated 2022.3.20 '''
		docs = [spacy.getdoc(snt, use_cache) for snt in snts]
		return docs_to_dims(snts, docs) 

	@app.get('/dims/essay')
	def essay_to_dims(essay:str="She has ready. I believe I can do it."): 	
		''' updated 2022.3.20 '''
		return snts_to_dims( spacy.snts(essay) )

	uvicorn.run(app, host='0.0.0.0', port=port)

if __name__ == "__main__":  
	fire.Fire(uvirun)