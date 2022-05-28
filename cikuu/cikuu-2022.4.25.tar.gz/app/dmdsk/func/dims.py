# 2022.3.5
from app.dmdsk import *

def run(rid=2575450):
	
	st.title("rid-dims")
	data = {eidv: json.loads(redis.dsk.hgetall(eidv)['dsk'])['doc'] for eidv in eidv_list(int(rid))}
	df = pd.DataFrame(data)
	df = df.stack().unstack(0)
	#st.write(df) 
	st.dataframe(df.style.highlight_max(axis=0))

if __name__ == '__main__': run()