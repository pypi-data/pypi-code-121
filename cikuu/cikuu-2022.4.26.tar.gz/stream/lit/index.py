# 2022.5.3 cp from index.py 
import streamlit as st
import os

app_state = st.experimental_get_query_params()
if not isinstance(app_state, str): app_state = {k: v[0] if isinstance(v, list) else v for k, v in app_state.items()} 
if "f" in app_state: 
	x = __import__(app_state['f'], fromlist=['run'])
	x.run()
else: 
	st.title("File list [ run() ]")
	for root, dirs, files in os.walk(".",topdown=False):
		for file in files: 
			if file.endswith(".py") and not file.startswith("_") and not 'common' in file  and not '/' in file: 
				file = file.split(".")[0]
				st.write(f"[{file}](?f={file})")
