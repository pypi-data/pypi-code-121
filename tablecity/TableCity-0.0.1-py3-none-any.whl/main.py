from peewee import *
import sys
sys.path.insert(0, "D:\Python\TableCity\TableCity")
from Connection_mysql_db.connection_mysql_db import *
from Tables import *


ConnectionMySql.connection_db('mydb', 'root', '12345678', 'localhost')

db.create_tables([City, Country, Density])

Country.add_country('Belarus')
Country.add_country('Poland')
Country.add_country('Ukrain')

City.add_city('Minsk', 1, 200000, 456.8)
City.add_city('Warsaw', 2, 2500000, 501.5)
City.add_city('Kiev', 3, 2350000, 486.1)

Density.add_density(1)
Density.add_density(2)
Density.add_density(3)


def db_to_print():
    with db:
        dict = (Country.select()
                .join(City, JOIN.LEFT_OUTER, on=(Country.id == City.country_id))
                .join(Density, JOIN.LEFT_OUTER, on=(City.id == Density.city_id))|
                Country.select()
                .join(City, JOIN.RIGHT_OUTER, on=(Country.id == City.country_id))
                .join(Density, JOIN.RIGHT_OUTER, on=(City.id == Density.city_id)))
        for item in dict.dicts().execute():
            print(item)
    

db_to_print()



    # def add_density_id(id: int):
    #     '''Add city id'''
    #     with db:
    #         new_id = Density(city_id = id,)
    #         new_id.save()