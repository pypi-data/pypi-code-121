import re

name = 'nn'
package = f'dl2050{name}'
description = 'NN lib'
author = 'João Neto'
author_email = 'joao.filipe.neto@gmail.com'
keywords = ['Neural Networks']

def get_version_parts(ver):
      res = re.split(r'\.', ver, maxsplit=2)
      if len(res)<3: raise RuntimeError('Unable to parse version number')
      return res

def get_minor(ver):
      res = get_version_parts(ver)
      return res[2]

def get_camel(ver):
      res = get_version_parts(ver)
      return f'{res[0]}_{res[1]}_{res[2]}'

def save_version(ver):
      with open(f'./{package}/__version__.py', 'w') as f: f.write(f'version = "{ver}"')

def pump_version(ver):
      res = get_version_parts(ver)
      ver2 = f'{res[0]}.{res[1]}.{str(int(res[2])+1)}'
      save_version(ver2)
      return ver2