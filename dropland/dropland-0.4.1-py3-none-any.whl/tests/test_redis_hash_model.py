import pytest

from dropland.storages.redis import USE_REDIS

pytestmark = pytest.mark.skipif(not USE_REDIS, reason='For Redis only')

if USE_REDIS:
    from .redis_models_data import redis_engine


    class TestModel(redis_engine.HashModel):
        a: int = 1
        b: str = '123'

        def __init__(self):
            self.a = 1
            self.b = '123'

        def get_id_value(self):
            return self.a


@pytest.mark.asyncio
async def test_model_fields(redis_ctx):
    assert TestModel.get_model_cache_key() == 'dropland.models.TestModel'
    assert TestModel.get_cache_key(1) == 'dropland.models.TestModel:1'
    assert TestModel.get_cache_id(123) == '123'
    assert TestModel.get_engine() is redis_engine


@pytest.mark.asyncio
async def test_model_serde(redis_ctx):
    m = TestModel()
    assert m.a == 1
    assert m.b == '123'

    assert TestModel.get_fields() == {'a', 'b'}
    assert m.get_values() == {'a': 1, 'b': '123'}

    ser = m.serialize()
    assert isinstance(ser, bytes)
    res = TestModel.deserialize(ser)
    assert isinstance(res, dict)

    assert res['a'] == 1
    assert res['b'] == '123'


@pytest.mark.asyncio
async def test_exists_save_and_get(redis_ctx):
    m = TestModel()

    assert not await TestModel.exists(1)
    assert not await TestModel.get(1)

    assert await m.save()
    assert await TestModel.exists(1)

    m2 = await TestModel.get(1)
    assert m2.a == 1
    assert m2.b == '123'

    await m.drop()
    assert not await TestModel.exists(1)
    assert not await TestModel.get(1)


@pytest.mark.asyncio
async def test_load(redis_ctx):
    m = TestModel()

    assert not await m.load()
    assert await m.save()
    assert await m.load()

    assert m.a == 1
    assert m.b == '123'

    m.b = None
    assert m.a == 1
    assert m.b is None

    assert await m.load()
    assert m.a == 1
    assert m.b == '123'


@pytest.mark.asyncio
async def test_drop(redis_ctx):
    m = TestModel()
    await m.save()

    m2 = await TestModel.get(1)
    assert m2.a == 1
    assert m2.b == '123'

    assert await m.load()
    assert m.a == 1
    assert m.b == '123'

    assert await TestModel.exists(1)
    assert await m.drop()
    assert not await m.drop()

    assert not await TestModel.exists(1)
    assert not await TestModel.get(1)
    assert not await m.load()


@pytest.mark.asyncio
async def test_save_all_get_any_and_scan(redis_ctx):
    m, m2 = TestModel(), TestModel()
    m2.a = 2

    assert await TestModel.save_all([m, m2])

    objects = await TestModel.get_any([])
    assert len(objects) == 0

    objects = await TestModel.get_any([1, 2])
    assert len(objects) == 2
    assert objects[0].a == 1
    assert objects[1].a == 2

    objects = await TestModel.get_any([-1, 1, 999999, 2, 0])
    assert len(objects) == 5
    assert objects[0] is None
    assert objects[1].a == 1
    assert objects[2] is None
    assert objects[3].a == 2
    assert objects[4] is None

    objects = {k: v async for k, v in TestModel.scan('*')}
    assert len(objects) == 2
    assert objects['1'].a == 1
    assert objects['2'].a == 2


@pytest.mark.asyncio
async def test_drop_all(redis_ctx):
    m, m2 = TestModel(), TestModel()
    m2.a = 2

    assert await TestModel.save_all([m, m2])
    objects = await TestModel.get_any([1, 2])
    assert len(objects) == 2
    assert objects[0].a == 1
    assert objects[1].a == 2

    assert await TestModel.drop_all([1, 2])
    assert not await TestModel.drop_all([1, 2])

    objects = await TestModel.get_any([1, 2])
    assert objects == [None, None]
