import asyncio
import logging
import os
import pickle
import time
import warnings
from unittest import mock

import asynctest
import yaaredis

from . import (
    Torrelque,
    TorrelqueError,
    TorrelqueLookupError,
    TorrelqueTaskStatus,
    TorrelqueTimeoutError,
)


def setUpModule():
    logging.basicConfig(level=logging.WARNING)
    warnings.simplefilter('error')


class TestTorrelque(asynctest.TestCase):

    redis = None
    testee = None

    async def setUp(self):
        dsn = os.getenv('TEST_REDIS_DSN', 'redis://localhost/1')
        self.redis = yaaredis.StrictRedis.from_url(dsn)
        self.testee = Torrelque(self.redis)

        await self.redis.flushdb()
        await self.redis.config_set('notify-keyspace-events', 'KA')

    def tearDown(self):
        self.redis.connection_pool.disconnect()

    def test_instantiation_error(self):
        with self.assertRaises(TorrelqueError) as ctx:
            Torrelque(object())
        self.assertEqual('yaaredis.StrictRedis instance expected', str(ctx.exception))

    async def _get_queue_state(self):
        pending = await self.redis.lrange(self.testee.keys['pending'], 0, -1)
        working = await self.redis.zrange(self.testee.keys['working'], 0, -1, withscores=True)
        delayed = await self.redis.zrange(self.testee.keys['delayed'], 0, -1, withscores=True)
        tasks = await self.redis.hgetall(self.testee.keys['tasks'])
        return pending, working, delayed, tasks

    async def test_enqueue(self):
        now = time.time()

        task_id1 = await self.testee.enqueue({'foo': 123}, task_timeout=5)
        task_id2 = await self.testee.enqueue({'bar': [1, 2, 3]})

        self.assertEqual(32, len(task_id1))
        self.assertEqual(5, (await self.testee.get_task_state(task_id1)).timeout)

        self.assertEqual(32, len(task_id2))
        self.assertEqual(300, (await self.testee.get_task_state(task_id2)).timeout)

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 2, 'delayed': 0, 'tasks': 2}, actual)

        actual = (await self.testee.get_task_state(task_id1))._asdict()
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertEqual({
            'timeout': 5,
            'last_requeue_time': None,
            'last_dequeue_time': None,
            'requeue_count': 0,
            'dequeue_count': 0,
            'status': TorrelqueTaskStatus.PENDING,
            'result': None,
            'release_time': None,
        }, actual)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([task_id2, task_id1], list(map(bytes.decode, pending)))
        self.assertEqual([], working)
        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1.encode(): b'{"foo": 123}',
            task_id2.encode(): b'{"bar": [1, 2, 3]}'
        }, tasks)

    async def test_enqueue_delayed(self):
        now = time.time()

        task_id = await self.testee.enqueue({'foo': 'bar'}, task_timeout=5, delay=30)
        task_state = (await self.testee.get_task_state(task_id))._asdict()
        self.assertAlmostEqual(now, task_state.pop('enqueue_time'), delta=0.1)
        self.assertEqual({
            'status': TorrelqueTaskStatus.DELAYED,
            'timeout': 5.0,
            'last_dequeue_time': None,
            'dequeue_count': 0,
            'last_requeue_time': None,
            'requeue_count': 0,
            'result': None,
            'release_time': None,
        }, task_state)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertTrue([] == pending == working)
        self.assertEqual({task_id.encode(): b'{"foo": "bar"}'}, tasks)
        self.assertEqual(1, len(delayed))
        self.assertEqual(2, len(delayed[0]))
        self.assertEqual(task_id.encode(), delayed[0][0])
        self.assertAlmostEqual(now + 30, delayed[0][1], delta=0.1)

    async def test_enqueue_bulk(self):
        now = time.time()
        async with await self.redis.pipeline(transaction=True) as pipeline:
            task_id1 = await self.testee.enqueue({'foo': 123}, task_timeout=5, pipeline=pipeline)
            task_id2 = await self.testee.enqueue({'bar': [1, 2, 3]}, pipeline=pipeline)
            await pipeline.execute()

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 2, 'delayed': 0, 'tasks': 2}, actual)

        actual = (await self.testee.get_task_state(task_id1))._asdict()
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertEqual({
            'timeout': 5,
            'last_requeue_time': None,
            'last_dequeue_time': None,
            'requeue_count': 0,
            'dequeue_count': 0,
            'status': TorrelqueTaskStatus.PENDING,
            'result': None,
            'release_time': None,
        }, actual)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([task_id2, task_id1], list(map(bytes.decode, pending)))
        self.assertEqual([], working)
        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1.encode(): b'{"foo": 123}',
            task_id2.encode(): b'{"bar": [1, 2, 3]}'
        }, tasks)

    async def test_dequeue(self):
        now = time.time()

        task_id1 = await self.testee.enqueue({'foo': 123}, task_timeout=5)
        task_id2 = await self.testee.enqueue({'bar': [1, 2, 3]})

        # dequeue first task
        task_id, task_data = await self.testee.dequeue()
        self.assertEqual(task_id1, task_id)
        self.assertEqual({'foo': 123}, task_data)

        actual = await self.testee.get_queue_stats()
        self.assertEqual({'working': 1, 'pending': 1, 'delayed': 0, 'tasks': 2}, actual._asdict())

        actual = (await self.testee.get_task_state(task_id1))._asdict()
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
        self.assertEqual({
            'last_requeue_time': None,
            'requeue_count': 0,
            'dequeue_count': 1,
            'timeout': 5,
            'status': TorrelqueTaskStatus.WORKING,
            'result': None,
            'release_time': None,
        }, actual)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([task_id2.encode()], pending)

        self.assertEqual(1, len(working))
        self.assertEqual(task_id1.encode(), working[0][0])
        self.assertAlmostEqual(now + 5, working[0][1], delta=0.2)

        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1.encode(): b'{"foo": 123}',
            task_id2.encode(): b'{"bar": [1, 2, 3]}'
        }, tasks)

        # dequeue second task
        task_id, task_data = await self.testee.dequeue()
        self.assertEqual(task_id2, task_id)
        self.assertEqual({'bar': [1, 2, 3]}, task_data)

        actual = await self.testee.get_queue_stats()
        self.assertEqual({'working': 2, 'pending': 0, 'delayed': 0, 'tasks': 2}, actual._asdict())

        actual = (await self.testee.get_task_state(task_id1))._asdict()
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
        self.assertEqual({
            'last_requeue_time': None,
            'requeue_count': 0,
            'dequeue_count': 1,
            'timeout': 5,
            'status': TorrelqueTaskStatus.WORKING,
            'result': None,
            'release_time': None,
        }, actual)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([], pending)

        self.assertEqual(2, len(working))
        self.assertEqual(task_id1.encode(), working[0][0])
        self.assertAlmostEqual(now + 5, working[0][1], delta=0.2)
        self.assertEqual(task_id2.encode(), working[1][0])
        self.assertAlmostEqual(now + 300, working[1][1], delta=0.2)

        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1.encode(): b'{"foo": 123}',
            task_id2.encode(): b'{"bar": [1, 2, 3]}'
        }, tasks)

        # dequeue with timeout on empty queue
        with self.assertRaises(TorrelqueTimeoutError):
            await self.testee.dequeue(timeout=1)

    async def test_dequeue_concurrent(self):
        task_id1 = await self.testee.enqueue({'foo': 123}, task_timeout=5)
        task_id2 = await self.testee.enqueue({'bar': [1, 2, 3]})

        actual = set()

        async def create_consumer():
            queue = Torrelque(self.redis)
            while True:
                task_id, _ = await queue.dequeue()
                actual.add(task_id)
                await queue.release(task_id)

        async def run_consumers():
            await asyncio.gather(*[create_consumer() for _ in range(8)])

        consumer_task = self.loop.create_task(run_consumers())

        async for _ in self.testee.watch(task_id2):
            pass

        self.assertEqual({task_id1, task_id2}, actual)

        consumer_task.cancel()

    async def test_dequeue_timeout_redis(self):
        with self.assertRaises(TorrelqueTimeoutError):
            await self.testee.dequeue(timeout=1)

    async def test_dequeue_bulk(self):
        now = time.time()
        task_ids = []
        async with await self.redis.pipeline(transaction=True) as pipeline:
            for i in range(10):
                task_id = await self.testee.enqueue({'i': i}, pipeline=pipeline)
                task_ids.append(task_id)
            await pipeline.execute()

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 10, 'delayed': 0, 'tasks': 10}, actual)

        expected = list(zip(task_ids[:8], [{'i': i} for i in range(8)]))
        actual = await self.testee.dequeue(max_tasks=8)
        self.assertEqual(expected, actual)

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 8, 'pending': 2, 'delayed': 0, 'tasks': 10}, actual)

        for task_id in task_ids[:8]:
            actual = (await self.testee.get_task_state(task_id))._asdict()
            self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
            self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
            self.assertEqual({
                'last_requeue_time': None,
                'requeue_count': 0,
                'dequeue_count': 1,
                'timeout': 300,
                'status': TorrelqueTaskStatus.WORKING,
                'result': None,
                'release_time': None,
            }, actual)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([task_ids[9].encode(), task_ids[8].encode()], pending)

        self.assertEqual(8, len(working))
        for i, task_id in enumerate(task_ids[:8]):
            self.assertEqual(task_id.encode(), working[i][0])
        self.assertAlmostEqual(now + self.testee.task_timeout, working[0][1], delta=0.2)

        self.assertEqual([], delayed)

        expected = {}
        for i, task_id in enumerate(task_ids):
            expected[task_id.encode()] = self.testee._serialiser.dumps({'i': i})
        self.assertEqual(expected, tasks)

        # dequeue again
        expected = list(zip(task_ids[8:], [{'i': i} for i in range(8, 10)]))
        actual = await self.testee.dequeue(max_tasks=8)
        self.assertEqual(expected, actual)

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 10, 'pending': 0, 'delayed': 0, 'tasks': 10}, actual)

        for task_id in task_ids[8:]:
            actual = (await self.testee.get_task_state(task_id))._asdict()
            self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
            self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
            self.assertEqual({
                'last_requeue_time': None,
                'requeue_count': 0,
                'dequeue_count': 1,
                'timeout': 300,
                'status': TorrelqueTaskStatus.WORKING,
                'result': None,
                'release_time': None,
            }, actual)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([], pending)

        self.assertEqual(10, len(working))
        for i, task_id in enumerate(task_ids[8:], start=8):
            self.assertEqual(task_id.encode(), working[i][0])
        self.assertAlmostEqual(now + self.testee.task_timeout, working[0][1], delta=0.2)

        self.assertEqual([], delayed)

        expected = {}
        for i, task_id in enumerate(task_ids):
            expected[task_id.encode()] = self.testee._serialiser.dumps({'i': i})
        self.assertEqual(expected, tasks)

        # dequeue with timeout on empty queue
        with self.assertRaises(TorrelqueTimeoutError):
            await self.testee.dequeue(max_tasks=4, timeout=1)

    async def test_dequeue_not_found_in_dequeueing(self):
        task_id = await self.testee.enqueue({'foo': 'bar'}, task_timeout=5)
        self.testee.schedule_sweep(0.1)

        orig_call_script = self.testee._call_script

        async def call_script(name, *args):
            if name == 'dequeue':
                await asyncio.sleep(0.2)
            return await orig_call_script(name, *args)

        with mock.patch.object(self.testee, '_call_script', call_script):
            with self.assertRaises(TorrelqueLookupError) as exctx:
                with self.assertLogs(level='WARNING') as logctx:
                    await self.testee.dequeue()

        self.assertEqual(
            [f'WARNING:torrelque:Task:{task_id} not found in dequeueing list'], logctx.output
        )
        self.assertEqual('Failed to dequeue pending task', str(exctx.exception))

        self.testee.unschedule_sweep()

    async def test_requeue(self):
        now = time.time()

        task_id1 = await self.testee.enqueue({'foo': 123}, task_timeout=5)
        task_id2 = await self.testee.enqueue({'bar': [1, 2, 3]})

        task_id, _ = await self.testee.dequeue()
        await self.testee.requeue(task_id)

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 2, 'delayed': 0, 'tasks': 2}, actual)

        actual = (await self.testee.get_task_state(task_id1))._asdict()
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
        self.assertAlmostEqual(now, actual.pop('last_requeue_time'), delta=0.2)
        self.assertEqual({
            'requeue_count': 1,
            'dequeue_count': 1,
            'timeout': 5,
            'status': TorrelqueTaskStatus.PENDING,
            'result': None,
            'release_time': None,
        }, actual)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([task_id1, task_id2], list(map(bytes.decode, pending)))
        self.assertEqual([], working)
        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1.encode(): b'{"foo": 123}',
            task_id2.encode(): b'{"bar": [1, 2, 3]}'
        }, tasks)

    async def test_requeue_delayed(self):
        now = time.time()

        task_id1 = await self.testee.enqueue({'foo': 123}, task_timeout=5)
        task_id2 = await self.testee.enqueue({'bar': [1, 2, 3]})

        task_id, _ = await self.testee.dequeue()
        await self.testee.requeue(task_id, delay=3600)

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 1, 'delayed': 1, 'tasks': 2}, actual)

        actual = (await self.testee.get_task_state(task_id1))._asdict()
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
        self.assertEqual({
            'last_requeue_time' : None,
            'requeue_count': 0,
            'dequeue_count': 1,
            'timeout': 5,
            'status': TorrelqueTaskStatus.DELAYED,
            'result': None,
            'release_time': None,
        }, actual)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([task_id2.encode()], pending)

        self.assertEqual([], working)

        self.assertEqual(1, len(delayed))
        self.assertEqual(task_id1.encode(), delayed[0][0])
        self.assertAlmostEqual(now + 3600, delayed[0][1], delta=0.2)

        self.assertEqual({
            task_id1.encode(): b'{"foo": 123}',
            task_id2.encode(): b'{"bar": [1, 2, 3]}'
        }, tasks)

    async def test_requeue_twice(self):
        now = time.time()

        task_ids = []
        task_ids.append(await self.testee.enqueue({'foo': 'bar'}))

        task_id, _ = await self.testee.dequeue()
        task_ids.append(task_id)
        await self.testee.requeue(task_id)

        task_id, _ = await self.testee.dequeue()
        task_ids.append(task_id)
        await self.testee.requeue(task_id)

        task_id, _ = await self.testee.dequeue()
        task_ids.append(task_id)
        await self.testee.release(task_id, result=1)

        self.assertEqual({task_id}, set(task_ids))

        expected = {
            'status': TorrelqueTaskStatus.COMPLETED,
            'timeout': 300.0,
            'dequeue_count': 3,
            'requeue_count': 2,
            'result': 1
        }
        actual = (await self.testee.get_task_state(task_id))._asdict()
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('last_requeue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('release_time'), delta=0.1)
        self.assertEqual(expected, actual)

    async def test_requeue_reset_task_timeout(self):
        now = time.time()

        task_id_orig = await self.testee.enqueue({'foo': 123}, task_timeout=5)

        task_id, _ = await self.testee.dequeue()
        self.assertEqual(task_id_orig, task_id)
        await self.testee.requeue(task_id, task_timeout=10)

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 1, 'delayed': 0, 'tasks': 1}, actual)

        actual = (await self.testee.get_task_state(task_id))._asdict()
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
        self.assertAlmostEqual(now, actual.pop('last_requeue_time'), delta=0.2)
        self.assertEqual({
            'requeue_count': 1,
            'dequeue_count': 1,
            'timeout': 10,
            'status': TorrelqueTaskStatus.PENDING,
            'result': None,
            'release_time': None,
        }, actual)

    async def test_requeue_nonexistent(self):
        with self.assertLogs(level='WARNING') as ctx:
            await self.testee.requeue('123')
        self.assertEqual(
            ['WARNING:torrelque:Inconsistent requeue of task:123: [0, 1, 1, 1, 1]'], ctx.output
        )

    async def test_requeue_bulk(self):
        now = time.time()
        task_ids = []
        async with await self.redis.pipeline(transaction=True) as pipeline:
            for i in range(10):
                task_id = await self.testee.enqueue({'i': i}, pipeline=pipeline)
                task_ids.append(task_id)
            await pipeline.execute()

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 10, 'delayed': 0, 'tasks': 10}, actual)
        dequeued = await self.testee.dequeue(max_tasks=8)

        async with await self.redis.pipeline(transaction=True) as pipeline:
            for task_id, _ in dequeued[:5]:
                await self.testee.requeue(task_id, pipeline=pipeline)
            await pipeline.execute()

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 3, 'pending': 7, 'delayed': 0, 'tasks': 10}, actual)

        for task_id, _ in dequeued[:5]:
            actual = (await self.testee.get_task_state(task_id))._asdict()
            self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
            self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
            self.assertAlmostEqual(now, actual.pop('last_requeue_time'), delta=0.2)
            self.assertEqual({
                'requeue_count': 1,
                'dequeue_count': 1,
                'timeout': 300,
                'status': TorrelqueTaskStatus.PENDING,
                'result': None,
                'release_time': None,
            }, actual)

        for task_id, _ in dequeued[5:]:
            actual = (await self.testee.get_task_state(task_id))._asdict()
            self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
            self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
            self.assertEqual({
                'last_requeue_time': None,
                'requeue_count': 0,
                'dequeue_count': 1,
                'timeout': 300,
                'status': TorrelqueTaskStatus.WORKING,
                'result': None,
                'release_time': None,
            }, actual)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual(
            [task_id.encode() for task_id in task_ids[4::-1] + task_ids[:7:-1]],
            pending,
        )

        self.assertEqual(3, len(working))
        for i, task_id in enumerate(task_ids[5:8]):
            self.assertEqual(task_id.encode(), working[i][0])
        self.assertAlmostEqual(now + self.testee.task_timeout, working[0][1], delta=0.2)

        self.assertEqual([], delayed)

        expected = {}
        for i, task_id in enumerate(task_ids):
            expected[task_id.encode()] = self.testee._serialiser.dumps({'i': i})
        self.assertEqual(expected, tasks)

    async def test_release(self):
        await self.testee.enqueue({'foo': 123}, task_timeout=5)
        task_id2 = await self.testee.enqueue({'bar': [1, 2, 3]})

        task_id, _ = await self.testee.dequeue()
        await self.testee.release(task_id)

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 1, 'delayed': 0, 'tasks': 1}, actual)

        with self.assertRaises(TorrelqueLookupError):
            await self.testee.get_task_state(task_id)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([task_id2.encode()], pending)
        self.assertEqual([], working)
        self.assertEqual([], delayed)
        self.assertEqual({task_id2.encode(): b'{"bar": [1, 2, 3]}'}, tasks)

    async def test_release_nonexistent(self):
        with self.assertLogs(level='WARNING') as ctx:
            await self.testee.release('123')
        self.assertEqual(
            ['WARNING:torrelque:Inconsistent release of task:123: [0, 0, 0]'], ctx.output
        )

    async def test_release_result(self):
        now = time.time()
        await self.testee.enqueue({'foo': 123}, task_timeout=5)

        task_id, _ = await self.testee.dequeue()
        await self.testee.release(task_id, result={'foo': 26, 'bar': 10})

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 0, 'delayed': 0, 'tasks': 0}, actual)

        actual = (await self.testee.get_task_state(task_id))._asdict()
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
        self.assertAlmostEqual(now, actual.pop('release_time'), delta=0.2)
        self.assertEqual({
            'requeue_count': 0,
            'dequeue_count': 1,
            'timeout': 5,
            'last_requeue_time': None,
            'status': TorrelqueTaskStatus.COMPLETED,
            'result': {'bar': 10, 'foo': 26},
        }, actual)
        self.assertEqual(3600, await self.redis.ttl(self.testee._get_state_key(task_id)))

        now = time.time()
        await self.testee.enqueue({'bar': [1, 2, 3]})

        task_id, _ = await self.testee.dequeue()
        await self.testee.release(
            task_id,
            result={'foo': 9, 'bar': 5},
            result_ttl=10,
            status=TorrelqueTaskStatus.REJECTED,
        )

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 0, 'delayed': 0, 'tasks': 0}, actual)

        actual = (await self.testee.get_task_state(task_id))._asdict()
        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
        self.assertAlmostEqual(now, actual.pop('release_time'), delta=0.2)
        self.assertEqual({
            'requeue_count': 0,
            'dequeue_count': 1,
            'timeout': 300,
            'last_requeue_time': None,
            'status': TorrelqueTaskStatus.REJECTED,
            'result': {'bar': 5, 'foo': 9},
        }, actual)
        self.assertEqual(10, await self.redis.ttl(self.testee._get_state_key(task_id)))

    async def test_release_result_invalid_status(self):
        with self.assertRaises(TorrelqueError) as ctx:
            await self.testee.release('aabbccdd', result=26, status=TorrelqueTaskStatus.DELAYED)
        self.assertEqual('Invalid status for released task: 2', str(ctx.exception))

    async def test_release_bulk(self):
        now = time.time()
        task_ids = []
        async with await self.redis.pipeline(transaction=True) as pipeline:
            for i in range(10):
                task_id = await self.testee.enqueue({'i': i}, pipeline=pipeline)
                task_ids.append(task_id)
            await pipeline.execute()

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 10, 'delayed': 0, 'tasks': 10}, actual)
        dequeued = await self.testee.dequeue(max_tasks=8)

        async with await self.redis.pipeline(transaction=True) as pipeline:
            for task_id, _ in dequeued[:5]:
                await self.testee.release(task_id, pipeline=pipeline, result=42)
            await pipeline.execute()

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 3, 'pending': 2, 'delayed': 0, 'tasks': 5}, actual)

        for task_id, _ in dequeued[:5]:
            actual = (await self.testee.get_task_state(task_id))._asdict()
            self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
            self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
            self.assertAlmostEqual(now, actual.pop('release_time'), delta=0.2)
            self.assertEqual({
                'last_requeue_time': None,
                'requeue_count': 0,
                'dequeue_count': 1,
                'timeout': 300,
                'status': TorrelqueTaskStatus.COMPLETED,
                'result': 42,
            }, actual)

        for task_id, _ in dequeued[5:]:
            actual = (await self.testee.get_task_state(task_id))._asdict()
            self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
            self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.2)
            self.assertEqual({
                'last_requeue_time': None,
                'requeue_count': 0,
                'dequeue_count': 1,
                'timeout': 300,
                'status': TorrelqueTaskStatus.WORKING,
                'result': None,
                'release_time': None,
            }, actual)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([task_id.encode() for task_id in task_ids[:7:-1]], pending)

        self.assertEqual(3, len(working))
        for i, task_id in enumerate(task_ids[5:8]):
            self.assertEqual(task_id.encode(), working[i][0])
        self.assertAlmostEqual(now + self.testee.task_timeout, working[0][1], delta=0.2)

        self.assertEqual([], delayed)

        expected = {}
        for i, task_id in list(enumerate(task_ids))[5:]:
            expected[task_id.encode()] = self.testee._serialiser.dumps({'i': i})
        self.assertEqual(expected, tasks)

    async def test_watch(self):
        now = time.time()

        task_id = await self.testee.enqueue({'gaia': 'gaia'})

        states = []

        async def watch():
            async for state in self.testee.watch(task_id):
                states.append(state._asdict())

        watch_task = self.loop.create_task(watch())
        # Watch is typically on the producer's side, but here and below
        # it needs more "space" on the loop to timely receive messages
        await asyncio.sleep(0)
        await self.testee.dequeue()
        await asyncio.sleep(0.05)
        await self.testee.requeue(task_id, task_timeout=30)
        await asyncio.sleep(0.05)
        await self.testee.dequeue()
        await asyncio.sleep(0.05)
        await self.testee.requeue(task_id, delay=0.04)
        await asyncio.sleep(0.05)
        await self.testee.sweep()
        await asyncio.sleep(0.05)
        await self.testee.dequeue()
        await asyncio.sleep(0.05)
        await self.testee.release(task_id)
        await asyncio.sleep(0.05)

        another_task_id = await self.testee.enqueue({'the art': 'of being'})
        await self.testee.dequeue()
        await self.testee.release(another_task_id)

        await watch_task

        for state in states:
            self.assertAlmostEqual(now, state.pop('enqueue_time'), delta=0.4)
            if state['last_dequeue_time']:
                self.assertAlmostEqual(now, state.pop('last_dequeue_time'), delta=0.4)
            if state['last_requeue_time']:
                self.assertAlmostEqual(now, state.pop('last_requeue_time'), delta=0.4)

        expected = [{
            'dequeue_count': 0,
            'last_dequeue_time': None,
            'last_requeue_time': None,
            'release_time': None,
            'requeue_count': 0,
            'result': None,
            'status': TorrelqueTaskStatus.PENDING,
            'timeout': 300.0
        }, {
            'dequeue_count': 1,
            'last_requeue_time': None,
            'release_time': None,
            'requeue_count': 0,
            'result': None,
            'status': TorrelqueTaskStatus.WORKING,
            'timeout': 300.0
        }, {
            'dequeue_count': 1,
            'release_time': None,
            'requeue_count': 1,
            'result': None,
            'status': TorrelqueTaskStatus.PENDING,
            'timeout': 30.0
        }, {
            'dequeue_count': 2,
            'release_time': None,
            'requeue_count': 1,
            'result': None,
            'status': TorrelqueTaskStatus.WORKING,
            'timeout': 30.0
        }, {
            'dequeue_count': 2,
            'release_time': None,
            'requeue_count': 1,
            'result': None,
            'status': TorrelqueTaskStatus.DELAYED,
            'timeout': 30.0
        }, {
            'dequeue_count': 2,
            'release_time': None,
            'requeue_count': 2,
            'result': None,
            'status': TorrelqueTaskStatus.PENDING,
            'timeout': 30.0
        }, {
            'dequeue_count': 3,
            'release_time': None,
            'requeue_count': 2,
            'result': None,
            'status': TorrelqueTaskStatus.WORKING,
            'timeout': 30.0
        }]
        self.assertEqual(states, expected)

    async def test_watch_result(self):
        now = time.time()

        task_id = await self.testee.enqueue({'falani': 'last'})

        states = []

        async def watch():
            async for state in self.testee.watch(task_id):
                states.append(state._asdict())

        watch_task = self.loop.create_task(watch())
        # Watch is typically on the producer's side, but here and below
        # it needs more "space" on the loop to timely receive messages
        await asyncio.sleep(0)
        await self.testee.dequeue()
        await asyncio.sleep(0.05)
        await self.testee.release(
            task_id, result={'some_status': 'ERROR'}, status=TorrelqueTaskStatus.REJECTED
        )
        await asyncio.sleep(0.05)

        await watch_task

        for state in states:
            self.assertAlmostEqual(now, state.pop('enqueue_time'), delta=0.1)
            if state['last_dequeue_time']:
                self.assertAlmostEqual(now, state.pop('last_dequeue_time'), delta=0.1)
            if state['release_time']:
                self.assertAlmostEqual(now, state.pop('release_time'), delta=0.1)

        expected = [{
            'dequeue_count': 0,
            'last_dequeue_time': None,
            'last_requeue_time': None,
            'release_time': None,
            'requeue_count': 0,
            'result': None,
            'status': TorrelqueTaskStatus.PENDING,
            'timeout': 300.0
        }, {
            'dequeue_count': 1,
            'last_requeue_time': None,
            'release_time': None,
            'requeue_count': 0,
            'result': None,
            'status': TorrelqueTaskStatus.WORKING,
            'timeout': 300.0
        }, {
            'dequeue_count': 1,
            'last_requeue_time': None,
            'requeue_count': 0,
            'result': {'some_status': 'ERROR'},
            'status': TorrelqueTaskStatus.REJECTED,
            'timeout': 300.0
        }]
        self.assertEqual(states, expected)

    async def test_watch_timeout(self):
        now = time.time()

        task_id = await self.testee.enqueue({'Subterfuge': '!'})

        states = []

        async def watch():
            async for state in self.testee.watch(task_id, timeout=0.1):
                states.append(state._asdict())

        watch_task = self.loop.create_task(watch())
        # Watch is typically on the producer's side, but here and below
        # it needs more "space" on the loop to timely receive messages
        await asyncio.sleep(0)
        await self.testee.dequeue()
        await asyncio.sleep(0.05)
        await self.testee.requeue(task_id, task_timeout=30)
        await asyncio.sleep(0.05)
        await self.testee.dequeue()
        await asyncio.sleep(0.05)

        with self.assertRaises(TorrelqueTimeoutError):
            await watch_task

        for state in states:
            self.assertAlmostEqual(now, state.pop('enqueue_time'), delta=0.1)
            if state['last_dequeue_time']:
                self.assertAlmostEqual(now, state.pop('last_dequeue_time'), delta=0.1)
            if state['last_requeue_time']:
                self.assertAlmostEqual(now, state.pop('last_requeue_time'), delta=0.1)

        expected = [{
            'dequeue_count': 0,
            'last_dequeue_time': None,
            'last_requeue_time': None,
            'release_time': None,
            'requeue_count': 0,
            'result': None,
            'status': TorrelqueTaskStatus.PENDING,
            'timeout': 300.0
        }, {
            'dequeue_count': 1,
            'last_requeue_time': None,
            'release_time': None,
            'requeue_count': 0,
            'result': None,
            'status': TorrelqueTaskStatus.WORKING,
            'timeout': 300.0
        }, {
            'dequeue_count': 1,
            'release_time': None,
            'requeue_count': 1,
            'result': None,
            'status': TorrelqueTaskStatus.PENDING,
            'timeout': 30.0
        }]
        self.assertEqual(states, expected)

    async def test_watch_nonexistent(self):
        with self.assertRaises(TorrelqueLookupError):
            async for _ in self.testee.watch('the road'):
                pass

    async def test_watch_released(self):
        now = time.time()

        task_id = await self.testee.enqueue({'foo': 'bar'})
        await self.testee.dequeue()
        await self.testee.release(task_id, result=1)

        actual = []
        async for state in self.testee.watch(task_id):
            actual.append(state._asdict())
        self.assertEqual(1, len(actual))
        actual = actual[0]

        self.assertAlmostEqual(now, actual.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('last_dequeue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual.pop('release_time'), delta=0.1)
        self.assertEqual({
            'last_requeue_time': None,
            'requeue_count': 0,
            'dequeue_count': 1,
            'timeout': 300,
            'status': TorrelqueTaskStatus.COMPLETED,
            'result': 1,
        }, actual)

    async def test_watch_invalid_keyspace_notification_config(self):
        await self.redis.config_set('notify-keyspace-events', 'Ez')
        with self.assertRaises(TorrelqueError) as ctx:
            async for _ in self.testee.watch('someid'):
                pass
        message = 'Redis notify-keyspace-events must include KA or Kgh'
        self.assertEqual(message, str(ctx.exception))

        await self.redis.config_set('notify-keyspace-events', '')
        with self.assertRaises(TorrelqueError) as ctx:
            async for _ in self.testee.watch('someid'):
                pass
        self.assertEqual(message, str(ctx.exception))

    async def test_watch_invalid_keyspace_notification_checked_once(self):
        task_id = await self.testee.enqueue({'foo': 'bar'})
        await self.testee.dequeue()
        await self.testee.release(task_id, result=1)

        with mock.patch.object(self.testee, '_redis', wraps=self.testee._redis) as spy:
            async for _ in self.testee.watch(task_id):
                pass
            async for _ in self.testee.watch(task_id):
                pass

            spy.config_get.assert_called_once()

    async def test_sweep(self):
        actual = await self.testee.sweep()
        self.assertEqual((0, 0, 0), actual)

        now = time.time()

        task_id1 = await self.testee.enqueue({'foo': 123}, task_timeout=0.1)
        task_id2 = await self.testee.enqueue({'bar': [1, 2, 3]})

        await self.testee.dequeue()
        await self.testee.dequeue()
        await self.testee.requeue(task_id2, delay=0.25)

        actual = await self.testee.sweep()
        self.assertEqual((0, 0, 0), actual)

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 1, 'pending': 0, 'delayed': 1, 'tasks': 2}, actual)

        actual_task1 = (await self.testee.get_task_state(task_id1))._asdict()
        self.assertAlmostEqual(now, actual_task1.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual_task1.pop('last_dequeue_time'), delta=0.1)
        self.assertEqual({
            'last_requeue_time': None,
            'requeue_count': 0,
            'dequeue_count': 1,
            'timeout': 0.1,
            'status': TorrelqueTaskStatus.WORKING,
            'result': None,
            'release_time': None,
        }, actual_task1)

        actual_task2 = (await self.testee.get_task_state(task_id2))._asdict()
        self.assertAlmostEqual(now, actual_task2.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual_task2.pop('last_dequeue_time'), delta=0.1)
        self.assertEqual({
            'last_requeue_time': None,
            'requeue_count': 0,
            'dequeue_count': 1,
            'timeout': 300,
            'status': TorrelqueTaskStatus.DELAYED,
            'result': None,
            'release_time': None,
        }, actual_task2)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([], pending)

        self.assertEqual(1, len(working))
        self.assertEqual(task_id1.encode(), working[0][0])
        self.assertAlmostEqual(now + 0.1, working[0][1], delta=0.1)

        self.assertEqual(1, len(delayed))
        self.assertEqual(task_id2.encode(), delayed[0][0])
        self.assertAlmostEqual(now + 0.25, delayed[0][1], delta=0.1)

        self.assertEqual({
            task_id1.encode(): b'{"foo": 123}',
            task_id2.encode(): b'{"bar": [1, 2, 3]}'
        }, tasks)

        await asyncio.sleep(0.25)

        requeue_time = time.time()
        actual = await self.testee.sweep()
        self.assertEqual((1, 1, 0), actual)

        actual = (await self.testee.get_queue_stats())._asdict()
        self.assertEqual({'working': 0, 'pending': 2, 'delayed': 0, 'tasks': 2}, actual)

        actual_task1 = (await self.testee.get_task_state(task_id1))._asdict()
        self.assertAlmostEqual(now, actual_task1.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual_task1.pop('last_dequeue_time'), delta=0.1)
        self.assertAlmostEqual(requeue_time, actual_task1.pop('last_requeue_time'), delta=0.1)
        self.assertEqual({
            'requeue_count': 1,
            'dequeue_count': 1,
            'timeout': 0.1,
            'status': TorrelqueTaskStatus.PENDING,
            'result': None,
            'release_time': None,
        }, actual_task1)

        actual_task2 = (await self.testee.get_task_state(task_id2))._asdict()
        self.assertAlmostEqual(now, actual_task2.pop('enqueue_time'), delta=0.1)
        self.assertAlmostEqual(now, actual_task2.pop('last_dequeue_time'), delta=0.1)
        self.assertAlmostEqual(requeue_time, actual_task2.pop('last_requeue_time'), delta=0.1)
        self.assertEqual({
            'requeue_count': 1,
            'dequeue_count': 1,
            'timeout': 300,
            'status': TorrelqueTaskStatus.PENDING,
            'result': None,
            'release_time': None,
        }, actual_task2)

        pending, working, delayed, tasks = await self._get_queue_state()
        self.assertEqual([task_id2, task_id1], list(map(bytes.decode, pending)))
        self.assertEqual([], working)
        self.assertEqual([], delayed)
        self.assertEqual({
            task_id1.encode(): b'{"foo": 123}',
            task_id2.encode(): b'{"bar": [1, 2, 3]}'
        }, tasks)

    async def test_sweep_schedule(self):
        self.testee = Torrelque(self.redis)
        self.testee.sweep_interval = 0.2

        task_id1 = await self.testee.enqueue({'foo': 123}, task_timeout=0.1)
        task_id2 = await self.testee.enqueue({'bar': [1, 2, 3]})

        await self.testee.dequeue()
        await self.testee.dequeue()
        await self.testee.requeue(task_id2, delay=0.15)

        self.testee.schedule_sweep()

        pending, _, _, _ = await self._get_queue_state()
        self.assertEqual([], pending)

        await asyncio.sleep(0.2)

        pending, _, _, _ = await self._get_queue_state()
        self.assertEqual([task_id2, task_id1], list(map(bytes.decode, pending)))

        # now release both and retry
        await self.testee.dequeue()
        await self.testee.dequeue()
        await self.testee.release(task_id1)
        await self.testee.release(task_id2)

        task_id1 = await self.testee.enqueue({'foo': 123}, task_timeout=0.1)
        task_id2 = await self.testee.enqueue({'bar': [1, 2, 3]})

        await self.testee.dequeue()
        await self.testee.dequeue()
        await self.testee.requeue(task_id2, delay=0.15)

        self.testee.unschedule_sweep()

        pending, _, _, _ = await self._get_queue_state()
        self.assertEqual([], pending)

        await asyncio.sleep(0.2)

        pending, _, _, _ = await self._get_queue_state()
        self.assertEqual([], pending)

    async def test_sweep_schedule_override_interval(self):
        self.testee.schedule_sweep(0.1)

        with self.assertLogs(level='DEBUG') as ctx:
            await asyncio.sleep(0.15)
        self.assertIn(
            'DEBUG:torrelque:Sweep has requeued: stale=0, delayed=0, undequeued=0', ctx.output
        )

        self.testee.unschedule_sweep()

    async def test_sweep_stale_dequeueing(self):
        task_ids = []
        async with await self.redis.pipeline(transaction=True) as pipeline:
            for i in range(10):
                task_id = await self.testee.enqueue({'i': i}, pipeline=pipeline)
                task_ids.append(task_id)
            await pipeline.execute()
        task_ids = list(reversed(task_ids))  # Queue order

        pending, _, _, _ = await self._get_queue_state()
        self.assertEqual(task_ids, list(map(bytes.decode, pending)))

        for i in range(8):
            await self.redis.rpoplpush(self.testee.keys['pending'], self.testee.keys['dequeueing'])

        self.testee.schedule_sweep(0.1)

        with self.assertLogs(level='DEBUG') as ctx:
            await asyncio.sleep(0.25)

        # Make sure undequeued task ids are returned on the second call
        self.assertEqual(
            [
                'DEBUG:torrelque:Sweep has requeued: stale=0, delayed=0, undequeued=0',
                'DEBUG:torrelque:Sweep has requeued: stale=0, delayed=0, undequeued=8',
            ],
            ctx.output[:2],
        )

        pending, working, delayed, _ = await self._get_queue_state()
        # Returned tasks are still FIFO, except tasks that didn't leave pending list
        self.assertEqual(task_ids[2:10] + task_ids[:2], list(map(bytes.decode, pending)))

        self.assertEqual([], working)
        self.assertEqual([], delayed)

        self.assertEqual(set(), await self.redis.smembers(self.testee.keys['undequeued']))

        self.testee.unschedule_sweep()

    async def test_sweep_schedule_coro_cancel(self):
        async def swleep():
            await asyncio.sleep(60)

        self.testee.sweep = swleep

        self.testee.schedule_sweep()
        await asyncio.sleep(0.01)
        self.testee.unschedule_sweep()

    async def test_custom_serialiser(self):
        self.testee = Torrelque(self.redis, serialiser=pickle)

        orig_task_data = {'bar': [1, 2, 3]}
        orig_task_id = await self.testee.enqueue(orig_task_data)

        task_id, task_data = await self.testee.dequeue()
        self.assertEqual(orig_task_id, task_id)
        self.assertEqual(orig_task_data, task_data)

        await self.testee.requeue(task_id)
        await self.testee.dequeue()
        await self.testee.release(task_id)

        self.assertEqual(([], [], [], {}), await self._get_queue_state())

    async def test_call_script(self):
        await self.redis.script_flush()

        with mock.patch.object(self.testee, '_redis', wraps=self.testee._redis) as spy:
            await self.testee.sweep()

            self.assertEqual(2, len(spy.mock_calls))
            spy.evalsha.assert_called_once()
            spy.eval.assert_called_once()

        with mock.patch.object(self.testee, '_redis', wraps=self.testee._redis) as spy:
            await self.testee.sweep()

            self.assertEqual(1, len(spy.mock_calls))
            spy.evalsha.assert_called_once()

    async def test_sweep_runner(self):
        sweep_mock = asyncio.Future()
        sweep_mock.set_result((2, 2, 1))
        error_list = [yaaredis.DataError(), sweep_mock]

        def one_error():
            obj = error_list.pop(0)
            if isinstance(obj, Exception):
                raise obj
            else:
                return obj

        with mock.patch.object(self.testee, 'sweep', mock.Mock(side_effect=one_error)):
            self.testee.schedule_sweep(0.1)

            with self.assertLogs('torrelque', 'ERROR') as ctx:
                await asyncio.sleep(0.1)
            self.assertEqual(1, len(ctx.output))
            self.assertIn('Sweep has failed with Redis error, continuing', ctx.output[0])

            with self.assertLogs('torrelque', 'DEBUG') as ctx:
                await asyncio.sleep(0.1)
            self.assertEqual(
                ['DEBUG:torrelque:Sweep has requeued: stale=2, delayed=2, undequeued=1'],
                ctx.output,
            )

            self.testee.unschedule_sweep()

        error_list = [ValueError()]

        with mock.patch.object(self.testee, 'sweep', mock.Mock(side_effect=one_error)) as m:
            self.testee.schedule_sweep(0.1)

            with self.assertLogs('torrelque', 'ERROR') as ctx:
                await asyncio.sleep(0.1)
            self.assertEqual(1, len(ctx.output))
            self.assertIn('Sweep has failed with unexpected error, stopping', ctx.output[0])
            self.assertEqual(1, len(m.mock_calls))

            await asyncio.sleep(0.1)
            self.assertEqual(1, len(m.mock_calls))

            self.testee.unschedule_sweep()
