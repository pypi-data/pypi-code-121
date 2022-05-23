from enum import auto
from peewee import *
import sys
sys.path.insert(0, "TableCity")
from Connection_mysql_db.connection_mysql_db import *
from BaseModel import *


class Country(BaseClass):

    id = AutoField()
    country_name = CharField(50, null=False, unique=True)

    @staticmethod
    def countries_list():
        '''Print City table'''
        with db:
            order = Country.select()
            for row in order:
                print(row.id, row.country_name)
            
    def add_country(name: int):
        '''Add country'''
        with db:
            new_country = Country(country_name = name.lower().strip(),)
            new_country.save()
    
    class Meta():
        table_name = 'Countries'
        