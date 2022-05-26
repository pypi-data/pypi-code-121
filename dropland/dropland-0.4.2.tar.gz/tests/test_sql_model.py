from datetime import datetime
from random import randint

import pytest
from sqlalchemy import Column, DateTime, Integer, String, func, text

from dropland.storages.redis import USE_REDIS
from dropland.storages.sql import USE_SQL

pytestmark = pytest.mark.skipif(not USE_SQL, reason='For Sql only')

if USE_REDIS:
    from dropland.data.model import CachedModel
    from .redis_models_data import redis_engine

if USE_SQL:
    from .sql_models_data import USE_GINO, USE_SQLA, \
        gino_mysql, gino_pg, sqla_mysql, sqla_pg, sqla_sqlite

    sqla_engines = (sqla_sqlite, sqla_pg, sqla_mysql)
    gino_engines = (gino_pg, gino_mysql)

    engines = sqla_engines if USE_SQLA else gino_engines
    models = [e.Model for e in engines]
    ids = ['SQLite', 'PostgreSQL', 'MySQL'] if USE_SQLA else ['PostgreSQL', 'MySQL']

    if USE_REDIS:
        models += [CachedModel('dropland', e.Model, redis_engine.Model) for e in engines]
        ids += [f'{i}+Redis' for i in ids]
else:
    models, ids = [], []


# noinspection PyPep8Naming
@pytest.mark.asyncio
@pytest.fixture(scope='module', params=models, ids=ids)
async def TestModel(request):
    Model = request.param
    engine = request.param.get_engine()
    table_name = f'testmodel_{ids[request.param_index].lower()}'

    class SomeModel(Model):
        __tablename__ = table_name

        id = Column(Integer, primary_key=True)
        data = Column(String(128))
        create_date = Column(DateTime, server_default=func.now())

        # required in order to access columns with server defaults
        # or SQL expression defaults, subsequent to a flush, without
        # triggering an expired load
        __mapper_args__ = {'eager_defaults': True}

    assert SomeModel.get_engine() is engine
    ti = SomeModel.get_table_info()
    assert ti.backend == engine.backend.name
    assert ti.db_type == engine.db_type
    assert ti.is_async == engine.is_async

    if USE_SQLA:
        async with engine.raw_engine.begin() as conn:
            await conn.run_sync(engine.metadata.drop_all, tables=[SomeModel.__table__])
            await conn.run_sync(engine.metadata.create_all, tables=[SomeModel.__table__])
            await conn.commit()

        yield SomeModel

        async with engine.raw_engine.begin() as conn:
            await conn.run_sync(engine.metadata.drop_all, tables=[SomeModel.__table__])
            await conn.commit()

    elif USE_GINO:
        from dropland.storages.sql import default_storage
        from gino.schema import GinoSchemaVisitor

        async with default_storage.manager().with_async_engines(['gino']):
            bind = engine.raw_engine.bind
            await GinoSchemaVisitor(engine.metadata).drop_all(bind, tables=[SomeModel.__table__])
            await GinoSchemaVisitor(engine.metadata).create_all(bind, tables=[SomeModel.__table__])

        yield SomeModel

        async with default_storage.manager().with_async_engines(['gino']):
            bind = engine.raw_engine.bind
            await GinoSchemaVisitor(engine.metadata).drop_all(bind, tables=[SomeModel.__table__])


_construct_counter = 0
_construct_rela_counter = 0
_construct_list_counter = 0
_construct_rela_list_counter = 0
_reload_rela_counter = 0


@pytest.fixture(scope='function')
def build_calls_counter(TestModel, monkeypatch):
    global _construct_counter, _construct_list_counter, \
        _construct_rela_counter, _construct_rela_list_counter, _reload_rela_counter
    _construct_counter = 0
    _construct_list_counter = 0
    _construct_rela_counter = 0
    _construct_rela_list_counter = 0
    _reload_rela_counter = 0

    old_construct = TestModel.construct
    old_construct_rela = TestModel.construct_rela
    old_construct_list = TestModel.construct_list
    old_construct_rela_list = TestModel.construct_rela_list
    old_reload_rela = TestModel.reload_rela

    async def construct(context, data, **kwargs):
        global _construct_counter
        _construct_counter += 1
        return await old_construct(context, data, **kwargs)

    async def construct_rela(context, instance, **kwargs):
        global _construct_rela_counter
        _construct_rela_counter += 1
        return await old_construct_rela(context, instance, **kwargs)

    async def construct_list(context, objects, **kwargs):
        global _construct_list_counter
        _construct_list_counter += 1
        return await old_construct_list(context, objects, **kwargs)

    async def construct_rela_list(context, objects, **kwargs):
        global _construct_rela_list_counter
        _construct_rela_list_counter += 1
        return await old_construct_rela_list(context, objects, **kwargs)

    async def reload_rela(self, context, load_fields, **kwargs):
        global _reload_rela_counter
        _reload_rela_counter += 1
        return await old_reload_rela(self, context, load_fields, **kwargs)

    monkeypatch.setattr(TestModel, 'construct', construct)
    monkeypatch.setattr(TestModel, 'construct_rela', construct_rela)
    monkeypatch.setattr(TestModel, 'construct_list', construct_list)
    monkeypatch.setattr(TestModel, 'construct_rela_list', construct_rela_list)
    monkeypatch.setattr(TestModel, 'reload_rela', reload_rela)


@pytest.mark.asyncio
async def test_model_fields(data_ctx, TestModel):
    m = TestModel()
    assert TestModel.get_fields() == {'id', 'create_date', 'data'}
    assert m.get_values() == {'id': None, 'create_date': None, 'data': None}

    m.id = 123
    m.data = 'qwer'
    assert m.get_values() == {'id': 123, 'create_date': None, 'data': 'qwer'}


@pytest.mark.asyncio
async def test_create(data_ctx, TestModel, build_calls_counter):
    obj = await TestModel.create(dict(data='123'))
    assert obj.id > 0
    assert obj.data == '123'

    assert _construct_counter == 1
    assert _construct_rela_counter == _construct_counter
    assert _construct_list_counter == 0
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_counter


@pytest.mark.asyncio
async def test_update(data_ctx, TestModel, build_calls_counter):
    obj = await TestModel.create(dict(data='123'))
    assert await obj.update(dict(data='456'))
    assert obj.id > 0
    assert obj.data == '456'

    assert _construct_counter == 1
    assert _construct_rela_counter == _construct_counter
    assert _construct_list_counter == 0
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_counter + 1


@pytest.mark.asyncio
async def test_update_by_id(data_ctx, TestModel, build_calls_counter):
    obj1 = await TestModel.create(dict(data='123'))

    obj2 = await TestModel.update_by_id(obj1.id, dict(data='234'))
    assert obj2.id > 0
    assert obj2.data == '234'

    obj3 = await TestModel.update_by_id(-1, dict(data='234'))
    assert obj3 is None

    assert _construct_counter == 2
    assert _construct_rela_counter == _construct_counter
    assert _construct_list_counter == 0
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_counter


@pytest.mark.asyncio
async def test_get(data_ctx, TestModel, build_calls_counter):
    obj1 = await TestModel.create(dict(data='123'))

    obj2 = await TestModel.get(obj1.id)
    assert obj1.id == obj2.id
    assert obj1.data == obj2.data
    assert obj1 == obj2

    obj3 = await TestModel.get(-1)
    assert obj3 is None

    assert _construct_counter == (1 if TestModel.has_cache() else 2)
    assert _construct_rela_counter == 2
    assert _construct_list_counter == 0
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_rela_counter


@pytest.mark.asyncio
async def test_list(data_ctx, TestModel, build_calls_counter):
    obj1 = await TestModel.create(dict(data='1'))
    obj2 = await TestModel.create(dict(data='2'))
    obj3 = await TestModel.create(dict(data='3'))

    objects = await TestModel.list()
    assert len(objects) == 3
    assert objects[0] == obj1
    assert objects[1] == obj2
    assert objects[2] == obj3

    objects = await TestModel.list(skip=1)
    assert len(objects) == 2
    assert objects[0] == obj2
    assert objects[1] == obj3

    objects = await TestModel.list(skip=2)
    assert len(objects) == 1
    assert objects[0] == obj3

    objects = await TestModel.list(skip=3)
    assert len(objects) == 0

    objects = await TestModel.list(limit=1)
    assert len(objects) == 1
    assert objects[0] == obj1

    objects = await TestModel.list(limit=2)
    assert len(objects) == 2
    assert objects[0] == obj1
    assert objects[1] == obj2

    objects = await TestModel.list(limit=3)
    assert len(objects) == 3
    assert objects[0] == obj1
    assert objects[1] == obj2
    assert objects[2] == obj3

    objects = await TestModel.list(skip=1, limit=3)
    assert len(objects) == 2
    assert objects[0] == obj2
    assert objects[1] == obj3

    objects = await TestModel.list(skip=2, limit=1)
    assert len(objects) == 1
    assert objects[0] == obj3

    objects = await TestModel.list(skip=3, limit=3)
    assert len(objects) == 0

    objects = await TestModel.list(skip=2, limit=0)
    assert len(objects) == 1
    assert objects[0] == obj3

    assert _construct_counter == 19
    assert _construct_rela_counter == _construct_counter
    assert _construct_list_counter == 11
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_counter


@pytest.mark.asyncio
async def test_filter(data_ctx, TestModel, build_calls_counter):
    obj1 = await TestModel.create(dict(data='1'))
    obj2 = await TestModel.create(dict(data='2'))
    obj3 = await TestModel.create(dict(data='3'))

    objects = await TestModel.list()
    assert len(objects) == 3
    assert objects[0] == obj1
    assert objects[1] == obj2
    assert objects[2] == obj3

    objects = await TestModel.list([])
    assert len(objects) == 3
    assert objects[0] == obj1
    assert objects[1] == obj2
    assert objects[2] == obj3

    objects = await TestModel.list([TestModel.data == '-1'])
    assert len(objects) == 0

    objects = await TestModel.list([TestModel.data == '1'])
    assert len(objects) == 1
    assert objects[0] == obj1

    objects = await TestModel.list([TestModel.data == '1', TestModel.data == '2'])
    assert len(objects) == 0

    objects = await TestModel.list([(TestModel.data == '1') | (TestModel.data == '2')])
    assert len(objects) == 2
    assert objects[0] == obj1
    assert objects[1] == obj2

    objects = await TestModel.list([(TestModel.data == '1') & (TestModel.id == obj1.id)])
    assert len(objects) == 1
    assert objects[0] == obj1

    objects = await TestModel.list([text('data > :data')], params=dict(data='1'))
    assert len(objects) == 2
    assert objects[0] == obj2
    assert objects[1] == obj3

    assert _construct_counter == 15
    assert _construct_rela_counter == _construct_counter
    assert _construct_list_counter == 8
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_counter


@pytest.mark.asyncio
async def test_any(data_ctx, TestModel, build_calls_counter):
    obj1 = await TestModel.create(dict(data='1'))
    obj2 = await TestModel.create(dict(data='2'))
    obj3 = await TestModel.create(dict(data='3'))

    objects = await TestModel.get_any([])
    assert len(objects) == 0

    objects = await TestModel.get_any([obj1.id, obj2.id, obj3.id])
    assert len(objects) == 3
    assert objects[0] == obj1
    assert objects[1] == obj2
    assert objects[2] == obj3

    objects = await TestModel.get_any([obj1.id, obj3.id])
    assert len(objects) == 2
    assert objects[0] == obj1
    assert objects[1] == obj3

    objects = await TestModel.get_any([-1, obj1.id, 999999, obj3.id, 0])
    assert len(objects) == 5
    assert objects[0] is None
    assert objects[1] == obj1
    assert objects[2] is None
    assert objects[3] == obj3
    assert objects[4] is None

    assert _construct_counter == 10
    assert _construct_rela_counter == _construct_counter
    assert _construct_list_counter == (5 if TestModel.has_cache() else 4)
    assert _construct_rela_list_counter == 4
    assert _reload_rela_counter == _construct_counter


@pytest.mark.asyncio
async def test_count(data_ctx, TestModel, build_calls_counter):
    obj1 = await TestModel.create(dict(data='1'))
    obj2 = await TestModel.create(dict(data='2'))
    obj3 = await TestModel.create(dict(data='3'))

    res = await TestModel.count()
    assert res == 3

    res = await TestModel.count([])
    assert res == 3

    res = await TestModel.count([TestModel.data == '-1'])
    assert res == 0

    res = await TestModel.count([TestModel.data == '1'])
    assert res == 1

    res = await TestModel.count([TestModel.data == '1', TestModel.data == '2'])
    assert res == 0

    res = await TestModel.count([(TestModel.data == '1') | (TestModel.data == '2')])
    assert res == 2

    res = await TestModel.count([(TestModel.data == '1') & (TestModel.id == obj1.id)])
    assert res == 1

    res = await TestModel.count([text('data > :data')], params=dict(data='1'))
    assert res == 2

    assert _construct_counter == 3
    assert _construct_rela_counter == _construct_counter
    assert _construct_list_counter == 0
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_counter


@pytest.mark.asyncio
async def test_exists(data_ctx, TestModel, build_calls_counter):
    obj1 = await TestModel.create(dict(data='1'))
    obj2 = await TestModel.create(dict(data='2'))
    obj3 = await TestModel.create(dict(data='3'))

    res = await TestModel.exists(obj1.id)
    assert res is True

    res = await TestModel.exists(-1)
    assert res is False

    res = await TestModel.exists_by([])
    assert res is False

    res = await TestModel.exists_by([TestModel.data == '-1'])
    assert res is False

    res = await TestModel.exists_by([TestModel.data == '1'])
    assert res is True

    res = await TestModel.exists_by([TestModel.data == '1', TestModel.data == '2'])
    assert res is False

    res = await TestModel.exists_by([(TestModel.data == '1') | (TestModel.data == '2')])
    assert res is True

    res = await TestModel.exists_by([(TestModel.data == '1') & (TestModel.id == obj1.id)])
    assert res is True

    res = await TestModel.exists_by([text('data > :data')], params=dict(data='1'))
    assert res is True

    res = await TestModel.exists_by([text('data > :data')], params=dict(data='3'))
    assert res is False

    assert _construct_counter == 3
    assert _construct_rela_counter == _construct_counter
    assert _construct_list_counter == 0
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_counter


@pytest.mark.asyncio
async def test_delete(data_ctx, TestModel, build_calls_counter):
    obj = await TestModel.create(dict(data='123'))

    objects = await TestModel.list()
    assert len(objects) == 1
    assert objects[0] == obj
    obj2 = await TestModel.get(obj.id)
    assert obj == obj2

    assert (await obj.delete()) is True

    objects = await TestModel.list()
    assert len(objects) == 0
    obj2 = await TestModel.get(obj.id)
    assert obj2 is None

    assert (await obj.delete()) is False

    assert _construct_counter == (2 if TestModel.has_cache() else 3)
    assert _construct_rela_counter == 3
    assert _construct_list_counter == 2
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_rela_counter


@pytest.mark.asyncio
async def test_delete_by_id(data_ctx, TestModel, build_calls_counter):
    obj = await TestModel.create(dict(data='123'))

    objects = await TestModel.list()
    assert len(objects) == 1
    assert objects[0] == obj
    obj2 = await TestModel.get(obj.id)
    assert obj == obj2

    assert (await TestModel.delete_by_id(obj.id)) is True

    objects = await TestModel.list()
    assert len(objects) == 0
    obj2 = await TestModel.get(obj.id)
    assert obj2 is None

    assert (await TestModel.delete_by_id(obj.id)) is False
    assert (await TestModel.delete_by_id(-1)) is False

    assert _construct_counter == (2 if TestModel.has_cache() else 3)
    assert _construct_rela_counter == 3
    assert _construct_list_counter == 2
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == 3


@pytest.mark.asyncio
async def test_save_and_load(data_ctx, TestModel, build_calls_counter):
    m = TestModel()
    m.id = randint(1, 1000000)
    m.data = 'qwer'
    assert m.create_date is None

    assert not await TestModel.get(m.id)

    assert await m.save()
    assert isinstance(m.create_date, datetime)

    m2 = await TestModel.get(m.id)
    assert m2.id == m.id
    assert m2.data == m.data
    assert isinstance(m2.create_date, datetime)
    assert m2.create_date == m.create_date

    m2.id = 1234
    m2.data = 'qwerty'
    m2.create_date = datetime.now()
    assert await m2.save(updated_fields=['id', 'create_date'])

    m3 = await TestModel.get(1234)
    assert m3.id == 1234
    assert m3.data == 'qwer'
    assert m3.create_date.replace(microsecond=0) == m2.create_date.replace(microsecond=0)

    assert await m2.load()
    assert m2.id == 1234
    assert m2.data == 'qwer'

    assert _construct_counter == (1 if TestModel.has_cache() else 2)
    assert _construct_rela_counter == 2
    assert _construct_list_counter == 0
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_rela_counter + 3


@pytest.mark.asyncio
async def test_save_all(data_ctx, TestModel, build_calls_counter):
    obj1 = TestModel(data='1')
    obj2 = TestModel(data='2')
    obj3 = TestModel(data='3')

    assert await TestModel.save_all([obj1, obj2, obj3])

    objects = await TestModel.get_any([obj1.id, obj2.id, obj3.id])
    assert len(objects) == 3
    assert objects[0] == obj1
    assert objects[1] == obj2
    assert objects[2] == obj3
    assert objects[0].id == obj1.id
    assert objects[0].data == obj1.data
    assert objects[1].id == obj2.id
    assert objects[1].data == obj2.data
    assert objects[2].id == obj3.id
    assert objects[2].data == obj3.data

    obj1.data = '4'
    obj2.data = '5'
    obj3.data = '6'

    assert await TestModel.save_all([obj1, obj2, obj3])

    objects = await TestModel.get_any([obj1.id, obj2.id, obj3.id])
    assert len(objects) == 3
    assert objects[0] == obj1
    assert objects[1] == obj2
    assert objects[2] == obj3
    assert objects[0].id == obj1.id
    assert objects[0].data == obj1.data
    assert objects[1].id == obj2.id
    assert objects[1].data == obj2.data
    assert objects[2].id == obj3.id
    assert objects[2].data == obj3.data

    assert _construct_counter == 6
    assert _construct_rela_counter == _construct_counter
    assert _construct_list_counter == 2
    assert _construct_rela_list_counter == _construct_list_counter
    assert _reload_rela_counter == _construct_counter
