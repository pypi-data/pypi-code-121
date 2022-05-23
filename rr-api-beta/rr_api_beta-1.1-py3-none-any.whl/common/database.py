from peewee import *

from common.constants import General

user = 'root'
password = 'password'
db_name = General.DATABASE

conn = MySQLDatabase(
    db_name, user=user,
    password=password,
    host='localhost'
)
