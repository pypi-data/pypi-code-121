import os,sys
# Get project's home directory, 
BASEDIR=os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# All data directory
DATADIR=os.path.abspath(os.path.join(BASEDIR,'data'))
# Insert the BASEDIR to system path
sys.path.insert(0,BASEDIR)

