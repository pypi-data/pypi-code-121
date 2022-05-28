# 2022.5.28

def topk_info(snts, docs,  topk, default_dims = {"internal_sim":0.2} ): 
	''' '''
	from dsk import score, pingyu
	from en.dims import docs_to_dims
	
	info = {}
	dims = docs_to_dims(snts[0:topk], docs[0:topk]) # only top [0:topk] snts are considered for scoring 
	for k,v in default_dims: 
		if not k in dims: 
			dims[k] = v # needed by formular 

	info.update(score.dims_score(dims))
	info['pingyu'] = pingyu.get_pingyu(dims)
	info['dims']   = dims  # new dsk format , /doc -> /info/dims 
	return info 

import difflib
trans_diff		= lambda src, trg:  [] if src == trg else [s for s in difflib.ndiff(src, trg) if not s.startswith('?')] #src:list, trg:list
trans_diff_merge= lambda src, trg:  [] if src == trg else [s.strip() for s in "^".join([s for s in difflib.ndiff(src, trg) if not s.startswith('?')]).replace("^+","|+").split("^") if not s.startswith("+") ]

def mkf_input(snts, docs, tokenizer, sntdic:dict={},diffmerge:bool=False): 
	''' '''
	srcs	= [ [t.text for t in doc] for doc in docs]
	tgts	= [ [t.text for t in doc] if ( snt not in sntdic or snt == sntdic.get(snt,snt) ) else [t.text for t in tokenizer(sntdic.get(snt,snt))] for snt, doc in zip(snts, docs)]
	input	= [ {"pid":0, "sid":i, "snt":snts[i], "tok": [t.text for t in doc],  
				"pos":[t.tag_ for t in doc], "dep": [t.dep_ for t in doc],"head":[t.head.i for t in doc],  
				"seg":[ ("NP", sp.start, sp.end) for sp in doc.noun_chunks] + [ (np.label_, np.start,np.end) for np in doc.ents] , 
				"gec": sntdic.get(snts[i],snts[i]), "diff": trans_diff_merge( srcs[i] , tgts[i]) if diffmerge else  trans_diff( srcs[i] , tgts[i] )	}
				for i, doc in enumerate(docs)]
	return input #mkfs	= requests.post(f"http://172.17.0.1:7095/parser", data={"q":json.dumps(input).encode("utf-8")}).json()