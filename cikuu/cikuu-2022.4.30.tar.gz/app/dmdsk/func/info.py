# 2022.3.5
from app.dmdsk import *
from collections import defaultdict, Counter

def run(rid=2575450):

	st.sidebar.markdown("[home](/)", unsafe_allow_html=True)
	
	st.title("rid info")
	rid = st.sidebar.text_input("作文号", "2578570") #2578570
	
	if st.sidebar.button("submit"):
		st.write(redis.dm.hgetall(f"rid:{rid}:snts"))

if __name__ == '__main__': run()