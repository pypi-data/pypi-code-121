'''Asynchronous Redis-backed reliable queue package.'''


import asyncio
import contextlib
import enum
import hashlib
import json
import logging
import time
import uuid
from importlib.resources import read_text
from typing import Any, Callable, List, NamedTuple, Optional, Sequence, Tuple, Union

import yaaredis
from yaaredis.pipeline import StrictPipeline


__all__ = (
    'Torrelque',
    'TorrelqueQueueStats',
    'TorrelqueTaskStatus',
    'TorrelqueTaskState',
    'TorrelqueError',
    'TorrelqueTimeoutError',
    'TorrelqueLookupError',
    'TorrelqueTaskSerialiser',
)

logger = logging.getLogger(__package__)

TaskPair = Tuple[str, dict]


class TorrelqueTaskStatus(enum.IntEnum):
    '''Task status.'''

    PENDING = 0
    '''Task is enqueued.'''

    WORKING = 1
    '''Task is dequeued.'''

    DELAYED = 2
    '''Task is delayed.'''

    COMPLETED = 3
    '''Task is released, as the result of successful completion.'''

    REJECTED = 4
    '''Task is released, as the result of (multiple) failed attempts.'''

    def isfinal(self):
        '''Tells whether the status is final.'''

        return self in (self.COMPLETED, self.REJECTED)


class TorrelqueQueueStats(NamedTuple):
    '''Queue counters.'''

    tasks: int
    '''Total number of tasks in the queue.'''

    pending: int
    '''Number of pending tasks in the queue.'''

    working: int
    '''Number of working tasks in the queue.'''

    delayed: int
    '''Number of delayed tasks in the queue.'''


class TorrelqueTaskState(NamedTuple):
    '''Task state.'''

    status: TorrelqueTaskStatus
    '''Status of the task.'''

    timeout: float
    '''
    Execution timeout of the task after while it's considered stale.
    '''

    result: Any
    '''Optional result of the task with in a final state.'''

    dequeue_count: int
    '''Number of times the task was dequeued from the queue.'''

    requeue_count: int
    '''Number of times the task was requeued from the queue.'''

    enqueue_time: float
    '''Unix timestamp of the enqueue time of the task.'''

    last_dequeue_time: Optional[float]
    '''Optional Unix timestamp of the last dequeue time of the task.'''

    last_requeue_time: Optional[float]
    '''Optional Unix timestamp of the last requeue time of the task.'''

    release_time: Optional[float]
    '''
    Optional Unix timestamp of the release time of the task in a final
    status.
    '''


class TorrelqueTaskSerialiser(NamedTuple):
    '''Task serialisation delegate.'''

    dumps: Callable[[Any], bytes]
    '''Serialise task data.'''

    loads: Callable[[bytes], Any]
    '''Deserialise task data.'''


class TorrelqueError(Exception):
    '''Generic Torrelque error.'''


class TorrelqueTimeoutError(Exception):
    '''Torrelque timeout error.'''


class TorrelqueLookupError(Exception):
    '''Torrelque lookup error.'''


class Torrelque:
    '''
    Reliable work queue.

    :argument redis:
        Redis client instance.
    :argument queue:
        Name of the queue. Must match across producers and consumers.
    :argument serialiser:
        An object with ``dumps`` and ``loads`` that (de)serialises
        task bodies.
    :raises TorrelqueError:
        Not a ``yaaredis.StrictRedis`` instance passed.
    '''

    task_timeout = 300
    '''
    Default timeout for a task in the "working" set to be
    considered stale.
    '''

    sweep_interval = 30
    '''Default interval between sweep calls, when sweep is scheduled.'''

    result_ttl = 3600
    '''Default time-to-live of a task result (when applicable).'''

    keys = {
        'pending'    : 'pending',     # list
        'dequeueing' : 'dequeueing',  # list
        'undequeued' : 'undequeued',  # set
        'working'    : 'working',     # sorted set
        'delayed'    : 'delayed',     # sorted set
        'tasks'      : 'tasks',       # hash
        'task'       : 'task'         # prefix for hashes
    }
    '''
    Queue Redis key name mapping.

    On initialisation the values are prefixed with the queue name, and
    the new dictionary is rebound to the instance.

    .. list-table:: Redis key description

       * - ``pending``
         - a list containing enqueued task ids
       * - ``dequeueing``
         - a short-living task id list where :py:meth:`.dequeue`
           ``RPOPLPUSH``-es task ids from ``pending`` list
       * - ``undequeued``
         - a set where :py:meth:`.sweep` stored potentially (evaluated
           on the next sweep) stale, "undequeued", task ids
       * - ``working``
         - a sorted set with successfully dequeued task ids where the
           score is the Unix timestamp when the task becomes stale
           according to its timeout
       * - ``delayed``
         - a sorted set with delayed task ids where the score is the
           Unix timestamp when the task becomes due
       * - ``tasks``
         - a hash mapping a task id to its serialised representation
       * - ``task``
         - a string prefix, followed by task id, for hashes storing
           individual task stats

    '''

    _serialiser: TorrelqueTaskSerialiser
    '''
    Task data serialiser that converts task object into and from string
    representation.
    '''

    _redis: yaaredis.StrictRedis
    '''Redis client.'''

    _sweep_task: asyncio.Task
    '''Periodic sweep ``asyncio`` task.'''

    _keyspace_notification_enabled = False
    '''
    Flag indicates that Redis keyspace notification were found
    correctly configured, and further tests should be omitted.
    '''

    _scripts: dict
    '''Dictionary with Lua scripts read on initialisation.'''

    def __init__(
        self,
        redis: yaaredis.StrictRedis,
        *,
        queue: str = 'trq',
        serialiser=TorrelqueTaskSerialiser(lambda obj: json.dumps(obj).encode(), json.loads),
    ):
        if not isinstance(redis, yaaredis.StrictRedis):
            raise TorrelqueError('yaaredis.StrictRedis instance expected')

        self._redis = redis
        self._serialiser = serialiser
        self._scripts = {n: read_text(__package__, f'{n}.lua') for n in ('dequeue', 'sweep')}

        self.keys = {k: f'{queue}:{v}' for k, v in self.keys.items()}

    def _get_state_key(self, task_id):
        return '{}:{}'.format(self.keys['task'], task_id)

    async def _call_script(self, name: str, keys: Sequence, args: Sequence):
        script = self._scripts[name]
        digest = hashlib.sha1(script.encode()).hexdigest()
        try:
            result = await self._redis.evalsha(digest, len(keys), *(*keys, *args))
        except yaaredis.NoScriptError:
            result = await self._redis.eval(script, len(keys), *(*keys, *args))

        return result

    async def _enqueue(
        self,
        pipeline: StrictPipeline,
        task,
        task_timeout: Optional[float] = None,
        delay: Optional[float] = None,
    ) -> str:
        task_timeout = task_timeout or self.task_timeout
        task_id = uuid.uuid1().hex
        task_data = self._serialiser.dumps(task)
        task_state_key = self._get_state_key(task_id)

        if delay:
            await pipeline.zadd(self.keys['delayed'], time.time() + delay, task_id)
            await pipeline.hset(task_state_key, 'status', TorrelqueTaskStatus.DELAYED.value)
        else:
            await pipeline.lpush(self.keys['pending'], task_id)
            await pipeline.hset(task_state_key, 'status', TorrelqueTaskStatus.PENDING.value)

        await pipeline.hset(self.keys['tasks'], task_id, task_data)
        await pipeline.hset(task_state_key, 'enqueue_time', time.time())
        await pipeline.hset(task_state_key, 'timeout', task_timeout)

        return task_id

    async def enqueue(
        self,
        task,
        *,
        task_timeout: Optional[float] = None,
        delay: Optional[float] = None,
        pipeline: Optional[StrictPipeline] = None
    ) -> str:
        '''
        Put a task on the queue optionally providing its timeout and delay.

        :argument task:
            Arbitrary serialisable task payload.
        :argument task_timeout:
            Time since the task's processing start after which it is
            considered stale.
        :argument delay:
            Number of seconds to delay processing of the task, i.e.
            putting it into the "pending" list. Note that the sweep
            must be scheduled for the delayed tasks to return, and
            the delay only has effect after the sweep execution.
        :argument pipeline:
            External Redis pipeline that allows for bulk enqueue.
        :return:
            Task identifier.
        '''

        if pipeline is not None:
            task_id = await self._enqueue(pipeline, task, task_timeout, delay)
        else:
            async with await self._redis.pipeline(transaction=True) as pipeline:
                task_id = await self._enqueue(pipeline, task, task_timeout, delay)
                await pipeline.execute()

        return task_id

    async def _dequeue(self, timeout: int, max_tasks: int) -> List[TaskPair]:
        pending_key = self.keys['pending']
        dequeueing_key = self.keys['dequeueing']

        # Try to move max_tasks task ids to dequeueing without blocking
        task_ids: List[bytes] = []
        if max_tasks > 1:
            async with await self._redis.pipeline(transaction=True) as pipeline:
                for _ in range(max_tasks):
                    await pipeline.rpoplpush(pending_key, dequeueing_key)
                task_ids.extend(task_id for task_id in await pipeline.execute() if task_id)

        # If the above hasn't succeeded guarantee at least one task
        if not task_ids:
            task_id = await self._redis.brpoplpush(
                pending_key, dequeueing_key, timeout=timeout or 0
            )
            if not task_id:
                raise TorrelqueTimeoutError
            else:
                task_ids.append(task_id)

        keys = [self.keys[k] for k in ('dequeueing', 'working', 'tasks', 'task')]
        args = [time.time(), TorrelqueTaskStatus.WORKING.value] + task_ids
        pairs = await self._call_script('dequeue', keys, args)

        result = []
        for task_id, task_data in pairs:
            task_id = task_id.decode()
            task_data = self._serialiser.loads(task_data)
            if not task_data:
                logger.warning('Task:%s not found in dequeueing list', task_id)
                continue

            result.append((task_id, task_data))

        if not result:
            raise TorrelqueLookupError('Failed to dequeue pending task')

        return result

    async def dequeue(
        self, timeout: Optional[int] = None, *, max_tasks: int = 1
    ) -> Union[TaskPair, List[TaskPair]]:
        '''
        Get a task or a task list from the queue with optional timeout.

        :argument timeout:
            Time to wait until a task is available. Timeout applies
            only to fetching single task. Note that Redis only supports
            an integer timeout.
        :argument max_tasks:
           If greater than 1 the method will try to optimistically
           dequeue as many tasks. That means that only 1 task is
           guaranteed.
        :raises TorrelqueTimeoutError:
            If timeout was provided and there was no result within it.
        :raises TorrelqueLookupError:
            Indicates that the task id has become staling during the
            runtime of this method. This is not expected under normal
            circumstances. It can happen if this method is paused, say
            on a debugger breakpoint, for a duration of 2 sweeps.
        :return:
            Tuple of the task identifier and the deserialised task
            payload. If ``max_tasks`` is greater than 1, no matter if
            it dequeues more than 1 task, the return value is a list of
            said 2-tuples.
        '''

        assert max_tasks > 0

        task_pairs = await self._dequeue(timeout, max_tasks)
        return task_pairs if max_tasks > 1 else task_pairs[0]

    async def _requeue(
        self,
        pipeline: StrictPipeline,
        task_id: str,
        delay: Optional[float] = None,
        task_timeout: Optional[float] = None
    ) -> list:
        expected = []
        await pipeline.zrem(self.keys['working'], task_id)
        expected.append(1)

        task_state_key = self._get_state_key(task_id)
        if not delay:
            await pipeline.lpush(self.keys['pending'], task_id)
            await pipeline.hset(task_state_key, 'last_requeue_time', time.time())
            await pipeline.hincrby(task_state_key, 'requeue_count', 1)
            await pipeline.hset(task_state_key, 'status', TorrelqueTaskStatus.PENDING.value)
            expected.extend([..., ..., ..., 0])
        else:
            await pipeline.zadd(self.keys['delayed'], time.time() + delay, task_id)
            await pipeline.hset(task_state_key, 'status', TorrelqueTaskStatus.DELAYED.value)
            expected.extend([1, 0])

        if task_timeout:
            await pipeline.hset(task_state_key, 'timeout', task_timeout)
            expected.append(0)

        return expected

    async def requeue(
        self,
        task_id: str,
        delay: Optional[float] = None,
        *,
        task_timeout: Optional[float] = None,
        pipeline: Optional[StrictPipeline] = None,
    ):
        '''
        Return failed task into the queue with optional delay.

        :argument task_id:
            Task identifier.
        :argument delay:
            Number of seconds to delay putting the task into "pending"
            list. Note that the sweep must be scheduled in order for
            tasks from "delayed" to return to "pending" list.
        :argument task_timeout:
            Redefine task timeout, which is the time since the task's
            processing start after which it is considered stale.
        :argument pipeline:
            External Redis pipeline that allows for bulk requeue.
        '''

        if pipeline is not None:
            await self._requeue(pipeline, task_id, delay, task_timeout)
        else:
            async with await self._redis.pipeline(transaction=True) as pipeline:
                expected = await self._requeue(pipeline, task_id, delay, task_timeout)
                actual = await pipeline.execute()

            if not all(expc == actl or expc is ... for expc, actl in zip(expected, actual)):
                logger.warning('Inconsistent requeue of task:%s: %s', task_id, actual)

    async def _release(
        self,
        pipeline: StrictPipeline,
        task_id: str,
        result=None,
        result_ttl: Optional[int] = None,
        status: TorrelqueTaskStatus = TorrelqueTaskStatus.COMPLETED,
    ) -> list:
        if status is not None and not status.isfinal():
            raise TorrelqueError(f'Invalid status for released task: {status}')

        expected = []
        await pipeline.zrem(self.keys['working'], task_id)
        await pipeline.hdel(self.keys['tasks'], task_id)
        expected.extend([1, 1])

        task_state_key = self._get_state_key(task_id)
        if result is not None:
            await pipeline.hset(task_state_key, 'result', self._serialiser.dumps(result))
            await pipeline.hset(task_state_key, 'release_time', time.time())
            await pipeline.hset(task_state_key, 'status', status.value)
            expected.extend([1, 1, 0])

            result_ttl = result_ttl if result_ttl is not None else self.result_ttl
            await pipeline.expire(task_state_key, result_ttl)
            expected.append(1)
        else:
            await pipeline.delete(task_state_key)
            expected.append(1)

        return expected

    async def release(
        self,
        task_id: str,
        *,
        result=None,
        result_ttl: Optional[int] = None,
        status: TorrelqueTaskStatus = TorrelqueTaskStatus.COMPLETED,
        pipeline: Optional[StrictPipeline] = None,
    ):
        '''
        Remove finished task from the queue.

        Unless ``result`` is specified, all task information is removed
        from the queue immediately.

        Since there's no dead letter queue, tasks that have exceeded
        allowed number of retries should also be released, possibly
        with ``TorrelqueTaskStatus.REJECTED`` status if producer is
        interested in the status.

        :argument task_id:
            Task identifier.
        :argument result:
            Arbitrary serialisable task result. If ``result`` is
            ``None`` task state key is removed immediately on release.
        :argument result_ttl:
            Number of seconds to keep task state key after release.
            Override of default result TTL.
        :argument status:
            Task status to set on release. It only apples when result
            is not ``None``.
        :argument pipeline:
            External Redis pipeline that allows for bulk release.
        :raises TorrelqueError:
            If the status is not final.
        '''

        if pipeline is not None:
            await self._release(pipeline, task_id, result, result_ttl, status)
        else:
            async with await self._redis.pipeline(transaction=True) as pipeline:
                expected = await self._release(pipeline, task_id, result, result_ttl, status)
                actual = await pipeline.execute()

            if expected != actual:
                logger.warning('Inconsistent release of task:%s: %s', task_id, actual)

    async def _check_keyspace_notification_config(self):
        if not self._keyspace_notification_enabled:
            config = await self._redis.config_get('notify-keyspace-events')
            notify_config = set(config['notify-keyspace-events'])
            # See https://redis.io/topics/notifications#configuration
            if {'K', 'A'} - notify_config and {'K', 'g', 'h'} - notify_config:
                raise TorrelqueError('Redis notify-keyspace-events must include KA or Kgh')
            self._keyspace_notification_enabled = True

    async def _get_keyspace_notification_message(self, pubsub, timeout: float):
        try:
            message = await asyncio.wait_for(pubsub.listen(), timeout)
            # This is the effect of ignore_subscribe_messages
            if message is None:
                message = await self._get_keyspace_notification_message(pubsub, timeout)
        except asyncio.TimeoutError as ex:
            raise TorrelqueTimeoutError from ex
        else:
            return message

    async def watch(self, task_id: str, *, timeout: Optional[float] = None):
        '''
        Watch task status change until it's released from the queue.

        .. note::

           This method relies on ``notify-keyspace-events`` introduced
           in Redis 2.8. The configuration must have generic and hash
           commands enabled. That is, the configuration must include
           either ``KA`` or ``Kgh``.

        :argument task_id:
            Task identifier.
        :argument timeout:
            Timeout for watching.
        :raises TorrelqueError:
            If ``notify-keyspace-events`` is not configured properly.
        :raises TorrelqueTimeoutError:
            If ``watch`` has taken longer than ``timeout``.
        :raises TorrelqueLookupError:
            If the task state key is not found.
        :return:
            Asynchronous generator that yields task state dictionaries
            as returned by :py:meth:`.get_task_state`. Generator stops
            when the task is released. If the task is released without
            result, generator won't yield ``dict`` with final status.
        '''

        start = time.monotonic()

        await self._check_keyspace_notification_config()

        task_state = await self.get_task_state(task_id)
        yield task_state

        status = task_state.status
        if status.isfinal():
            return

        with contextlib.closing(self._redis.pubsub(ignore_subscribe_messages=True)) as pubsub:
            dbn = self._redis.connection_pool.connection_kwargs['db']
            await pubsub.subscribe('__keyspace@{}__:{}'.format(dbn, self._get_state_key(task_id)))

            iter_timeout = timeout
            while True:
                message = await self._get_keyspace_notification_message(pubsub, iter_timeout)
                if message['data'] == b'del':
                    return  # Released without result
                elif message['data'] == b'hset':
                    try:
                        task_state = await self.get_task_state(task_id)
                    except TorrelqueLookupError:
                        return  # Race condition with release

                    if task_state.status != status:
                        status = task_state.status
                        yield task_state
                        if status.isfinal():
                            return

                if timeout is not None:
                    iter_timeout = timeout - (time.monotonic() - start)

    async def sweep(self) -> Tuple[int, int, int]:
        '''
        Execute the task sweep.

        :return:
            3-tuple:
            - stale tasks from "working" set returned into "pending" list
            - due delayed tasks from "delayed" set returned into "pending" list
            - stale dequeueing task ids returned into "pending" list
        '''

        keys = [
            self.keys[k]
            for k in ('pending', 'dequeueing', 'undequeued', 'working', 'delayed', 'task')
        ]
        args = [time.time(), TorrelqueTaskStatus.PENDING.value]
        return tuple(await self._call_script('sweep', keys, args))

    async def _sweep_runner(self, interval: float):
        while True:
            start = time.monotonic()
            try:
                result = await self.sweep()
            except yaaredis.RedisError:
                logger.exception('Sweep has failed with Redis error, continuing')
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception('Sweep has failed with unexpected error, stopping')
                break
            else:
                logger.debug('Sweep has requeued: stale=%d, delayed=%d, undequeued=%d', *result)

            await asyncio.sleep(interval - (time.monotonic() - start))

    def schedule_sweep(self, interval: Optional[float] = None):
        '''
        Schedule the sweep in a background coroutine.

        :argument interval:
            Override of default sweep interval.
        '''

        interval = interval or self.sweep_interval
        self._sweep_task = asyncio.get_event_loop().create_task(self._sweep_runner(interval))

    def unschedule_sweep(self):
        '''Unschedule the sweep in a background coroutine.'''

        assert self._sweep_task
        self._sweep_task.cancel()

    async def get_queue_stats(self) -> TorrelqueQueueStats:
        '''Get queue counters.'''

        async with await self._redis.pipeline(transaction=True) as pipe:
            await pipe.hlen(self.keys['tasks'])
            await pipe.llen(self.keys['pending'])
            await pipe.zcard(self.keys['working'])
            await pipe.zcard(self.keys['delayed'])
            result = await pipe.execute()

        return TorrelqueQueueStats(*result)

    async def get_task_state(self, task_id: str) -> TorrelqueTaskState:
        '''
        Get task state.

        :argument task_id:
            Task identifier.
        :raises TorrelqueLookupError:
            If the task state key is not found.
        '''

        result = await self._redis.hgetall(self._get_state_key(task_id))
        if not result:
            raise TorrelqueLookupError

        return TorrelqueTaskState(
            status             = TorrelqueTaskStatus(int(result[b'status'])),
            timeout            = float(result[b'timeout']),
            enqueue_time       = float(result[b'enqueue_time']),
            last_dequeue_time  = float(result.get(b'last_dequeue_time', 0)) or None,
            dequeue_count      = int(result.get(b'dequeue_count', 0)),
            last_requeue_time  = float(result.get(b'last_requeue_time', 0)) or None,
            requeue_count      = int(result.get(b'requeue_count', 0)),
            release_time       = float(result.get(b'release_time', 0)) or None,
            result             = (
                self._serialiser.loads(result[b'result'])
                if result.get(b'result') is not None else None
            )
        )
