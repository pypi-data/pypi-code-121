# 2022.3.9  
import json,requests,hashlib,os,redis,fire
from en import nlp , snts
from en.terms import *

os.gechost= os.getenv('gechost',"gec.jukuu.com") #http://gec.jukuu.com/gecv1/dsk?diffmerge=false&debug=false&dskhost=dsk.jukuu.com
os.dskhost= os.getenv('dskhost',"dsk.jukuu.com")
feedbacks = lambda dic :  [ v for k,v in dic['feedback'].items() ]

class util(object):
	def __init__(self, host='127.0.0.1', port=9221, db=0): 
		self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)

	def sntbr(self, did): 
		'''  did=101 '''
		docsnts = snts( self.r.hget(f"doc:{did}", "body") ) 	
		self.r.hset(f"doc:{did}","snts", json.dumps(docsnts))

	def dsk(self, did):
		''' did=102 '''
		essay = self.r.hget(f"doc:{did}", "body")
		dsk = requests.post(f"http://{os.gechost}/gecv1/dsk", params={"dskhost":os.dskhost}, json={"rid":"10", "key": hashlib.md5(essay.encode("utf-8")).hexdigest(), "essay":essay}).json()
		self.r.delete(f"feedback:{did}")
		for snt in dsk['snt']:
			for k,v in snt['feedback'].items(): 
				ibeg = v.get('ibeg', 0)
				iend = v.get('iend', 0) 
				cate = v.get('cate','')
				if cate.startswith("e_") or cate.startswith("w_"):
					self.r.hset(f"feedback:{did}", f"{ibeg},{iend},{cate}", v.get('kp',''))

	def errant(self, did):
		''' did=102 '''
		essay = self.r.hget(f"doc:{did}", "body")
		res = requests.post(f"http://{os.gechost}/gecv1/errant", json={"essay":essay}).json()
		self.r.delete(f"errant:{did}")
		offset = 0 
		for snt_edits in res:
			for edit in snt_edits['edits']: 
				ibeg = offset + edit.get('position', 0)
				iend = ibeg + len(edit.get('kp', ''))
				cate = edit.get('cate','')
				self.r.hset(f"errant:{did}", f"{ibeg},{iend},{cate}", edit.get('kp',''))
			snt = snt_edits['snt']
			offset = offset + len(snt) 

	def tag(self, did): 
		'''  did=102 '''
		doc = nlp(self.r.hget(f"doc:{did}", "body")) 
		[ self.r.hset(f"NP:{did}", f"{doc[np.start].idx},{doc[np.start].idx + len(np.text)},NP", np.text) for np in doc.noun_chunks if np.end - np.start > 1]
		for name, ibeg,iend in matchers['ap'](doc) :
			self.r.hset(f"AP:{did}",f"{doc[ibeg].idx},{doc[ibeg].idx + len(doc[ibeg:iend].text)},AP", doc[ibeg:iend].text)
		for name, ibeg,iend in matchers['vp'](doc) :
			self.r.hset(f"VP:{did}",f"{doc[ibeg].idx},{doc[ibeg].idx + len(doc[ibeg:iend].text)},VP", doc[ibeg:iend].text)

		# VERB: VBD/VBP/VBG
		[ self.r.hset(f"{t.pos_}:{did}",f"{t.idx},{t.idx + len(t.text)},{t.tag_}", t.text) for t in doc if t.pos_ in ["VERB","NOUN","ADJ","ADV"] ]

		# clause
		for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
			children = list(v.subtree)
			start = children[0].i  	#end = children[-1].i 
			cl = " ".join([c.text for c in v.subtree])
			self.r.hset(f"clause:{did}",f"{doc[start].idx},{doc[start].idx + len(cl)},{v.dep_}", cl)

		#non_pred_verb
		[ self.r.hset(f"non_pred_verb:{did}",f"{t.idx},{t.idx + len(t.text)},VBN", t.text) for t in doc if t.tag_ == 'VBN']
		for name, ibeg,iend in matchers['vtov'](doc) :
			self.r.hset(f"non_pred_verb:{did}",f"{doc[ibeg].idx},{doc[ibeg].idx + len(doc[ibeg:iend].text)},vtov", doc[ibeg:iend].text)
		for name, ibeg,iend in matchers['vvbg'](doc) :
			self.r.hset(f"non_pred_verb:{did}",f"{doc[ibeg].idx},{doc[ibeg].idx + len(doc[ibeg:iend].text)},vvbg", doc[ibeg:iend].text)

		# stype
		for sent in doc.sents:
			sdoc = sent.as_doc()
			if sdoc.text.strip() == '' : continue #added 2022.3.11
			stype = "simple" if len([t for t in sdoc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "complex" 
			self.r.hset(f"stype:{did}",f"{sent.start},{sent.end},{stype}", sent.text)
			self.r.sadd(f"snt:{sent.text}", stype) # added 2022.3.14
			if len([t for t in sdoc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0:
				self.r.hset(f"stype:{did}",f"{sent.start},{sent.end},compound", sent.text)
				self.r.sadd(f"snt:{sent.text}", "compound") # added 2022.3.14

	def start_www(self, wwwport): 
		''' uvicorn '''
		uvicorn.run(app, host='0.0.0.0', port=wwwport)

from uvirun import *
@app.get('/annotate/tagdoc')
def annotate(did:str="101", rhost:str='127.0.0.1', rport:int=9221, rdb=0):  
	'''  ''' 
	if not hasattr(annotate, 'inst'):
		annotate.inst = util(host=rhost, port=rport, db=rdb)
	annotate.inst.tag(did) 
	return did 
	
if __name__ == "__main__":  
	fire.Fire(util)