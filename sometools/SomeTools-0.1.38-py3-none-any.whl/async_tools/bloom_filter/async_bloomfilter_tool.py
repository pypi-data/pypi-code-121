# 布隆过滤器,基于redis from：https://blog.csdn.net/bone_ace/article/details/53107018

from hashlib import md5
from sometools.async_tools.base import Base

class SimpleBloomFilterHash:
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class AioBloomFilterMixIn(Base):
    def __init__(self, *args, block_num=2, key='bloomfilter', **kwargs):
        # super(AioGeneralBloomFilter, self).__init__(*args, **kwargs)
        self.bloom_filter_timeout = kwargs.get('bloom_filter_timeout') or 7200  # 布隆过滤key过期时间
        self.bit_size = 1 << 31  # Redis的String类型最大容量为512M，现使用256M
        self.bloom_filter_seeds = [5, 7, 11, 13, 31, 37, 61]
        self.bloom_filter_key = key
        self.bloom_filter_block_num = block_num
        self.bloom_filter_hashfunc = []
        for seed in self.bloom_filter_seeds:
            self.bloom_filter_hashfunc.append(SimpleBloomFilterHash(self.bit_size, seed))
        super(AioBloomFilterMixIn, self).__init__(*args, **kwargs)

    async def aio_is_bloom_filter_contains(self, str_input:str)->int:
        try:
            if self.aio_redis_conn:
                if not str_input:
                    return False
                m5 = md5()
                str_input = str_input.encode('utf-8')
                m5.update(str_input)
                str_input = m5.hexdigest()
                ret = True
                name = self.bloom_filter_key + str(int(str_input[0:2], 16) % self.bloom_filter_block_num)
                for f in self.bloom_filter_hashfunc:
                    loc = f.hash(str_input)
                    ret = ret & await self.aio_redis_conn.getbit(name, loc)
                return ret
            else:
                raise Exception(f'需要事先建立redis链接（self.aio_redis_conn）')
        except Exception as e:
            print(e)

    async def aio_bloom_filter_insert(self, str_input:str, bloom_filter_timeout=None)->int:
        if self.aio_redis_conn:
            if bloom_filter_timeout:
                time_out_num = bloom_filter_timeout
            else:
                time_out_num = self.bloom_filter_timeout
            m5 = md5()
            if not str_input:
                return False
            str_input = str_input.encode('utf-8')
            m5.update(str_input)
            str_input = m5.hexdigest()
            name = self.bloom_filter_key + str(int(str_input[0:2], 16) % self.bloom_filter_block_num)
            for f in self.bloom_filter_hashfunc:
                loc = f.hash(str_input)
                if await self.aio_redis_conn.exists(name):  # 1 存在  0 不存在
                    await self.aio_redis_conn.setbit(name, loc, 1)
                else:
                    await self.aio_redis_conn.setbit(name, loc, 1)
                    await self.aio_redis_conn.expire(name, time_out_num)
            if await self.aio_redis_conn.ttl(name) == -2:  # key 不存在
                pass
            if await self.aio_redis_conn.ttl(name) == -1:  # 无过期时间
                await self.aio_redis_conn.delete(name)
            return 1
            # if await self.aio_redis_conn.ttl(name) < 300:  # 剩下五分钟过期直接删除key
            #     await self.aio_redis_conn.delete(name)
        else:
            raise Exception(f'需要事先建立redis链接（self.aio_redis_conn）')