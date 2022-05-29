# 2022.5.29   gears-cli run gears-xdsk.py --host 172.17.0.1   REQUIREMENTS requests | requests==2.22.0
import json,traceback, dsk 

def parse(x):
	try:
		xid		= x['id']
		hkey	= f"{x['key']}:{x['id']}" 
		res		= dsk.localgec_todsk( x['value'].get('essay_or_snts',''), device=int(x['value'].get('device', -1)), dskhost=x['value'].get('dskhost', 'gpu120.wrask.com:7095') )

		execute("LPUSH", f"{x['key']}:{xid}", json.dumps(res)) 
		execute("EXPIRE",f"{x['key']}:{xid}", int( x['value'].get('ttl',37200)) ) 
		execute("SETEX", f"dsk:{x['key']}:{xid}", 37200, json.dumps(res)) # as a backup
	except Exception as e:
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		log(f"xdsk failed {str(x)}, for {str(e)}\n" + traceback.format_exc())

gb = GearsBuilder('StreamReader')
gb.foreach(parse)
gb.register('xdsk:*')

# xadd xdsk:test * essay_or_snts "She has ready. It are ok."