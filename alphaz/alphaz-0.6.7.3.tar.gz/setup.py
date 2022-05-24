import os, glob, re

from setuptools import setup, find_packages

version = "0.6.7.3"

excludes = ['.git','.vscode']

archives = glob.glob("dist/*")
for archive in archives:
  os.remove(archive)

def not_excluded(path, excludes = []):
  for exclude in excludes:
    if exclude in path:
      return False
  return True

def fast_scandir(dirname,excludes=[]):
  subfolders = [f.path for f in os.scandir(dirname) if f.is_dir() and not_excluded(f.path, excludes)]
  for dirname in list(subfolders):
      subfolders.extend(fast_scandir(dirname))
  return subfolders

def get_files(dirs):
  files = []
  for dir in dirs:
    files.extend([x for x in glob.glob(dir + os.sep + '*') if not '.py' in x])
  return files

subfolders = fast_scandir('alphaz',excludes)
subfolders.append("alphaz")

data = {x.replace(os.sep,'.').replace('alphaz.',''):['*'] for x in subfolders}

files = get_files(subfolders)

with open("MANIFEST.in","w") as f:
  f.write("\n".join(["include %s"%x for x in files]))

"""req_path = os.getcwd()+os.sep+'alphaz/requirements.txt'
print(f"Reading {req_path} ...")
with open(req_path, 'r') as f:
    required = [''.join([i for i in x.strip().replace("\ufeff","") if i.isalnum()]) for x in f.readlines()]
    try:
      """

required=['paramiko',
'typing-extensions',
'numpy',
'colorama',
'concurrent_log_handler',
'flask_sqlalchemy',
'fuzzywuzzy',
'flask_marshmallow',
'marshmallow_sqlalchemy',
'requests',
'lxml',
'flask_admin',
'xmltodict',
'dicttoxml',
'pyjwt',
'flask_mail',
'flask_statistics',
'flask_debugtoolbar',
'gevent',
'flask_monitoringdashboard',
'pysocks',
'pymysql',
'bcrypt',
'pandas',
'scp',
'gunicorn',
'celery',
'flower',
'zeep',
'pysftp',
'ldap3','cx_Oracle','pycryptodome','concurrent_log_handler',"flask_cors","pylint","bandit","black",
'unidecode']

setup(
  name = 'alphaz',
  packages = [x.replace(os.sep,'.') for x in subfolders],
  include_package_data=True,
  version = version,
  license='MIT',        
  description = 'A package full of very nice tools', 
  author = 'Aurèle',
  author_email="contact@aurele.eu",
  url="https://github.com/ZAurele/alphaz",
  download_url = 'https://github.com/ZAurele/alphaz/archive/refs/tags/%s.tar.gz'%version,
  keywords = ['Flask', 'Json'],
  install_requires=required,
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers', 
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3.10', 
    
  ],
)

