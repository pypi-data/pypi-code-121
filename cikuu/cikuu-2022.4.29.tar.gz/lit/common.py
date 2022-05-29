# 2022.4.14
import streamlit as st
import time,redis, requests  

now	= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
r	= redis.Redis(host='172.17.0.1', port=6379, decode_responses=True) 
redis.r = r 