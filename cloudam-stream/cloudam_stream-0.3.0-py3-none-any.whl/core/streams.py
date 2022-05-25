import time
import os


class RedisProducer(object):
    def __init__(self, redis_client, max_memory_threshold=0.8, min_memory_threshold=0.5, flow_depth=1,
                 actor_level=1):
        if os.getenv("max_memory_threshold") is not None:
            max_memory_threshold = os.getenv("max_memory_threshold")
        if os.getenv("min_memory_threshold") is not None:
            min_memory_threshold = os.getenv("min_memory_threshold")
        # 内存阈值，限制producer发送
        self.max_memory_threshold = max_memory_threshold
        self.min_memory_threshold = min_memory_threshold
        self.flow_depth = flow_depth
        self.actor_level = actor_level
        self.redis_client = redis_client

    def check_memory(self, memory_threshold, message):
        memory_info = self.redis_client.info(section="memory")
        used_memory = memory_info['used_memory_rss']
        expect_used_memory = used_memory + len(message)
        #TODO
        total_memory = memory_info['total_system_memory']
        # total_memory = memory_info['maxmemory']
        percent = round((expect_used_memory / total_memory), 4)
        return percent > memory_threshold

    def capped(self, memory_threshold, message):
        if self.check_memory(memory_threshold, message):
            print("memory exceed:" + memory_threshold + "%, wait 5 seconds")
            time.sleep(5)
            self.capped(self.redis_client)
        # print("memory less than 75%, continue")

    def calculate_memory_threshold(self, depth, level):
        if depth == 1:
            return self.max_memory_threshold
        elif depth <= 4:
            return self.max_memory_threshold - 0.1 * (level - 1)
        else:
            return self.max_memory_threshold - (self.max_memory_threshold - self.min_memory_threshold) / (depth - 1) * (
                    level - 1)

    # 生产消息
    def produce(self, stream_name, message):
        memory_threshold = self.calculate_memory_threshold(self.flow_depth, self.actor_level)
        # 判断redis内存
        self.capped(memory_threshold, message)
        print("produce message")
        print(message)
        self.redis_client.xadd(name=stream_name, fields={"": message})


class RedisConsumer(object):
    def __init__(self, redis_client, group_name, stream_names):
        self.redis_client = redis_client
        self.group_name = group_name
        streams = dict()
        for stream_name in stream_names:
            streams[stream_name] = '>'
        self.streams = streams

    # 消费消息
    def consume(self, consumer_id, count):
        total_pending_key = self.group_name + "_pending"
        msgs = self.redis_client.xreadgroup(self.group_name, consumer_id, self.streams, count=count, noack=True,
                                            block=3000)
        msg_num = len(msgs)
        if msg_num > 0:
            # 统计pending中的消息数量
            self.redis_client.incr(total_pending_key, msg_num)
        return msgs

    # 确认消费
    def ack(self, stream_name, msg_id):
        total_ack_key = self.group_name + "_ack"
        total_pending_key = self.group_name + "_pending"
        self.redis_client.xack(stream_name, self.group_name, msg_id)
        self.redis_client.xdel(stream_name, msg_id)
        self.redis_client.incr(total_ack_key, 1)
        self.redis_client.decr(total_pending_key, 1)