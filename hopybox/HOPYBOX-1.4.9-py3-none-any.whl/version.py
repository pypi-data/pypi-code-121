import sys
from platform import system,python_version

version_number = 149
version_type = 'default'
# version_type = 'Beta'
gcc_version = sys.version.split(' ')[8].split(']')[0]

head_version = 'HOPYBOX 1.4.9 ({}, May 25 2022, 18:54:01)\n[Python {}] on {}\nType "help" , "copyright" , "version" or "license" for more information'.format(version_type,python_version(),system())

def system_version():
  print('\033[96mHOPYBOX:1.4.9\nPython:{}\nGCC:{}'.format(python_version(),gcc_version))