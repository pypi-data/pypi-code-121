# 2022.3.5
from app.dmdsk import *

options = {
"平均词长":"awl",
"平均句长":"ast",
}

def run(rid=2575450):
	
	st.title("rid-dim-awl")
	dim = st.sidebar.selectbox('当前维度',[k for k,v in options.items()])
	data = {eidv: json.loads(redis.dsk.hgetall(eidv)['dsk'])['doc'][options[dim]] for eidv in eidv_list(int(rid))}
	
	st.sidebar.write(data) 
	st.line_chart({"data": [f for eidv,f in data.items()]})
	#st.dataframe(df.style.highlight_max(axis=0))

if __name__ == '__main__': run()