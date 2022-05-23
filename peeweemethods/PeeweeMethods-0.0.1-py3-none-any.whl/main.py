from peewee import *

database = MySQLDatabase('hw13',
                         user='root',
                         password='12345678',
                         host='localhost',
                         )


class BaseModel(Model):
    class Meta:
        database = database


class Table1(BaseModel):
    Part_ID = IntegerField(primary_key=True)
    Part = CharField()
    Cat = IntegerField()


class Table2(BaseModel):
    Catnumb = IntegerField()
    Cat_name = CharField()
    Price = IntegerField()


with database:
    database.create_tables([Table1, Table2])

data_source1 = [
    {'Part_ID': 1, 'Part': 'Квартиры', 'Cat': 505},
    {'Part_ID': 2, 'Part': 'Автомашины', 'Cat': 205},
    {'Part_ID': 3, 'Part': 'Доски', 'Cat': 10},
    {'Part_ID': 4, 'Part': 'Шкафы', 'Cat': 30},
    {'Part_ID': 5, 'Part': 'Книги', 'Cat': 160}
]
data_source2 = [
    {'Catnumb': 10, 'Cat_name': 'Стройматериалы', 'Price': 105},
    {'Catnumb': 505, 'Cat_name': 'Недвижимость', 'Price': 210},
    {'Catnumb': 205, 'Cat_name': 'Транспорт', 'Price': 160},
    {'Catnumb': 30, 'Cat_name': 'Мебель', 'Price': 77},
    {'Catnumb': 45, 'Cat_name': 'Техника', 'Price': 65}
]


Table1.insert_many(data_source1).execute()
Table2.insert_many(data_source2).execute()


def inner_join():
    '''Объединение по критерию Cat и Catnumb задание 13.3.'''
    query = (Table1
             .select(Table1.Part_ID, Table1.Part, Table2.Cat_name, Table2.Price)
             .join(Table2, on=(Table1.Cat == Table2.Catnumb)))
    for value in query.order_by(Table1.Part_ID):
        print(value.Part_ID, value.Part, value.table2.Cat_name, value.table2.Price)


def last_three_line():
    '''Печать последних 3-х записей в таблице1.'''
    query = Table1.select().order_by(Table1.Part_ID.desc()).limit(3)
    for line in query:
        print(line.Part_ID, line.Part, line.Cat)


inner_join()
print()
last_three_line()
