# 2022.4.11

def rinit(host='127.0.0.1', port=6379, db=0):
	''' redis search init commands, 2022.4.11  '''
	import redis
	r		= redis.Redis(host=host, port=port, db=db, decode_responses=True) 
	r.execute_command("FT.CREATE ftsnt ON HASH PREFIX 1 snt: SCHEMA snt TEXT lems TAG trps TAG kps TAG cates TAG feedbacks TAG rid TAG uid TAG latest TAG tags TAG borntm NUMERIC SORTABLE")
	r.execute_command("FT.CREATE ftessay ON HASH PREFIX 1 essay: SCHEMA rid TAG uid TAG tags TAG latest TAG borntm NUMERIC SORTABLE") # essay:{xid}
	print (r.info())

if __name__ == '__main__': 
	import fire 
	fire.Fire()
