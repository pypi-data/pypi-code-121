import os
from dotenv import load_dotenv

#print('loading environment variables...')

load_dotenv()  # take environment variables from .env.

if not 'DATABASE_FOLDER' in os.environ:    
    os.environ['DATABASE_FOLDER'] = os.path.expanduser("~")+'\DB' 

if not 'S3_BUCKET' in os.environ:    
    os.environ['S3_BUCKET'] = 's3://deepportfolio'

if not 'LOG_STREAMNAME' in os.environ:    
    os.environ['LOG_STREAMNAME'] = 'deepportfolio-logs'
    
if not 'BASE_STREAM_NAME' in os.environ:    
    os.environ['BASE_STREAM_NAME'] = 'deepportfolio-real-time'    

if not 'AWS_PROFILENAME' in os.environ:
    os.environ['AWS_PROFILENAME'] = 'guest'

os.environ['USER_COMPUTER'] = os.environ['USERNAME']+'@'+os.environ['COMPUTERNAME']

loaded=True