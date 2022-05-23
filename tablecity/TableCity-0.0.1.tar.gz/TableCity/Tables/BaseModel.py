from numpy import insert
from peewee import *
import sys
sys.path.insert(0, "TableCity")
from Connection_mysql_db.connection_mysql_db import *


class BaseClass(Model):
    
    class Meta():
        database = db
        primary_key = False
        