from peewee import *
from common.database import conn


class BaseModel(Model):
    class Meta:
        database = conn
