from peewee import *


db = MySQLDatabase('mydb',
                    user = 'root',
                    password = '12345678',
                    host = 'localhost'
)


class BaseClass(Model):
    
    class Meta():
        database = db
        primary_key = False


class City(BaseClass):

    id = IntegerField(null=False, unique=True)
    city_name = CharField(50)
    civils = IntegerField(null=False)
    city_country_id = IntegerField(null=False)
    area = FloatField()

    class Meta():
        table_name = 'Cities'

class Country(BaseClass):

    country_name = CharField(50)
    country_id = IntegerField(null=False)

    class Meta():
        table_name = 'Countries'

class Density(BaseClass):

    city_id = IntegerField(null=False)
    density_value = FloatField()

    class Meta():
        table_name = 'Densities'
        
class Terretory(BaseClass):

    country_name = CharField(50)
    country_id = IntegerField(null=False)
    terretory_value = FloatField()

    class Meta():
        table_name = 'Terretory'
        
class VVP(BaseClass):

    country_name = CharField(50)
    country_id = IntegerField(null=False)
    vvp_value = FloatField()

    class Meta():
        table_name = 'VVP'
        
class HDI(BaseClass):

    country_name = CharField(50)
    country_id = IntegerField(null=False)
    ndi_value = FloatField()

    class Meta():
        table_name = 'HDI'

with db:

    db.create_tables([City, Country, Density,Terretory, VVP, HDI])

    data1 = [(1, 'Minsk', 2000000, 1, 348.8), (2, 'Kiev', 3000000, 2, 839.0)]
    data2 = [(1, 'Belarus'), (2, 'Ukraine')]
    data3 = [(1, City.select(City.civils/City.area).where(City.id == 1)), (2, City.select(City.civils/City.area).where(City.id == 2))]
    data4 = [(1, 'Berarus', 207600)]
    data5 = [(1, 'Berarus', 188954)]
    data6 = [(1, 'Berarus', 0.823)]
    
    City.insert_many(data1, fields=[City.id, City.city_name, City.city_country_id, City.area]).execute()
    Country.insert_many(data1, fields=[Country.country_id, Country.country_name]).execute()
    Density.insert_many(data1, fields=[Density.city_id, Density.density_value]).execute()
    Terretory.insert_many(data1, fields=[Terretory.country_id, Terretory.country_name, Terretory.terretory_value]).execute()
    VVP.insert_many(data1, fields=[VVP.country_id, VVP.country_name, VVP.vvp_value]).execute()
    HDI.insert_many(data1, fields=[HDI.country_id, HDI.country_name, HDI.ndi_value]).execute()