from __future__ import unicode_literals
import requests

try:
    unicode
except:
    unicode = str
    
session = requests.Session()
