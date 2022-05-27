'''
项目介绍
    Lsdict 是一款可设置 key 的有效期的字典。

已实现的功能
    ● 通过 life 指定寿命
    ● 通过 endtime 指定失效时间
    ● 索引取值 (key 不存在时会报错)
    ● get 取值 (key 不存在时返回指定值)
    ● setdefault 取值 (key 不存在时自动添加指定值)
    ● pop 取值 (删除指定的 key, 并返回对应的 value)
    ● 遍历 items (同时遍历 keys 和 values)
    ● 遍历 keys
    ● 遍历 values
    ● 统计 key 的数量
    ● 延长 key 的寿命
    ● 重置 key 的寿命
'''

import asyncio
from time import time as nowstamp
from .toolkit.data_structures import undefined
from .pk_factory import pk1 as newpk
from .toolkit.data_structures import ParamError


class lsdict():

    def __init__(self, clear_interval=100):
        self._ks = {}
        self._vs = {}
        self.clear_interval = clear_interval  # 自动清理间隔, 单位: 秒
        if clear_interval:
            asyncio.create_task(self._auto_clear())
    
    async def _auto_clear(self):
        while self.clear_interval:
            await asyncio.sleep(max(1, self.clear_interval))
            PkTup = list(self._vs.items())
            await asyncio.sleep(1)
            pks = set(self._ks.values())
            await asyncio.sleep(1)
            for pk, tup in PkTup:
                await asyncio.sleep(1)
                if pk not in pks or tup[0] <= nowstamp():
                    await asyncio.sleep(1)
                    self._vs.pop(pk, 0)
    
    def add(self, key, value, life=undefined, endtime=undefined):
        '''
        life: 存活时长, 该值会自动转换成 endtime
        endtime: 失效时间
        '''
        {key: 0}  # 校验key的合法性
        if life is not undefined and endtime is not undefined:
            raise ParamError('life 与 endtime 最多只能传1个')
        elif life is not undefined:
            endtime = nowstamp() + life
        elif endtime is undefined:
            endtime = float('inf')
        opk = self._ks.get(key)
        if endtime > nowstamp():
            pk = newpk()
            self._vs[pk] = (endtime, value)  # 使用元祖结构, 不允许修改
            self._ks[key] = pk
        if opk:
            self._vs.pop(opk, 0)
        return True

    def __getitem__(self, key):
        pk = self._ks.get(key)
        if pk:
            tup = self._vs.get(pk)
            if tup:
                if tup[0] >= nowstamp():
                    return tup[1]
                self._vs.pop(pk, 0)
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except:
            return default

    def setdefault(self, key, default=None, life=undefined, endtime=undefined):
        pk = self._ks.get(key)
        if pk:
            tup = self._vs.get(pk)
            if tup:
                if tup[0] >= nowstamp():
                    return tup[1]
        self.add(key, default, life, endtime)
        return default  # 即使值被其它线程重置了, 返回值也必须是default, 这样才符合一般预期

    def pop(self, key, default=undefined):
        pk = self._ks.pop(key, 0)
        if pk:
            tup = self._vs.pop(pk, 0)
            if tup:
                if tup[0] >= nowstamp():
                    return tup[1]
        if default is undefined:
            raise KeyError(key)
        else:
            return default

    def items(self):
        for key in list(self._ks):
            try:
                yield key, self[key]
            except:
                pass

    def keys(self):
        for key, value in self.items():
            yield key

    def values(self):
        for key, value in self.items():
            yield value

    def __len__(self): return len(list(self.items()))

    def setlife(self, key, default=undefined, addlife=undefined, life=undefined, endtime=undefined):
        if len([x for x in (addlife, life, endtime) if x is undefined]) != 2:
            raise ParamError("[addlife, life, endtime] 必须传递1个, 且只能传递1个")
        state = False
        pk = self._ks.get(key)
        if pk:
            tup = self._vs.get(pk)
            if tup:
                oetime, value = tup
                if oetime >= nowstamp():
                    state = True
        if not state:
            if default is undefined:
                self._vs.pop(pk, 0)
                raise KeyError(key)
            value = default
            oetime = nowstamp()
        if addlife is not undefined:
            oetime += addlife
        elif life is not undefined:
            oetime = nowstamp() + life
        else:
            oetime = endtime
        self.add(key, value, endtime=oetime)
        return value
