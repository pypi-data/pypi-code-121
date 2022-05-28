# 2022.3.2
import json,requests,fire,hashlib
from uvirun import * 
feedbacks = lambda dic :  [ v for k,v in dic['feedback'].items() ]

@app.get("/dsk/feedback")
def dsk_feedback(text:str="The quick fox jumped over the lazy dog. The justice delayed is justice denied."):
	''' '''
	dsk = requests.post(f"http://{fire.dskurl}/essay/gecdsk", json={"rid":"10", "key": hashlib.md5(text.encode("utf-8")).hexdigest(), "essay":text}).json()
	return  [ ( dic.get('meta',{}).get('snt',''), feedbacks(dic) ) for dic in dsk['snt']]

def run(port, dskurl, host='0.0.0.0'):
	''' '''
	print (port, dskurl, flush=True) 
	fire.dskurl = dskurl 
	uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":  
	fire.Fire(run)