# 2022.3.5
from app.dmdsk import *

def run(rid=2575450):
	
	st.title("eid-version")
	eidv = st.text_input("input a eidv", "152816246-2")
	ssi = eidv_term(eidv)
	st.write(ssi) 

if __name__ == '__main__': run()