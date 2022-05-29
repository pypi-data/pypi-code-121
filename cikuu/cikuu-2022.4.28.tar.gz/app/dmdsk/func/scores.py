# 2022.3.5
from app.dmdsk import *

def run(rid=2575450):
	
	st.title("rid-scores")
	res = {eidv:redis.dsk.hget(eidv,'score') for eidv in eidv_list(int(rid))}
	st.write(res) 

if __name__ == '__main__': run()