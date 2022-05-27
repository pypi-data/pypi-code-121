import os   

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')
USER_DB = os.environ.get('USER_DB')
PASS_DB = os.environ.get('PASS_DB')
HOST = os.environ.get('HOST')
PORT = os.environ.get('PORT')
DB = os.environ.get('DB')

credentials = f'dev_s3:\n  key: {AWS_ACCESS_KEY_ID}\n  secret: {AWS_SECRET_ACCESS_KEY}\naws_postgres_dw:\n  con: postgresql://{USER_DB}:{PASS_DB}@{HOST}:{PORT}/{DB}\ngcp_postgres_dw:\n  con: postgresql://{USER_DB}:{PASS_DB}@{HOST}:{PORT}/{DB}'

with open('conf/local/credentials.yml', 'w') as credentials_writer:
    credentials_writer.write(credentials)
    
credentials_writer.close()




