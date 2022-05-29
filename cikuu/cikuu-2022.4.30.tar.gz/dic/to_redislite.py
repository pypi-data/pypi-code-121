# 2022.2.24 https://redislite.readthedocs.io/en/latest/topic/what_is_redislite.html
from redislite import Redis
r = Redis('./dic.redislite')

from word_idf import word_idf
r.zadd('word_idf', word_idf )

from word_awl import word_awl 
for w in word_awl : 
	r.sadd('word_awl', w)
	r.hset('word_level', w, 'awl') 

from word_gsl1 import word_gsl1 
for w in word_gsl1 : 
	r.sadd('word_gsl1', w)
	r.hset('word_level', w, 'gsl1') 

from word_gsl2 import word_gsl2 
for w in word_gsl2 : 
	r.sadd('word_gsl2', w)
	r.hset('word_level', w, 'gsl2') 

from ecdic import ecdic 
r.hmset('ecdic', ecdic)

from bnc_wordlist import bnc_wordlist 
r.zadd('bnc_wordlist', bnc_wordlist)

print ("finished")
