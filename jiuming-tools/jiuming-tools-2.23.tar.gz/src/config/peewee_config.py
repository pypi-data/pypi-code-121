from peewee import *

# 创建sqlite
from src.config.global_config import db_dir

db = SqliteDatabase(db_dir + '/tools.db')


# 定义peewee 元数据
class BaseModel(Model):
    class Meta:
        database = db


class MyTask(BaseModel):
    name = CharField()
    content = TextField()
    level = IntegerField()
    over = BooleanField()
    over_time = TimestampField()
    create_time = TimestampField()
    update_time = TimestampField()


db.connect()
db.create_tables([MyTask])
