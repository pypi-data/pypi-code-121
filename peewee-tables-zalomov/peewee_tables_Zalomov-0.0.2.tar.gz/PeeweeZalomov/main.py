from peewee import *


def db_create(db_name: str, username: str, password: str, hostname: str):
    """Returns database if everything went good. Otherwise, returns None"""
    try:
        db = MySQLDatabase(db_name, user=username,
                           password=password, host=hostname)
        return db
    except Exception:
        return None


db = db_create(db_name=input("Enter database name: "), username=input("Enter username: "),
               password=input("Enter password: "), hostname=input("Enter hostname: "))
CatParts = {505: "Квартиры", 205: "Автомашины", 10: "Доски", 30: "Шкафы", 160: "Книги"}
CatPrice = {10: ["Стройматериалы", 105.00], 505: ["Недвижимость", 210.00], 205: ["Транспорт", 160.00],
            30: ["Мебель", 77.00], 45: ["Техника", 65.00]}


class BaseModel(Model):
    class Meta:
        database = db
        primary_key = False


class GoodDesc(BaseModel):
    Part_ID = IntegerField(unique=True)
    Part = CharField(max_length=20)
    Cat = IntegerField()

    @classmethod
    def good_desc_insert(cls, part: str, cat: int):
        """Insert new record in gooddesk table. Part_ID is counted automatically"""
        last_id = GoodDesc.select(fn.MAX(GoodDesc.Part_ID)).scalar()
        GoodDesc.insert(Part_ID=last_id + 1, Part=part, Cat=cat).execute()

    @classmethod
    def print_good_desc(cls):
        """Prints everything from gooddesc"""
        query = GoodDesc.select()
        print("Part_ID\tPart\tCat")
        for note in query:
            print(f"{note.Part_ID}\t{note.Part}\t{note.Cat}")

    @classmethod
    def print_by_cat(cls, cat: int):
        """Prints good category by its number."""
        print("Part_ID\tPart\tCat")
        query = GoodDesc.select().where(GoodDesc.Cat == cat)
        for note in query:
            print(f"{note.Part_ID}\t{note.Part}\t{note.Cat}")


class GoodPrice(BaseModel):
    Catnumb = IntegerField()
    Cat_name = CharField(max_length=30)
    Price = FloatField()

    @classmethod
    def up_price_by(cls, up_percent: int):
        GoodPrice.update({GoodPrice.Price: GoodPrice.Price+GoodPrice.Price*up_percent/100}).execute()

    @classmethod
    def print_good_price(cls):
        """Prints everything from goodprice"""
        query = GoodPrice.select()
        print("Catnumb\tCat_name\tPrice")
        for note in query:
            print(f"{note.Catnumb}\t{note.Cat_name}\t{note.Price}")

    @classmethod
    def good_price_insert(cls, catnumb: int, cat_name: str, price: float):
        """Insert one new record in goodprice table."""
        GoodPrice.insert(Catnumb=catnumb, Cat_name=cat_name, Price=price).execute()

    @classmethod
    def print_half_price(cls):
        """Prints category with price higher than max/2"""
        try:
            max_price = GoodPrice.select(fn.MAX(GoodPrice.Price)).scalar()
        except TypeError:
            print("It looks like there are no records in tables/Table don't exist!")
            return
        query = GoodPrice.select().where(GoodPrice.Price > round(max_price/2, 2))
        print("Catnumb\tCat_name\tPrice")
        for record in query:
            print(f"{record.Catnumb}\t{record.Cat_name}\t{record.Price}")


def table_create():
    """Creates tables"""
    db.create_tables([GoodDesc, GoodPrice])


def table_reset():
    """Resets tables"""
    db.drop_tables([GoodDesc, GoodPrice])
    db.create_tables([GoodDesc, GoodPrice])


table_create()


def disconnect():
    """Disconnect your database"""
    try:
        db.close()
    except Exception:
        pass

def data_print():
    """Prints connected gooddesc and goodprice tables"""
    query = GoodDesc.select(GoodDesc.Part_ID, GoodDesc.Part, GoodPrice.Cat_name,
                            GoodPrice.Price).join(GoodPrice, on=(GoodDesc.Cat == GoodPrice.Catnumb)).order_by(
        GoodDesc.Part_ID)
    print("Here is the joint of tables: ")
    print("Part_ID\tPart\tCat_name\tPrice")
    for goods in query:
        print(f"{goods.Part_ID}\t{goods.Part}\t{goods.goodprice.Cat_name}\t{goods.goodprice.Price}")


def table_fill():
    """Fills tables with pre-edited data. Resets all of your changes"""
    try:
        db.connect()
    except OperationalError:
        pass
    except ImproperlyConfigured:
        print("Something went wrong while connecting to database...")
        print("MySQL driver not installed!")
    try:
        db.drop_tables([GoodDesc, GoodPrice])  # Deleting duplicate info as Part_ID pole is unique
        db.create_tables([GoodDesc, GoodPrice])
    except ImproperlyConfigured:
        print("Something went wrong while connecting to database...")
        print("MySQL driver not installed!")
    else:
        print("Successfully connected to database!")
        counter = 1
        for key, att in CatParts.items():
            good_desc_table = GoodDesc(Part_ID=counter, Part=att, Cat=key)
            good_desc_table.save()
            counter += 1
        del counter
        for key, att in CatPrice.items():
            good_price_table = GoodPrice(Catnumb=key, Cat_name=att[0], Price=att[1])
            good_price_table.save()
        print("Successfully written info in tables!")
