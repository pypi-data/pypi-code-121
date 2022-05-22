from  peewee import *
database = MySQLDatabase('mybd',
            user = 'root',
            password = 'ALMAZZ27ev',
            host = '127.0.0.1'
)
class razdel(Model):
    part_id = IntegerField()
    part = CharField()
    cat = IntegerField()

    class Meta:
        database = database

class catalog(Model):
    catnumb = IntegerField()
    cat_name = CharField()
    price = FloatField()

    class Meta:
        database = database
def inner_bd():

    in_bd = razdel.select(razdel.cat, razdel.part, catalog.cat_name, catalog.price).join(catalog, JOIN.INNER, on = (razdel.cat == catalog.catnumb)).dicts()
    for row in in_bd:
        print(row)
inner_bd() 

def left_bd():
    lf_bd = razdel.select(razdel.cat, razdel.part, catalog.cat_name, catalog.price).join(catalog, JOIN.LEFT_OUTER, on = (razdel.cat == catalog.catnumb)).dicts()
    for row in lf_bd:
        print(row)
left_bd()

def lim_bd():
    lm_bd = razdel.select(razdel.cat, razdel.part, catalog.cat_name, catalog.price).join(catalog, JOIN.INNER, on = (razdel.cat == catalog.catnumb)).limit(3).dicts()
    for row in lm_bd:
        print(row)
lim_bd()

    
    