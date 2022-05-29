# 2022.4.7 snt-mkf 
import en,difflib,requests,sys,traceback,re
trans_diff		= lambda src, trg:  [] if src == trg else [s for s in difflib.ndiff(src, trg) if not s.startswith('?')] #src:list, trg:list
trans_diff_merge= lambda src, trg:  [] if src == trg else [s.strip() for s in "^".join([s for s in difflib.ndiff(src, trg) if not s.startswith('?')]).replace("^+","|+").split("^") if not s.startswith("+") ]
mkf_input		= lambda i, snt, gec, toklist, gec_toklist, doc, diffmerge,pid=0: 	{"pid":pid, "sid":i, "snt":snt, "tok": toklist,  #"offset":-1,"len":-1,"re_sntbr":0,  normally, offset =0
				"pos":[t.tag_ for t in doc], "dep": [t.dep_ for t in doc],"head":[t.head.i for t in doc],  #"tag":[t.tag_ for t in doc],
				"seg":[ ("NP", sp.start, sp.end) for sp in doc.noun_chunks] + [ (np.label_, np.start,np.end) for np in doc.ents] , 
				"gec": gec, "diff": trans_diff_merge( toklist , gec_toklist) if diffmerge else trans_diff( toklist , gec_toklist)	}

def mkf_inputs(valids, docs,  sntdic:dict={}, diffmerge:bool=False, getdoc=lambda snt: spacy.nlp(snt)):
	''' valids = snts, 2022.4.7  '''
	return [ mkf_input(i,valids[i],sntdic.get(valids[i],valids[i]), [t.text for t in doc], [t.text for t in (doc if valids[i] == sntdic.get(valids[i],valids[i]) else getdoc(sntdic.get(valids[i],valids[i]) )) ], doc, diffmerge )  for i, doc in enumerate(docs)]

def adjust_by_wordlist(snt, mkf):
	''' '''
	for k,v in mkf.get('feedback',{}).items(): 
		try:
			if 'ibeg_byte' in v: del v['ibeg_byte']
			if 'iend_byte' in v: del v['iend_byte']
			if 'word_list' in v:
				m = re.search(f"\\b{v['word_list']}\\b",snt) #offset = snt.find(v['word_list'])  
				if m is not None: 
					v['ibeg_byte'], v['iend_byte'] = m.span() # mark the first hitted  #v['ibeg_byte'] = offset  #v['iend_byte'] = offset + len(v['word_list'])
		except Exception as ex:
			print(">>adjust_by_wordlist Ex:", ex, "\t|", snt)
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)
			#redis.r.hset(f"debug:{id}", "ex:_adjust_by_wordlist", json.dumps([ str(ex), traceback.format_tb(exc_traceback_obj)]) )

def snt_mkf(snts, docs, sntdic:dict={}, ibeg_byte:bool=False, diffmerge:bool=False, batch:int=0, dskhost:str="172.17.0.1:7095") :  
	''' multiple process, ie: batch sent count in one shot=16,  added 2022.4.7 '''
	import grequests
	inputs = mkf_inputs(snts, docs, sntdic, diffmerge)

	if batch <= 0: # single process, tranditional way 
		mkfs	= requests.post(f"http://{dskhost}/parser", data={"q":json.dumps(inputs).encode("utf-8")}).json()
		if ibeg_byte: [adjust_by_wordlist(snt,mkf) for snt,mkf in zip(snts, mkfs)]
		return dict(zip(snts, mkfs))

	req_list = []
	offset = 0 
	while offset < len(inputs): 
		req_list.append( grequests.post(f"http://{dskhost}/parser", data={"q":json.dumps(inputs[offset:offset+batch]).encode("utf-8")}) )
		offset = offset + batch

	res_list = grequests.map(req_list)
	dic = {}
	for res in res_list: 	
		for ar in res.json(): #[{"feedback":{"_punct_space@w_punct.space_extra":{"cate":"w_punct.space_extra",
			snt = ar.get('meta',{}).get('snt','')
			if snt: 
				dic[snt] = ar 
				if ibeg_byte: adjust_by_wordlist(snt, ar)
	return dic 

def sntmkf(snt:str, gec:str, diffmerge:bool=False, dskhost:str="172.17.0.1:7095" ): 
	''' snt -> mkf, for debug only '''
	try:
		doc		= spacy.nlp(snt) 
		tdoc	= spacy.nlp(gec)
		input	= mkf_input( 0,snt,gec, [t.text for t in doc], [t.text for t in tdoc], doc, diffmerge ) 
		return requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts": [input]}).encode("utf-8")}).json()
	except Exception as ex:
		print(">>sntmkf Ex:", ex, "\t|", snt)

def sntsmkf(pairs:list =[["She has ready.","She is ready."], ["It are ok.","It is ok.", 1]], 
		dskhost:str="127.0.0.1:7095", asdsk:bool=False , diffmerge:bool=False, getdoc=lambda snt: spacy.nlp(snt)
		):
	''' snts -> mkfs,  if asdsk=True, return dsk , with info, kw, doc   '''
	try:
		snts	= [ pair[0] for pair in pairs ] 
		pids	= [ pair[2] if len(pair) >= 3 else 0 for pair in pairs ] 
		docs	= [ getdoc(snt) for snt in snts ] 
		sntdic  = { pair[0] : pair[1] for pair in pairs }  # 1. change to lighter nltk tokenizer 2. when snt=trans, keep unchanged toklist 
		input	= [ mkf_input(i,snts[i],sntdic[snts[i]], [t.text for t in doc], [t.text for t in (doc if snts[i] == sntdic[snts[i]] else getdoc(sntdic[snts[i]]) ) ], doc, diffmerge)  for i, doc in enumerate(docs)]
		mkfs	= requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json()
		return mkfs 
	except Exception as ex:
		print(">>gecv1_dsk Ex:", ex, "\t|", pairs)
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)
		return {"failed":str(ex)}

# moved to dsk.uvirun ,2022.4.7 
def snts_feedbacks(snts:list=["The quick fox jumped over the lazy dog.","Justice delayed is justice denied."],asdsk:bool=False, diffmerge:bool=False, dskhost:str="172.17.0.1:7095", getdoc=lambda snt: spacy.nlp(snt)):
		''' a simple wrapper of dsk-7095, for a quick feedback computing, 2022.4.6 '''
		try:
			docs	= [ getdoc(snt) for snt in snts ] 
			input	= [ mkf_input(i,snts[i],snts[i], [t.text for t in doc], [t.text for t in doc], doc, diffmerge)   for i, doc in enumerate(docs)]
			return requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json() if input else {}
		except Exception as ex:
			print(">>snts_feedbacks Ex:", ex, "\t|", snts)

def feedbacks(essay:str="The quick fox jumped over the lazy dog. Justice delayed is justice denied.",asdsk:bool=False, diffmerge:bool=False, dskhost:str="172.17.0.1:7095", getdoc=lambda snt: spacy.nlp(snt)):
		''' a simple wrapper of dsk-7095, for a quick feedback computing, 2022.4.6 '''
		try:
			sntpids = spacy.sntpid(essay)
			snts	= [ snt for snt,pid in sntpids ] 
			pids	= [ pid for snt,pid in sntpids ] 
			docs	= [ getdoc(snt) for snt in snts ] 
			input	= [ mkf_input(i,snts[i],snts[i], [t.text for t in doc], [t.text for t in doc], doc, diffmerge, pids[i] )   for i, doc in enumerate(docs)]
			return requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json() if input else {}
		except Exception as ex:
			print(">>gecv1_dsk Ex:", ex, "\t|", essay)

def uvirun(port): 
	''' python -m dsk.mkf uvirun 17095 '''
	import fastapi,uvicorn
	app		= fastapi.FastAPI()
	has_cl	= lambda d: any([t for t in d if t.dep_ in ('ccomp','xcomp','mark','csubj','relcl','pcomp')])
	cl_num	= lambda docs: len([d for d in docs if has_cl(d)])

	@app.get('/')
	def home():  return fastapi.responses.HTMLResponse(content=f"<h2>mkf wrapper </h2><a href='/docs'> docs </a> | <a href='/redoc'> redoc </a><br>last update: 2022.4.6")

	@app.post('/essay/todsk')
	def essay_to_dsk(sntdic:dict={"She has ready.":"She is ready.", "It are ok.":"It is ok."}, 
		essay:str="The quick fox jumped over the lazy dog. Justice delayed is justice denied.",
		asdsk:bool=True, diffmerge:bool=False, cl_ratio:bool=True, dskhost:str="dsk.jukuu.com"):  # 172.17.0.1:7095
		''' a simple wrapper of dsk-7095 , 2022.4.6 '''
		try:
			sntpids = spacy.sntpid(essay)
			snts	= [ snt for snt,pid in sntpids ] 
			pids	= [ pid for snt,pid in sntpids ] 
			docs	= [ spacy.nlp(snt) for snt in snts ] 
			input	= [ mkf_input(i,snts[i],sntdic.get(snts[i],snts[i]), [t.text for t in doc], [t.text for t in (doc if snts[i] == sntdic.get(snts[i],snts[i]) else spacy.nlp(sntdic.get(snts[i],snts[i])) )], doc, diffmerge, pids[i] )   for i, doc in enumerate(docs)]
			dsk		= requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json()
			if cl_ratio and isinstance(dsk, dict) and 'doc' in dsk: dsk['doc']['cl_ratio'] = cl_num(docs) / (len(snts) + 0.01)
			return dsk 
		except Exception as ex:
			print(">>gecv1_dsk Ex:", ex, "\t|", sntdic)
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)
			return str(ex)

	uvicorn.run(app, host='0.0.0.0', port=port)

def test():
	from dic import essay 
	snts	= spacy.snts(essay) 
	docs	= [spacy.nlp(snt) for snt in snts]
	#inputs	= mkf_inputs(snts, docs) 
	mkfs	= snt_mkf(snts, docs, ibeg_byte=True, dskhost='dsk.jukuu.com')
	print (len(mkfs), mkfs)

if __name__ == '__main__':
	import fire 
	fire.Fire({"test":test, "uvirun":uvirun, "hello": lambda: sntsmkf(asdsk=False, ), 'feedbacks': lambda: feedbacks()}) 