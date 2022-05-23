from peewee import *
import sys
sys.path.insert(0, "TableCity")
from Connection_mysql_db.connection_mysql_db import *
from BaseModel import *
from Country import *


class City(BaseClass):

    id = AutoField()
    city_name = CharField(50, null=False, unique=True)
    country_id = IntegerField(null=False)
    civils = IntegerField(null=False)
    area = FloatField()
    
    @staticmethod
    def cities_list():
        '''Print City table'''
        with db:
            order = City.select()
            for row in order:
                print(row.id, row.city_name, row.country_id, row.civils, row.area)
    
    def add_city(city_name: str, country_id: int, civils: int, area: float):
        '''Add other sities'''
        with db:
            data = [
                (city_name, country_id, civils, area)
            ]
            City.insert_many(data, fields=[City.city_name, City.civils, City.country_id, City.area]).execute()
    

    class Meta():
        table_name = 'Cities'