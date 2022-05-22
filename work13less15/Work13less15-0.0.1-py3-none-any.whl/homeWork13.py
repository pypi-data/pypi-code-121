from peewee import *

HW13 = MySQLDatabase('mydb',
    user='root',
    password='20021999',
    host='localhost'
    )
    

class Home(Model):
    Part_ID = FloatField()
    Part = CharField()
    Cat = FloatField()
    
    class Meta:
        database = HW13 
    
class Home_two(Model):
    CatNumb = FloatField()
    Cat_name = CharField()
    price = FloatField()  

    class Meta:
        database = HW13      
    
Home.create_table()
Home_two.create_table()

h1 = Home(Part_ID = 1, Part = 'Квартиры', Cat = 505)
h1.save()
h2 = Home(Part_ID = 2, Part = 'Автомашины', Cat = 205)
h2.save()
h3 = Home(Part_ID = 3, Part = 'Доски', Cat = 10)
h3.save()
h4 = Home(Part_ID = 4, Part = 'Шкафы', Cat = 30)
h4.save()
h5 = Home(Part_ID = 5, Part = 'Книги', Cat = 160)
h5.save()

h_t1 = Home_two(CatNumb = 10, Cat_name = 'Стройматериалы', price = 105.00)
h_t1.save()
h_t2 = Home_two(CatNumb = 505, Cat_name = 'Недвижимость', price = 210.00)
h_t2.save()
h_t3 = Home_two(CatNumb = 205, Cat_name = 'Транспорт', price = 160.00)
h_t3.save()
h_t4 = Home_two(CatNumb = 30, Cat_name = 'Мебель', price = 77.00)
h_t4.save()
h_t5 = Home_two(CatNumb = 45, Cat_name = 'Техника', price = 65.00)
h_t5.save()



for Home in Home.Cat().join(Home_two).where(Cat = Home_two.CatNumb):
    Home in Home.Cat().leftjoin(Home_two).where(Cat = Home_two.CatNumb)
    Home in Home.Cat().rightjoin(Home_two).where(Cat = Home_two.CatNumb)
    print(Home)    
            