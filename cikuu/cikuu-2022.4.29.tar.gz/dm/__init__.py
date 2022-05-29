# https://github.com/yahoo/redislite

ifnone		= lambda v, default: v if v else default 
zset		= lambda key, topk = -1, asdic =False: r.zrevrange(key,0,topk,True) if not asdic else dict(r.zrevrange(key,0,topk,True))
zperc		= lambda key: util.L1_norm(r.zrevrange(key,0,-1,True)) # zsetperc("gzjc:lempos:book") #[('NOUN', 0.9894), ('VERB', 0.0106)]
zset_if		= lambda key, substr=':VB': [(k, score) for k, score in r.zrevrange(key,0,-1,True) if substr in k ] # lemtag
zdic		= lambda key,cutoff=0: { k:v for k,v in r.zrevrange(key,0,-1,True) if v > cutoff }

import math 
def likelihood(a,b,c,d, minus=None):  #from: http://ucrel.lancs.ac.uk/llwizard.html
	try:
		if a is None or a <= 0 : a = 0.000001
		if b is None or b <= 0 : b = 0.000001
		E1 = c * (a + b) / (c + d)
		E2 = d * (a + b) / (c + d)
		G2 = round(2 * ((a * math.log(a / E1)) + (b * math.log(b / E2))), 2)
		if minus or  (minus is None and a/c < b/d): G2 = 0 - G2
		return G2
	except Exception as e:
		print ("likelihood ex:",e, a,b,c,d)
		return 0
			
if __name__	== '__main__': 
	print (likelihood(1,2,3,4))