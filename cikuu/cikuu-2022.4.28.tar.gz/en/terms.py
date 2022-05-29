# 2022.2.7, cp from dmssi.py , pure rule files 
import spacy , traceback, sys
from spacy.matcher import Matcher,DependencyMatcher
from collections import	Counter, defaultdict

if not hasattr(spacy,'nlp'): spacy.nlp	= spacy.load('en_core_web_sm') #if not 'nlp' in dir(): nlp	= spacy.load('en_core_web_sm')
vp_span = lambda doc,ibeg,iend: doc[ibeg].lemma_ + " " + doc[ibeg+1:iend].text.lower()

def new_matcher(patterns, name='pat'):
	matcher = Matcher(spacy.nlp.vocab)
	matcher.add(name, patterns, greedy ='LONGEST')
	return matcher
matchers = {
"vend":new_matcher([[{"POS": {"IN": ["AUX","VERB"]}},{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": {"IN": ["ADJ","VERB"]}, "OP": "*"},{"POS": {"IN": ["PART","ADP","TO"]}, "OP": "*"},{"POS": 'VERB'}]]), # could hardly wait to meet
"vp":  new_matcher([[{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ"]}, "OP": "*"},{"POS": 'NOUN'}, {"POS": {"IN": ["ADP","TO"]}, "OP": "*"}], #He paid a close attention to the book. |He looked up from the side. | make use of
                     [{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ","TO","PART"]}, "OP": "*"},{"POS": 'VERB'}]]), # wait to meet
"pp":  new_matcher([[{'POS': 'ADP'},{"POS": {"IN": ["DET","NUM","ADJ",'PUNCT','CONJ']}, "OP": "*"},{"POS": {"IN": ["NOUN","PART"]}, "OP": "+"}]]),    
"ap":  new_matcher([[{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": 'ADJ'}]]),  
"vprt": new_matcher([[{"POS": 'VERB'}, {"POS": {"IN": ["PREP", "ADP",'TO']}, "OP": "+"}]]),   # look up /look up from,  computed twice
"vtov":  new_matcher([[{"POS": 'VERB'}, {"TAG": 'TO'},{"TAG": 'VB'}]]),   # plan to go
"vvbg":  new_matcher([[{"POS": 'VERB'}, {"TAG": 'VBG'}]]),   # consider going
"vpg":  new_matcher([[{"POS": 'VERB'}, {"POS": {"IN": ["PREP", "ADP",'PART']}, "OP": "+"},{"TAG": 'VBG'}]]),   # insisted on going
"vAp":  new_matcher([[{'LEMMA': 'be'},{"TAG": {"IN": ["VBN"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}}]]),   # be based on   
"vap":  new_matcher([[{'LEMMA': 'be'},{"POS": {"IN": ["ADJ"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}}]]),   # be angry with
} #for name, ibeg,iend in matcher(doc) : print(spacy.nlp.vocab[name].text, doc[ibeg:iend].text)

def new_depmatcher(pattern, name='pat'):
	matcher = DependencyMatcher(spacy.nlp.vocab)
	matcher.add(name, [pattern])
	return matcher
depmatchers = {
"svo":new_depmatcher([ 
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  }
]), # [(4851363122962674176, [2, 0, 4])]
"sva":new_depmatcher([ 
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "acomp"}
  }
]), 
"svx":new_depmatcher([  # plan to go , enjoy swimming 
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "xcomp"}
  }
]), 
"svc":new_depmatcher([  # I think it is right.
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "ccomp"}
  }
]), 
"sattr":new_depmatcher([  #She is  a girl.
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"LEMMA": "be"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "attr"}
  }
]), 
"vpn":new_depmatcher([ # turn off the light
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "prt"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  }
]), 
"vap":new_depmatcher([ # be happy with
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "acomp",
    "RIGHT_ATTRS": {"DEP": "acomp"}
  },
  {
    "LEFT_ID": "acomp",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  }
]), 
"vdp":new_depmatcher([ # be based on
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"TAG": "VBN"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "be",
    "RIGHT_ATTRS": {"LEMMA": "be"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  }
]), 
"vppn":new_depmatcher([ # look up from phone
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prt",
    "RIGHT_ATTRS": {"DEP": "prt"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  }
]), 
"vpnpn":new_depmatcher([ # vary from A to B
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep1",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep1",
    "REL_OP": ">",
    "RIGHT_ID": "object1",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep2",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep2",
    "REL_OP": ">",
    "RIGHT_ID": "object2",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  }
]), 
"vnp":new_depmatcher([ # turn it down
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "prt"}
  }
]), 
"vnpn":new_depmatcher([  # make use of books, take sth into account
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  },
  {
    "LEFT_ID": "object",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep",
    "REL_OP": ">",
    "RIGHT_ID": "pobj",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  }  
]), 
} # for name, ar in depmatchers['svx'](doc) : print(doc[ar[1]], doc[ar[0]], doc[ar[2]])

def attach(doc):
	ssv = defaultdict(dict)
	try:
		[ ssv[f"tok-{t.i}"].update ({"type":"tok", "lex": t.text, "low":t.text.lower(), "lem": t.lemma_, 
			"pos":t.pos_, "tag":t.tag_, "dep":t.dep_ , "head":t.head.lemma_, "offset":round(t.i/len(doc),2)}) for t in doc]
		[ ssv[f"trp-{t.i}"].update ({"type":"trp", "gov": t.head.lemma_, "rel":f"{t.dep_}_{t.head.pos_}_{t.pos_}", "dep":t.lemma_, "govpos":t.head.pos_, "deppos":t.pos_}) for t in doc if t.dep_ not in ('punct') and t.pos_ not in ('PUNCT','SPACE')] #'ROOT',
		[ ssv[f"rootv-{t.i}"].update ({"type":"rootv", "lem": t.lemma_, "pos":t.pos_, "tag":t.tag_}) for t in doc if t.dep_ =='ROOT']
		[ ssv[f"vvbg-{t.i}"].update ({"type":"vvbg", "lem": t.head.lemma_, "chunk":f"{t.head.lemma_} {t.text.lower()}", "kp":f"{t.head.lemma_} DOING", "tail":t.lemma})
			 for t in doc if t.dep_ =='xcomp' and t.head.pos_ == 'VERB' and t.tag_ == 'VBG' and t.lemma_.isalpha() and t.head.lemma_.isalpha()]   #I enjoy smiling. 
		[ ssv[f"vtov-{t.i}"].update ({"type":"vtov", "lem": t.head.lemma_, "tail":t.text.lower(), "chunk":f"{t.head.lemma_} to {t.text.lower()}", "kp":f"{t.head.lemma_} to DO"}) # begin to DO:go 
			 for t in doc if t.dep_ =='xcomp' and t.head.pos_ == 'VERB' and t.tag_ == 'VB' and t.i > 1 and t.doc[t.i-1].tag_ == 'TO' and t.head.text.isalpha() and t.head.lemma_.isalpha()]   #I plan to go. 
		[ ssv[f"mdv-{t.i}"].update ({"type":"mdv","lem":t.head.lemma_, "chunk":f"{t.head.lemma_} {t.lemma_}"}) for t in doc  if t.tag_ == 'MD' and t.dep_ =='aux' and t.head.pos_ == 'VERB' and t.head.lemma_.isalpha()]
		[ ssv[f"np-{sp.start}"].update ({"type":"np","lem":sp.root.lemma_.lower(), "chunk":sp.text.lower()})
			 for sp in doc.noun_chunks if sp.end - sp.start > 1] # add  #book:np , f"#{sp.root.lemma_.lower()}:np" 
		[ ssv[f"npone-{sp.start}"].update ({"type":"np","lem":sp.root.lemma_.lower(),"chunk":sp.text.lower()}) for sp in doc.noun_chunks  if sp.end - sp.start <= 1]
		[ ssv[f"vp-{ibeg}"].update ({"type":"vp","lem":doc[ibeg].lemma_,"chunk":vp_span(doc,ibeg,iend), "tail":doc[iend-1].lemma_}) for name, ibeg,iend in matchers['vp'](doc)]
		[ ssv[f"vprt-{ibeg}"].update ({"type":"vprt","lem":doc[ibeg].lemma_,"chunk":vp_span(doc,ibeg,iend),})
			 for name, ibeg,iend in matchers['vprt'](doc)]
		[ ssv[f"pp-{ibeg}"].update ({"type":"pp","lem":doc[iend-1].lemma_.lower(), "chunk":doc[ibeg:iend].text.lower(),})
			 for name, ibeg,iend in matchers['pp'](doc)]
		[ ssv[f"ap-{ibeg}"].update ({"type":"ap","lem":doc[iend-1].lemma_.lower(),"chunk":doc[ibeg:iend].text.lower(), })
			for name, ibeg,iend in matchers['ap'](doc)]
		[ ssv[f"vend-{ibeg}"].update ({"type":"vend","lem":doc[iend-1].lemma_,"chunk":vp_span(doc,ibeg,iend), })
			for name, ibeg,iend in matchers['vend'](doc)]
		[ ssv[f"vpg-{ibeg}"].update ({"type":"vpg","lem":doc[ibeg+1].lemma_,"chunk":vp_span(doc,ibeg,iend)})
			for name, ibeg,iend in matchers['vpg'](doc)]
		[ ssv[f"svo-{doc[x[0]].i}"].update ({"type":"svo", "chunk":f"{doc[x[1]].lemma_} {doc[x[0]].lemma_} {doc[x[2]].lemma_}", "lem":doc[x[0]].lemma_, }) 
			for name, x in depmatchers['svo'](doc) ]
		[ ssv[f"sva-{doc[x[0]].i}"].update ({"type":"sva","lem":doc[x[0]].lemma_,"chunk":f"{doc[x[1]].lemma_} {doc[x[0]].lemma_} {doc[x[2]].lemma_}"})
			for name, x in depmatchers['sva'](doc) ]
		[ ssv[f"svx-{doc[x[0]].i}"].update ({"type":"svx","lem":doc[x[0]].lemma_,"chunk":doc[x[1]].lemma_+' '+doc[x[0]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['svx'](doc) ]
		[ ssv[f"sva-{doc[x[0]].i}"].update ({"type":"sva","lem":doc[x[0]].lemma_,"chunk":doc[x[1]].lemma_+' '+doc[x[0]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['svc'](doc) ]
		[ ssv[f"sattr-{doc[x[0]].i}"].update ({"type":"sattr","lem":doc[x[0]].lemma_,"chunk":doc[x[1]].lemma_+' '+doc[x[0]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['sattr'](doc) ]
		[ ssv[f"vpn-{doc[x[0]].i}"].update ({"type":"vpn","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['vpn'](doc) ]
		[ ssv[f"vap-{doc[x[0]].i}"].update ({"type":"vap","lem":doc[x[1]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['vap'](doc) ]
		[ ssv[f"vdp-{doc[x[0]].i}"].update ({"type":"vdp","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['vdp'](doc) ]
		[ ssv[f"vnp-{doc[x[0]].i}"].update ({"type":"vnp","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['vnp'](doc) ]
		[ ssv[f"vnpn-{doc[x[0]].i}"].update ({"type":"vnpn","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].text.lower()+' '+doc[x[2]].text.lower()+' '+doc[x[3]].text.lower(), })
			for name, x in depmatchers['vnpn'](doc) ]
		[ ssv[f"vppn-{doc[x[0]].i}"].update ({"type":"vppn","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].text.lower()+' '+doc[x[2]].text.lower()+' '+doc[x[3]].text.lower(), })
			for name, x in depmatchers['vppn'](doc) ]
		[ ssv[f"vpnpn-{doc[x[0]].i}"].update ({"type":"vpnpn","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].text.lower()+' '+doc[x[2]].text.lower()+' '+doc[x[3]].text.lower()+' '+doc[x[4]].lemma_, })
			for name, x in depmatchers['vpnpn'](doc) ]
	except Exception as e:
		print ( "ex:", e) 
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)

	for k,v in ssv.items():
		doc.user_data[k] = v 

hit = lambda ssi, *kvs: [ssi[kv[0]].update({kv[1]: 1}) for kv  in kvs ] 
def zset_ssi(doc, ssi):  # ssi = defaultdict(Counter)
	hit(ssi, ("SUM", "snt"))
	[ hit(ssi, ("SUM", "LEX"),("LEX", t.text.lower()), ("LEM",t.lemma_), (t.pos_, t.lemma_), (t.tag_, t.lemma_), ("SUM", t.pos_), ("SUM", t.tag_),("SUM", t.dep_)) for t in doc]
	[ hit(ssi, (f"{t.lemma_}/LEX", t.text.lower()) , (f"{t.lemma_}/POS", t.pos_), (f"{t.lemma_}/{t.pos_}", t.tag_),(f"*/{t.pos_}", t.tag_),) for t in doc if t.pos_ not in ("PROPN","PUNCT")]  
	[ hit(ssi, (f"{t.lemma_}/{t.pos_}", '#'), (f"*/{t.pos_}", '#') ) for t in doc if t.pos_ in ('VERB',"NOUN","ADJ","ADV")] #sum  
	[ hit(ssi,(f"{t.dep_}_{t.head.pos_}_{t.pos_}", f"{t.head.lemma_} {t.lemma_}"), # dobj_VERR_NOUN : open door
			  (f"~{t.dep_}_{t.head.pos_}_{t.pos_}", f"{t.lemma_} {t.head.lemma_}"), # ~dobj_VERR_NOUN : door open
			  (f"{t.head.lemma_}/{t.head.pos_}", f"{t.dep_}"),  # open/VERB  : dobj
			  (f"{t.lemma_}/{t.pos_}", f"~{t.dep_}"), # door/NOUN :  ~dobj
			  (f"*/{t.head.pos_}", f"{t.dep_}"),  # */VERB  : dobj
			  (f"*/{t.pos_}", f"~{t.dep_}"), # */NOUN :  ~dobj
			) for t in doc if t.dep_ not in ('punct') and t.pos_ not in ('PUNCT','SPACE',"PROPN","NUM") and t.text.isalpha()]  #'ROOT',
	[ hit(ssi,  (f"{t.lemma_}/VERB", "rootv"), (f"*/VERB", "rootv") )  for t in doc if t.dep_ =='ROOT' and t.pos_ == 'VERB']
	[ hit(ssi,  (f"vvbg", f"{t.head.lemma_} {t.text.lower()}"), 
				(f"{t.head.lemma_}/VERB", "vvbg"), 
				(f"{t.lemma_}/VERB", "~vvbg"), 
				(f"*/VERB", "vvbg"), (f"*/VERB", "~vvbg") 
		) for t in doc if t.dep_ =='xcomp' and t.head.pos_ == 'VERB' and t.tag_ == 'VBG' and t.lemma_.isalpha() and t.head.lemma_.isalpha()]   #I enjoy smiling. 
	[ hit(ssi, (f"vtov", f"{t.head.lemma_} to {t.text.lower()}"), 
				(f"{t.head.lemma_}/VERB", "vtov"), 	(f"{t.lemma_}/VERB", "~vtov"), 
				(f"*/VERB", "vtov"), (f"*/VERB", "~vtov") 
		) for t in doc if t.dep_ =='xcomp' and t.head.pos_ == 'VERB' and t.tag_ == 'VB' and t.i > 1 and t.doc[t.i-1].tag_ == 'TO' and t.head.text.isalpha() and t.head.lemma_.isalpha()]   #I plan to go. 
	[ hit(ssi, (f"mdv", f"{t.head.lemma_} {t.lemma_}"), 
				(f"{t.head.lemma_}/VERB", "mdv"), 
				(f"*/VERB", "mdv"), 
				) for t in doc  if t.tag_ == 'MD' and t.dep_ =='aux' and t.head.pos_ == 'VERB' and t.head.lemma_.isalpha()]

	[ ( n:=sp.root.lemma_.lower(), np:= sp.text.lower(), # book/np:a book
		hit(ssi, (f"{n}/np", np), (f"{n}/NOUN", "np"), (f"*/NOUN", "np"), ) ) for sp in doc.noun_chunks if sp.end - sp.start > 1] # add  #book:np , f"#{sp.root.lemma_.lower()}:np" 
	[ ( n:=sp.root.lemma_.lower(), np:= sp.text.lower(), 
		hit(ssi, (f"{n}/npone", np), (f"{n}/NOUN", "npone"), (f"*/NOUN", "npone"), )) for sp in doc.noun_chunks  if sp.end - sp.start <= 1]

	[ ( v:=doc[ibeg].lemma_, vp:= vp_span(doc,ibeg,iend), 
		hit(ssi, (f"{v}/vp", vp), (f"{v}/VERB", 'vp'), (f"*/VERB", "vp"),)) for name, ibeg,iend in matchers['vp'](doc)]
	[ ( v:=doc[ibeg].lemma_, vp:= vp_span(doc,ibeg,iend), 
		hit(ssi, (f"{v}/vprt",vp),(f"{v}/VERB", "vprt"), (f"*/VERB", "vprt"),) ) for name, ibeg,iend in matchers['vprt'](doc)]
	[ ( n:=doc[iend-1].lemma_.lower(), pp:= doc[ibeg:iend].text.lower(), 
		hit(ssi, (f"{n}/pp", pp), (f"{n}/NOUN", 'pp'), (f'*/NOUN', 'pp')) ) for name, ibeg,iend in matchers['pp'](doc)]
	[ ( a:=doc[iend-1].lemma_.lower(), ap:= doc[ibeg:iend].text.lower(), 
		hit(ssi, (f"{a}/ap", ap), (f"{a}/ADJ", 'ap'), ('*/ADJ','ap')) ) for name, ibeg,iend in matchers['ap'](doc)]
	[ ( v:=doc[iend-1].lemma_, vp:= vp_span(doc,ibeg,iend), 
		hit(ssi, (f"{v}/vend", vp), (f"{v}/VERB", 'vend'), (f"*/VERB","vend")) ) for name, ibeg,iend in matchers['vend'](doc)]
	[ ( v:=doc[ibeg+1].lemma_, vp:= vp_span(doc,ibeg,iend), 
		hit(ssi, (f"{v}/vpg",vp), (f"{v}/VERB", 'vpg'), (f'*/VERB','vpg')) ) for name, ibeg,iend in matchers['vpg'](doc)]

	[ ( s:=doc[x[1]].lemma_, v:=doc[x[0]].lemma_, o:=doc[x[2]].lemma_, 
	    hit(ssi, (f"{v}/svo", f"{s} {v} {o}"),  (f"{v}/VERB", "svo"), (f"{o}/NOUN", "~svo"), (f"*/VERB", "svo"), (f"*/NOUN", "~svo"), ) ) for name, x in depmatchers['svo'](doc) ]
	[ ( s:=doc[x[1]].lemma_, v:=doc[x[0]].lemma_, a:=doc[x[2]].lemma_, 
		hit(ssi, (f"{a}/sva",f"{s} {v} {a}"), (f"{v}/VERB", "sva"),  (f"{a}/ADJ", "~sva"), (f"*/VERB", "sva"),  (f"*/ADJ", "~sva"),  )) for name, x in depmatchers['sva'](doc) ]
	[ ( s:=doc[z[1]].lemma_, v:=doc[z[0]].lemma_, x:=doc[z[2]].lemma_, 
		hit(ssi, (f"{v}/svx", f"{s} {v} {x}"), (f"{v}/VERB","svx"), (f"*/VERB","svx"),)) for name, z in depmatchers['svx'](doc) ]
	[ ( s:=doc[x[1]].lemma_, v:=doc[x[0]].lemma_, c:=doc[x[2]].lemma_, 
		hit(ssi, (f"{v}/svc", f"{s} {v} {c}"), (f"{v}/VERB", "svc"), (f"*/VERB", "svc"))) for name, x in depmatchers['svc'](doc) ]
	[ ( s:=doc[x[1]].lemma_, v:=doc[x[0]].lemma_, c:=doc[x[2]].lemma_, 
		hit(ssi, (f"{v}/sattr", f"{s} {v} {c}"), (f"{v}/VERB","svattr"), (f"*/VERB","svattr"))) for name, x in depmatchers['sattr'](doc) ]
	[ ( v:=doc[x[0]].lemma_, p:=doc[x[1]].lemma_, n:=doc[x[2]].lemma_, 
		hit(ssi, (f"{v}/vpn", f"{v} {p} {n}"), (f"{v}/VERB","vpn"), (f"*/VERB","vpn"))) for name, x in depmatchers['vpn'](doc) ]
	[ ( v:=doc[x[0]].lemma_, a:=doc[x[1]].lemma_, p:=doc[x[2]].lemma_, 
		hit(ssi, (f"{v}/vap",f"{v} {a} {p}"), (f"{a}/ADJ","vap"), (f"*/ADJ","vap"))) for name, x in depmatchers['vap'](doc) ]
	[ ( v:=doc[x[0]].lemma_, d:=doc[x[1]].lemma_, p:=doc[x[2]].lemma_, 
		hit(ssi, (f"{v}/vdp",f"{v} {d} {p}"), (f"{v}/VERB","vdp"), (f"*/VERB","vdp"))) for name, x in depmatchers['vdp'](doc) ]
	[ ( v:=doc[x[0]].lemma_, n:=doc[x[1]].lemma_, p:=doc[x[2]].lemma_, 
		hit(ssi, (f"{v}/vnp",f"{v} {n} {p}"), (f"{v}/VERB","vnp"), (f"*/VERB","vnp"))) for name, x in depmatchers['vnp'](doc) ]
	[ ( v:=doc[x[0]].lemma_, n1:=doc[x[1]].text.lower(), p:=doc[x[2]].text.lower(), n2:=doc[x[3]].text.lower(), 
		hit(ssi, (f"{v}/vnpn",f"{v} {n1} {p} {n2}"), (f"{v}/VERB","vnpn"), (f"*/VERB","vnpn"))) for name, x in depmatchers['vnpn'](doc) ]
	[ ( v:=doc[x[0]].lemma_, p1:=doc[x[1]].text.lower(), p2:=doc[x[2]].text.lower(), n:=doc[x[3]].text.lower(), 
		hit(ssi, (f"{v}/vppn",f"{v} {p1} {p2} {n}"), (f"{v}/VERB","vppn"),(f"*/VERB","vppn"))) for name, x in depmatchers['vppn'](doc) ]
	[ ( v:=doc[x[0]].lemma_, p1:=doc[x[1]].text.lower(), n1:=doc[x[2]].text.lower(), p2:=doc[x[3]].text.lower(), n2:=doc[x[4]].lemma_, 
		hit(ssi, (f"{v}/vpnpn","{v} {p1} {n1} {p2} {n2}"), (f"{v}/VERB","vpnpn"), (f"*/VERB","vpnpn"))) for name, x in depmatchers['vpnpn'](doc) ]

def getssi(doc): # added 2022.2.27
	ssi = defaultdict(Counter)
	zset_ssi(doc, ssi)
	return ssi 

incr = lambda si, *names, delta = 1: [si.update({name: delta}) for name in names ] #si.incr("one", "two")
def es_terms(doc):  # added 2021.10.13
	si = Counter()
	[ incr(si, f"{t.pos_}:{t.lemma_}")  for t in doc]  
	[ incr(si, f"{t.dep_}_{t.head.pos_}_{t.pos_}:{t.head.lemma_} {t.lemma_}") for t in doc if t.dep_ not in ("ROOT","punct") and t.pos_ not in ("PUNCT","SPACE")] 
	[ incr(si,  f"rootv:{t.lemma_}")  for t in doc if t.dep_ =="ROOT" and t.pos_ == "VERB"]
	[ incr(si, f"vvbg:{t.head.lemma_} {t.text.lower()}") for t in doc if t.dep_ =="xcomp" and t.head.pos_ == "VERB" and t.tag_ == "VBG" and t.lemma_.isalpha() and t.head.lemma_.isalpha()]   #I enjoy smiling. 
	[ incr(si, f"vtov:{t.head.lemma_} {t.lemma_}") for t in doc if t.dep_ =="xcomp" and t.head.pos_ == "VERB" and t.tag_ == "VB" and t.i > 1 and t.doc[t.i-1].tag_ == "TO" and t.head.text.isalpha() and t.head.lemma_.isalpha()]   #I plan to go. 
	[ incr(si, f"mdv:{t.head.lemma_} {t.lemma_}") for t in doc  if t.tag_ == "MD" and t.dep_ =="aux" and t.head.pos_ == "VERB" and t.head.lemma_.isalpha()]

	[ ( n:=sp.root.lemma_.lower(), np:= sp.text.lower(), incr(si, f"{n}:np:{np}")) for sp in doc.noun_chunks if sp.end - sp.start > 1] 
	[ ( n:=sp.root.lemma_.lower(), np:= sp.text.lower(), incr(si, f"{n}:npone:{np}")) for sp in doc.noun_chunks  if sp.end - sp.start <= 1]
	[ ( v:=doc[ibeg].lemma_, vp:= vp_span(doc,ibeg,iend), incr(si, f"vp:{vp}")) for name, ibeg,iend in matchers["vp"](doc)]
	[ ( v:=doc[ibeg].lemma_, vp:= vp_span(doc,ibeg,iend), 	incr(si, f"vprt:{vp}")) for name, ibeg,iend in matchers["vprt"](doc)]
	[ ( n:=doc[iend-1].lemma_.lower(), pp:= doc[ibeg:iend].text.lower(), incr(si, f"{n}:pp:{pp}")) for name, ibeg,iend in matchers["pp"](doc)]
	[ ( a:=doc[iend-1].lemma_.lower(), ap:= doc[ibeg:iend].text.lower(), incr(si, f"{a}:ap:{ap}")) for name, ibeg,iend in matchers["ap"](doc)]
	[ ( v:=doc[iend-1].lemma_, vp:= vp_span(doc,ibeg,iend), incr(si, f"{v}:vend:{vp}")) for name, ibeg,iend in matchers["vend"](doc)]
	[ ( v:=doc[ibeg+1].lemma_, vp:= vp_span(doc,ibeg,iend), incr(si, f"{v}:vpg:{vp}")) for name, ibeg,iend in matchers["vpg"](doc)]

	[ ( s:=doc[x[1]].lemma_, v:=doc[x[0]].lemma_, o:=doc[x[2]].lemma_, 
	    incr(si, f"svo:{v}:{s} {o}")) for name, x in depmatchers["svo"](doc) ]
	[ ( s:=doc[x[1]].lemma_, v:=doc[x[0]].lemma_, a:=doc[x[2]].lemma_, incr(si, f"{a}:sva:{s} {v} {a}")) for name, x in depmatchers["sva"](doc) ]
	#[ ( s:=doc[x[1]].lemma_, a:=doc[x[2]].lemma_, incr(si, f"{a}:sbea:{s}")) for name, x in depmatchers["sbea"](doc) ] # the girl is happy
	[ ( s:=doc[z[1]].lemma_, v:=doc[z[0]].lemma_, x:=doc[z[2]].lemma_, 
		incr(si, f"svx:{v}:{s} {x}")) for name, z in depmatchers["svx"](doc) ]
	[ ( s:=doc[x[1]].lemma_, v:=doc[x[0]].lemma_, c:=doc[x[2]].lemma_, 
		incr(si, f"svc:{v}:{s} {c}")) for name, x in depmatchers["svc"](doc) ]
	#[ ( s:=doc[x[1]].lemma_, v:=doc[x[0]].lemma_, c:=doc[x[2]].lemma_, 	incr(si, f"sbea:{s} {c}")) for name, x in depmatchers["sbea"](doc) ]
	[ ( v:=doc[x[0]].lemma_, p:=doc[x[1]].lemma_, n:=doc[x[2]].lemma_, 
		incr(si, f"vpn:{v} {p} {n}")) for name, x in depmatchers["vpn"](doc) ]
	[ ( v:=doc[x[0]].lemma_, a:=doc[x[1]].lemma_, p:=doc[x[2]].lemma_, 
		incr(si, f"vap:{a}:{v} {p}")) for name, x in depmatchers["vap"](doc) ]  # vap:.* happy .* 
	[ ( v:=doc[x[0]].lemma_, d:=doc[x[1]].lemma_, p:=doc[x[2]].lemma_, 
		incr(si, f"{d}:vdp:{v} {d} {p}")) for name, x in depmatchers["vdp"](doc) ]
	[ ( v:=doc[x[0]].lemma_, n:=doc[x[1]].lemma_, p:=doc[x[2]].lemma_, 
		incr(si, f"vnp:{v} {n} {p}")) for name, x in depmatchers["vnp"](doc) ]
	[ ( v:=doc[x[0]].lemma_, n1:=doc[x[1]].text.lower(), p:=doc[x[2]].text.lower(), n2:=doc[x[3]].text.lower(), 
		incr(si, f"vnpn:{v} {n1} {p} {n2}")) for name, x in depmatchers["vnpn"](doc) ]
	[ ( v:=doc[x[0]].lemma_, p1:=doc[x[1]].text.lower(), p2:=doc[x[2]].text.lower(), n:=doc[x[3]].text.lower(), 
		incr(si, f"vppn:{v} {p1} {p2} {n}")) for name, x in depmatchers["vppn"](doc) ]
	[ ( v:=doc[x[0]].lemma_, p1:=doc[x[1]].text.lower(), n1:=doc[x[2]].text.lower(), p2:=doc[x[3]].text.lower(), n2:=doc[x[4]].lemma_, 
		incr(si, f"vpnpn:{v} {p1} {n1} {p2} {n2}")) for name, x in depmatchers["vpnpn"](doc) ]

	return dict(si) 

if __name__ == "__main__":  
	doc = spacy.nlp("I am happy with the box.")
	attach(doc)
	print (doc.user_data) 

'''
from nlp import terms 
terms.attach(doc) 

#from verbnet import submit_verbnet  # added 2022.2.11
def id_source(sid, doc):
	ssv = defaultdict(dict)
	es_source(sid, doc, ssv)
	submit_verbnet(sid, doc, ssv) # added 2022.2.11
	return ssv

#{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}

curl -H "Content-Type: application/json" -XPOST "localhost:9200/how2java/product/_bulk?refresh" --data-binary "@products.json"

{ "index" : { "_index" : "zhouls", "_type" : "user", "_id" : "6" } }
{ "name" : "mayun" , "age" : "51" }
{ "update" : { "_index" : "zhouls", "_type" : "user", "_id" : "6" } }
{ "doc" : { "age" : 52 }}

$ cat requests
{ "index" : { "_index" : "test", "_id" : "1" } }
{ "field1" : "value1" }
$ curl -s -H "Content-Type: application/x-ndjson" -XPOST localhost:9200/_bulk --data-binary "@requests"; echo
{"took":7, "errors": false, "items":[{"index":{"_index":"test","_id":"1","_version":1,"result":"created","forced_refresh":false}}]}
'''