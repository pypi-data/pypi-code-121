import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))) # https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
sys.path.append(os.path.dirname(os.path.realpath(__file__+'/libs'))) # 为了不需要手动修改 mainWindow.py 中的相对路径的 import
sys.path.append(os.path.dirname(os.path.realpath(__file__+'/scripts')))