import os
from rr.my_sql import MySqlConnection
from api_utils.constants import General

db_user = os.environ.get('aws-user')
db_password = os.environ.get('aws-password')
host = os.environ.get('aws-host')

if not db_user:
    db_user = General.DEFAULT_USER

if not db_password:
    db_password = General.DEFAULT_PASSWORD

if not db_password:
    db_password = General.DEFAULT_HOST

conn = MySqlConnection(host=host, user=db_user, password=db_password, database=General.DATABASE)
