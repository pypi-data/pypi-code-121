import asyncio
import importlib

from tortoise import Model, fields, Tortoise
from jija.utils.collector import collect_subclasses
from aerich.ddl.postgres import PostgresDDL


class ModelUpdater:
    connection = None
    ddl = None

    def __init__(self, model):
        self.model = model

    async def update(self, existing_models):
        if self.model._meta.db_table in existing_models:
            await self.update_fields()
        else:
            print('jija')
            await self.create_model()

    async def update_fields(self):
        model_fields = self.model._meta.fields_map
        db_fields = await self.get_db_fields()

        new_fields = list(filter(lambda field_name: not db_fields.get(field_name), model_fields))
        old_fields = list(filter(lambda field_name: not model_fields.get(field_name), db_fields))
        same_fields = list(filter(lambda field_name: model_fields.get(field_name), db_fields))

        for key in same_fields:
            different = FieldGenerator.get_different(db_fields[key], model_fields[key])
            if different:
                print(key, different)

        for key in new_fields:
            await self.__create_field(model_fields[key])

        for key in old_fields:
            await self.__delete_field(db_fields[key])
        # print(create_fields)
        # for name in model_fields.values)
        # print(model_fields)
        # print(db_fields)

    async def __create_field(self, field):
        ddl = self.ddl.add_column(self.model, field)
        await self.connection.execute_query_dict(ddl)

    async def __delete_field(self, field):
        pass

    async def get_db_fields(self):
        raw_db_fields = await self.connection.execute_query_dict(f"""
            SELECT table_name, column_name, column_default, is_nullable, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' and table_name = '{self.model._meta.db_table}'
        """)

        db_fields = {}
        for field_data in raw_db_fields:
            db_fields[field_data['column_name']] = FieldGenerator.generate_field(field_data)
        return db_fields

    async def create_model(self):
        await self.connection.execute_query_dict(self.ddl.create_table(self.model))


class FieldGenerator:
    @classmethod
    def generate_field(cls, data):
        field_type = cls.__get_type(data['data_type'])
        kwargs = cls.__get_kwargs(data)

        return field_type(**kwargs)

    @classmethod
    def __get_type(cls, data_type):
        if data_type == 'integer':
            return fields.IntField
        elif data_type == 'character varying':
            return fields.TextField
        elif data_type == 'text':
            return fields.TextField
        elif data_type == 'double precision':
            return fields.FloatField
        elif data_type == 'timestamp with time zone':
            return fields.DatetimeField
        elif data_type == 'date':
            return fields.DateField
        else:
            raise ValueError('Unknown field type')

    @classmethod
    def __get_kwargs(cls, data):
        kwargs = {
            'null': data['is_nullable'] == 'YES',
        }

        try:
            default = data['column_default']
            if default != f"nextval('{data['table_name']}_id_seq'::regclass)":
                kwargs['default'] = default
        except ValueError:
            pass

        max_length = data.get('character_maximum_length')
        if max_length:
            kwargs['max_length'] = max_length

        return kwargs

    @classmethod
    def get_different(cls, old, new):
        different = []
        for item in ('default', 'null', 'max_length'):
            if hasattr(old, item):
                if str(getattr(old, item)) != str(getattr(new, item)):
                    different.append(item)

        return different

    @classmethod
    def field_to_dict(cls):
        list(diff(old_data_field, new_data_field))


class Jija(Model):
    a = fields.TextField()
    g = fields.IntField()


class Juja(Model):
    a = fields.CharField(max_length=334)
    b = fields.TextField()
    c = fields.IntField(default=5)
    d = fields.FloatField(null=True)
    e = fields.DatetimeField(unique=True)
    f = fields.DateField()

async def main():
    await initdb()
    await Migrator.run()


async def initdb():
    settings = {
        'connections': {
            'default': {
                'engine': 'tortoise.backends.asyncpg',
                'credentials': {
                    'port': '5432',
                    'user': 'postgres',
                    # 'database': 'tg_sniffer',
                    'database': 'test',
                    'host': 'localhost',
                    'password': '4296'
                }
            },
        },

        'apps': {
            'my_app': {
                'models': ['__main__'],
                'default_connection': 'default',
            }
        },

        'use_tz': False,
        'timezone': 'UTC'
    }

    await Tortoise.init(config=settings)

class FakeClient:
    class capabilities:
        inline_comment = None


class Migrator:
    @classmethod
    async def run(cls):
        ModelUpdater.connection = Tortoise.get_connection("default")
        ModelUpdater.ddl = PostgresDDL(FakeClient)

        models = cls.get_models()
        exist_models = await cls.get_existing_models()

        for model in models:
            await model.update(exist_models)
        #     if model._meta.db_table in exist_models:
        #         await cls.migrate_model(model)
        #     else:
        #         await cls.create_model(model)

    @classmethod
    def get_models(cls):
        mm = importlib.import_module('__main__')

        models = []
        for model in collect_subclasses(mm, Model):
            model = ModelUpdater(model)
            models.append(model)

        return models

    @classmethod
    async def get_existing_models(cls):
        conn = Tortoise.get_connection("default")
        res = list(map(
            lambda item: item['table_name'],
            await conn.execute_query_dict(
                "SELECT TABLE_NAME FROM information_schema.tables WHERE table_schema = 'public'")
        ))
        return res

import aerich

if __name__ == '__main__':
    # print(Juja._meta.fields_map)
    asyncio.get_event_loop().run_until_complete(main())
