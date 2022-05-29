#https://docs.streamlit.io/library/components/components-api

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(layout='wide')
st.sidebar.header("i+1 写作智慧课堂")
url = st.sidebar.text_input("input", "http://www.penly.cn:3000/public/dashboard/8e5329fc-6df2-4e5a-a827-79877da1ce73") 
st.sidebar.write(url) 

tid = st.sidebar.slider("tid", 1, 10, 1)
show = st.sidebar.checkbox('显示答案', True)

st.sidebar.markdown('''---''') 
genre = st.sidebar.radio('请选择',('打分', '划词', '润色'))

components.iframe(url,  height = 1200) #width=1500,