# import price_val_engine
from os.path import join, dirname

def get_version():
   try:
      with open(join(dirname(__file__), 'price_val_engine/VERSION'), 'rb') as f:
         version = f.read().decode('ascii').strip()
         return version
   except:
      pass