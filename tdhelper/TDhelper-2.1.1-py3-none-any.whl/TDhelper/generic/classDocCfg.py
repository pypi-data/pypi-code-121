import io
import os
import sys
import re
import json
def doc(source_str, key):
    result= ''
    isRead= False
    if source_str:
        source_str= io.StringIO(source_str)
        while True:
            m_str= source_str.readline()
            if not m_str:
                break
            m_str= m_str.strip()
            m_str= re.sub(u"\r|\n","",m_str,count=0,flags=0)
            if m_str.lower() == "["+key+"]":
                isRead= True
                m_str= ''
            elif m_str.lower() == "["+key+"end]":
                isRead= False
                break
            if isRead:
                result+=m_str
    if result:
        m_path= result.split('::')
        m_key= None
        if len(m_path)>1:
            m_key= m_path[0:len(m_path)-1]
            result= m_path[len(m_path)-1]
        if result.endswith('.json'):
            m_path= os.path.join(sys.path[0], result)
            m_path= m_path.replace("\\","/")
            with open(m_path,mode='r',encoding='utf-8') as f:
                result= f.read()
                if m_key:
                    result= json.loads(result)
                    for k in m_key:
                        if k in result:
                            result= result[k]
                    if isinstance(result, dict):
                        result= json.dumps(result)
                f.close()
    return result