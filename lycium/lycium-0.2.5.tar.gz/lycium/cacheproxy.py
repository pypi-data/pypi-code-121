#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import redis
import logging
import datetime
import tornado.gen
import aredis

from .supports import singleton
from .modelutils import model_columns, format_mongo_value, DEFAULT_SKIP_FIELDS
from .dbproxy import DbProxy

LOG = logging.getLogger('components.cacheproxy')

@singleton
class CacheProxy(object):
    """
    Cacher agent component
    """

    def __init__(self):
        self.dbproxy = DbProxy()
        self.async_redis_conn = None
    
    def configure(self, redis_conf: dict) -> bool:
        self.async_redis_conn = aredis.StrictRedis(host=redis_conf['host'], port=redis_conf['port'], 
            db=redis_conf['db'], password=redis_conf['password'], retry_on_timeout=True)
        return True

    def prepare(self):
        pass

    @tornado.gen.coroutine
    def getObject(self, key, keys):
        self.prepare()
        res = yield self.async_redis_conn.hmget(key, keys)
        if not res:
            return False
        result = {}
        isAllNone = True
        i = 0
        for k in keys:
            v = res[i].decode() if isinstance(res[i], bytes) else res[i]
            result[k] = v
            i += 1
            if isAllNone and v is not None:
                isAllNone = False
        if isAllNone:
            result = False
        return result
    
    @tornado.gen.coroutine
    def getObjects(self, key, keys):
        self.prepare()
        results = []
        idxes = yield self.getSetsValues(key)
        for idx in idxes:
            row = yield self.getObject(key+':'+idx, keys)
            if row is not False:
                results.append(row)
        return results

    @tornado.gen.coroutine
    def saveObject(self, key, mapping, expire=None):
        if not mapping:
            return False
        for k,v in mapping.items():
            if v is None:
                mapping[k] = ''
        yield self.async_redis_conn.hmset(key, mapping)
        if expire is not None:
            yield self.async_redis_conn.expire(key, expire)
        return True

    @tornado.gen.coroutine
    def getSetsValues(self, key):
        results = []
        vals = yield self.async_redis_conn.smembers(key)
        if not vals:
            return results
        for val in vals:
            val = val.decode() if isinstance(val, bytes) else str(val)
            results.append(val)
        return results

    @tornado.gen.coroutine
    def addSetsValue(self, key, value):
        yield self.async_redis_conn.sadd(key, value)
        
    @tornado.gen.coroutine
    def getSetsValuesExtend(self, key, keys):
        vals = yield self.getSetsValues(key)
        return self.parseImplodedValues(vals, keys)

    def parseImplodedValues(self, rows, keys):
        results = []
        if not rows:
            return results
        l = len(keys)
        for val in rows:
            one = {k:'' for k in keys}
            i = 0
            eles = val.split('-')
            l2 = len(eles)
            for i in range(l):
                if i < l2:
                    one[keys[i]] = eles[i]
            # in case that if last field is text that contains '-'
            if l > 0 and l2 > l:
                for j in range(l2-l):
                    one[keys[l-1]] += '-' + eles[l+j]
            results.append(one)
        return results
        
    @tornado.gen.coroutine
    def getSortedSetsValues(self, key):
        results = []
        vals = yield self.zrange(key, 0, -1, withscores=True)
        if not vals:
            return results
        for ele in vals:
            val = ele[0]
            val = val.decode() if isinstance(val, bytes) else val
            results.append(val)
        return results
    
    @tornado.gen.coroutine
    def getSortedSetsValuesExtend(self, key, keys):
        vals = yield self.getSortedSetsValues(key)
        return self.parseImplodedValues(vals, keys)

    @tornado.gen.coroutine
    def getCacheValue(self, key):
        val = yield self.async_redis_conn.get(key)
        return val

    @tornado.gen.coroutine
    def scanHashKeys(self, hashKey, keyMatch, count=1000, cursor=0):
        res = yield self.async_redis_conn.hscan(hashKey, cursor, match=keyMatch, count=count)
        keys = []
        nextCursor = 0
        if res:
            nextCursor = res[0]
            for k in res[1]:
                keys.append(k.decode() if isinstance(k, bytes) else str(k))
        return keys, nextCursor
    
    @tornado.gen.coroutine
    def findHashKeys(self, hashKey, keyMatch, matchKeys = {}):
        keys = []
        if not hashKey or not keyMatch or not matchKeys:
            return keys
        nextCursor = -1
        while nextCursor != 0:
            if nextCursor == -1:
                nextCursor = 0
            scanedKeys, nextCursor = yield self.scanHashKeys(hashKey, keyMatch, cursor=nextCursor)
            for k in scanedKeys:
                if k in matchKeys:
                    keys.append(k)
        return keys

    @tornado.gen.coroutine
    def getAllHashKeys(self, hashKeyPrefix, matchKeys = {}):
        res = yield self.async_redis_conn.hgetall(hashKeyPrefix)
        result = []
        for row in res:
            a = row
        return result
        
    @tornado.gen.coroutine
    def clearByKeyPrefix(self, keyPrefix):
        keys = yield self.async_redis_conn.keys(keyPrefix+'*')
        del_keys = [[]]
        i = 0
        for k in keys:
            del_keys[i].append(k.decode() if isinstance(k, bytes) else str(k))
            if len(del_keys[i]) > 50:
                i += 1
                del_keys.append([])

            if i > 10:
                yield [self.async_redis_conn.delete(*dkeys) for dkeys in del_keys]
                del_keys = [[]]
                i = 0
        
        if del_keys[0]:
            yield [self.async_redis_conn.delete(*dkeys) for dkeys in del_keys]

    @tornado.gen.coroutine
    def incr(self, key, expire = None):
        yield self.async_redis_conn.incr(key)
        if expire:
            yield self.async_redis_conn.expire(key, expire)

    @tornado.gen.coroutine
    def set(self, key, value, expire = None, px=None, nx=False, xx=False):
        """
        Set the value at key ``name`` to ``value``

        ``expire`` sets an expire flag on key ``name`` for ``expire`` seconds.

        ``px`` sets an expire flag on key ``name`` for ``px`` milliseconds.

        ``nx`` if set to True, set the value at key ``name`` to ``value`` only
            if it does not exist.

        ``xx`` if set to True, set the value at key ``name`` to ``value`` only
            if it already exists.
        """
        yield self.async_redis_conn.set(key, value, ex=expire, px=px, nx=nx, xx=xx)

    @tornado.gen.coroutine
    def get(self, key):
        val = yield self.async_redis_conn.get(key)
        return val

    @tornado.gen.coroutine
    def delete(self, key):
        val = yield self.async_redis_conn.delete(key)
        return val

    @tornado.gen.coroutine
    def zrange(self, name, start, end, desc=False, withscores=False,
               score_cast_func=float):
        """
        Return a range of values from sorted set ``name`` between
        ``start`` and ``end`` sorted in ascending order.

        ``start`` and ``end`` can be negative, indicating the end of the range.

        ``desc`` a boolean indicating whether to sort the results descendingly

        ``withscores`` indicates to return the scores along with the values.
        The return type is a list of (value, score) pairs

        ``score_cast_func`` a callable used to cast the score return value
        """
        val = yield self.async_redis_conn.zrange(name, start, end, desc=desc, withscores=withscores, score_cast_func=score_cast_func)
        return val

    @tornado.gen.coroutine
    def isExistsInSets(self, key, value):
        val = yield self.async_redis_conn.sismember(key, value)
        return val

    @tornado.gen.coroutine
    def loadMongoDataToCache(self, model, keyPrefix, pk, filters=None, excachecb=None, clearcache=True):
        checkUniques = {}
        @tornado.gen.coroutine
        def _load_cache_pk(item):
            cache_key = keyPrefix + self._getIndexKeyValue(item, pk)
            if cache_key in checkUniques:
                LOG.warning('loadToCache by key:%s that already exists.', cache_key)
            checkUniques[cache_key] = 1
            yield self.saveObject(cache_key, item)
            if callable(excachecb):
                yield excachecb(item, self.async_redis_conn)

        if clearcache:
            yield self.clearByKeyPrefix(keyPrefix)
        yield self._loadDataFromMongoDb(model, _load_cache_pk, filters=filters)

    @tornado.gen.coroutine
    def loadMongoDataToCacheIndexedToMany(self, model, keyPrefix, indexKey, pk, filters=None, orderby=None, clearcache=True):
        @tornado.gen.coroutine
        def _load_cache_index(item):
            yield self.addToCacheIndexedToMany(item, keyPrefix, indexKey, pk)
        if clearcache:
            yield self.clearByKeyPrefix(keyPrefix)
        yield self._loadDataFromMongoDb(model, _load_cache_index, filters=filters, orderby=orderby)

    @tornado.gen.coroutine
    def addToCacheIndexedToMany(self, item, keyPrefix, indexKey, pk):
        if not isinstance(item, dict):
            item2 = item
            item = {}
            columns,_ = model_columns(item2)
            for k in columns:
                if k not in DEFAULT_SKIP_FIELDS:
                    item[k] = getattr(item2, k)
        pkValue = self._getIndexKeyValue(item, pk)
        idxValue = self._getIndexKeyValue(item, indexKey)
        cache_key = keyPrefix + idxValue
        yield self.async_redis_conn.sadd(cache_key, pkValue)
        cache_key += ':' + pkValue
        yield self.saveObject(cache_key, item)

    @tornado.gen.coroutine
    def delFromCacheIndexedToMany(self, item, keyPrefix, indexKey, pk):
        pkValue = self._getIndexKeyValue(item, pk)
        idxValue = self._getIndexKeyValue(item, indexKey)
        cache_key = keyPrefix + idxValue
        yield self.async_redis_conn.srem(cache_key, pkValue)
        cache_key += ':' + pkValue
        yield self.async_redis_conn.delete(cache_key)

    def _getIndexKeyValue(self, item, indexKey):
        idxValue = ''
        if isinstance(indexKey, list):
            vals = []
            for k in indexKey:
                if isinstance(item, dict):
                    vals.append(str(item[k]) if item[k] is not None else '')
                else:
                    vals.append(str(getattr(item, k, '')))
            idxValue = ':'.join(vals)
        else:
            if isinstance(item, dict):
                idxValue = str(item[indexKey] if item[indexKey] is not None else '')
            else:
                idxValue = str(getattr(item, indexKey, ''))
        return idxValue

    @tornado.gen.coroutine
    def _loadDataFromMongoDb(self, model, cb, filters=None, orderby=None):
        limit = 5000
        offset = 0
        nrows = limit
        modelName = str(model.__name__)
        LOG.info("loading %s from db begining", modelName)
        qfilters = []
        kwfilters = {}
        curId = None
        if isinstance(filters, tuple):
            for f in filters:
                if isinstance(f, dict):
                    for k,v in f.items():
                        kwfilters[k] = v
                elif isinstance(f, list):
                    for v in f:
                        qfilters.append(v)
        elif isinstance(filters, dict):
            kwfilters = filters
        elif isinstance(filters, list):
            qfilters = filters
        while nrows >= limit:
            if curId:
                kwfilters['id__gt'] = curId
            rows = yield self.dbproxy.query_all_mongo(model, (qfilters, kwfilters), limit)
            nrows = 0
            for row in rows:
                nrows += 1
                curId = row.get('id')
                item = {}
                for k in row:
                    if k in DEFAULT_SKIP_FIELDS:
                        continue
                    item[k] = format_mongo_value(row.get(k))
                if tornado.gen.is_coroutine_function(cb):
                    yield cb(item)
                else:
                    cb(item)
            offset += nrows
            LOG.info("loading %s from db offset:%d rows:%d", modelName, offset, nrows)
        
        LOG.info("loading %s from db finished", modelName)
