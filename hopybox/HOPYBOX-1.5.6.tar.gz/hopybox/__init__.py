'''
            Copyright (c) 2022 HOStudio123(ChenJinlin) ,
                      All Rights Reserved.
'''
from platform import python_version
python_code = python_version().split('.')
if int(python_code[0]) < 3:
  print('Sorry, You python version is less than 3.8, and this program cannot be used.')
elif int(python_code[1]) < 8:
  print('Sorry, You python version is less than 3.8, and this procedure cannot be used.')
else:
  from .__main__ import *