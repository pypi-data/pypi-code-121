from peewee import *
import sys
sys.path.insert(0, "TableCity")
from Connection_mysql_db.connection_mysql_db import *
from BaseModel import *
from Country import *
from City import *


class Density(BaseClass):

    city_id = IntegerField(null=False, index=True)
    density_value = FloatField(null=False)
    
    @staticmethod
    def density_list():
        order = Density.select()
        for row in order:
            print(row.city_id, row.density_value)
            
    def add_density(id: int):
        value = City.select((City.area / City.civils)).where(City.id == id)
        new_value = Density(density_value = value, city_id = id,)
        new_value.save()

    class Meta():
        table_name = 'Densities'