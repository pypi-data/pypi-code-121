import os 

def importnow(package : str):
    try:
        exec(f"import {package}")
    except:
        os.system(f"pip install {package}")