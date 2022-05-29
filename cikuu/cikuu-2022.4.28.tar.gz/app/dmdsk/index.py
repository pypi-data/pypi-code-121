# 2022.2.3
import streamlit as st
import pandas as pd
import os
from func import * 

app_state = st.experimental_get_query_params()
if not isinstance(app_state, str): app_state = {k: v[0] if isinstance(v, list) else v for k, v in app_state.items()} 

st.sidebar.markdown("[home](/)", unsafe_allow_html=True)
rid = st.sidebar.text_input("作文号", "2575450")

if "f" in app_state: 
	f = app_state['f']
	x = __import__(f"func.{f}", fromlist=['run'])
	x.run(rid)
else: 
	st.title("Func list")
	for root, dirs, files in os.walk("func"):
		for file in files: 
			if file.endswith(".py") and not file.startswith("_") : #and not 'common' in file
				file = file.split(".")[0]
				st.write(f"[{file}](?f={file})")
