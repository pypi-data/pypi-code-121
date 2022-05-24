from re_common.baselibrary.utils.myredisclient import MyRedis

myredis = MyRedis("./config.ini")
myredis.set_redis_from_config(sesc="redis_test")
myredis.conn_redis()
myredis.get_pipeline()
# myredis.mset({"k1": "v1", "k2": "v2"})
a = myredis.hset("hash1", "k1", "v1")

print(a)
