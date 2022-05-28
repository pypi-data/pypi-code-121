# client sample, 2022.2.4
import json, redis, requests, time

r	= redis.Redis(host="192.168.201.120", decode_responses=True)
arr	= {"key":f"1002-{time.time()}", "rid":"10","routing_key":"wps-dsk-to-blpop","essay":"English is a internationaly language which becomes importantly for modern world. \nIn China, English is took to be a foreigh language which many student choosed to learn. They begin to studying English at a early age. They use at least one hour to learn English knowledges a day. Even kids in kindergarten have begun learning simple words. That's a good phenomenan, for English is essential nowadays.\nIn addition to, some people think English is superior than Chinese. In me opinion, though English is for great significance, but English is after all a foreign language. it is hard for people to see eye to eye. English do help us read English original works, but Chinese helps us learn a true China. Only by characters Chinese literature can send off its brilliance. Learning a country's culture, especial its classic culture, the first thing is learn its language. Because of we are Chinese, why do we give up our mother tongue and learn our owne culture through a foreign language?"}
key = arr["key"] 
print ('key is:', key ,flush=True)

#r.lpush(f"gec-suc:hello","hello world")	
#print("test blpop:",  r.blpop([f"gec-suc:hello",f"gec-err:hello"], timeout=2), flush=True)

start = time.time() 
requests.post(f"http://root:jkpigai!@192.168.201.79:15672/api/exchanges/%2f/wps-essay/publish", json={"properties":{},"routing_key":'wps-essay-normal',"payload":json.dumps(arr),"payload_encoding":"string"}).text 
res	= r.blpop([f"gec-suc:{key}",f"gec-err:{key}"], timeout=6)	
print ("timing:", time.time() - start, res) 
