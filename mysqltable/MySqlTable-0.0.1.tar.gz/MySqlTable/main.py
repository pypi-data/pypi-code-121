from peewee import *

try:
    database = MySQLDatabase("mydatabase",
    user="root",
    password="6113045Qwe",
    host="localhost",
)
except:
    print("Ошибка")

class List1(Model):
    Part = CharField()
    Cat = FloatField()

    class Meta:
        database = database
    
List1.create_table()
Line1 = List1(Part = "Квартиры", Cat = 505)
Line1.save()
Line2 = List1(Part = "Автомашины", Cat = 205)
Line2.save()
Line3 = List1(Part = "Доски", Cat = 10)
Line3.save()
Line4 = List1(Part = "Шкафы", Cat = 30)
Line4.save()
Line5 = List1(Part = "Книги", Cat = 160)
Line5.save()

class List2(Model):
    Catnumb = FloatField()
    Cat_Name = CharField()
    Price = FloatField()

    class Meta:
        database = database
List2.create_table()
Line1 = List2(Catnumb = 10,Cat_Name = "Стройматериалы", Price = 105.00)
Line1.save()
Line2 = List2(Catnumb = 505,Cat_Name = "Недвижимость", Price = 210.00)
Line2.save()
Line3 = List2(Catnumb = 205,Cat_Name = "Транспорт", Price = 160.00)
Line3.save()
Line4 = List2(Catnumb = 30,Cat_Name = "Мебель", Price = 77.00)
Line4.save()
Line5 = List2(Catnumb = 45,Cat_Name = "Техника", Price  = 65.00)
Line5.save()

query1 = List1.select(List1.Part)
print(List1.Part)

query2 = List1.select().where(List1.Part ** '%к%')
for List1 in query2:
    print(List1.Part)

query3 = List1.select().where(List1.Cat)
for List1 in query3:
    print(List1.Cat)