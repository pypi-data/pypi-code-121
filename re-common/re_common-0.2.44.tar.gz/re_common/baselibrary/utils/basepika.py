import pika


# https://blog.csdn.net/songfreeman/article/details/50943603
class BasePika(object):

    def __init__(self, username=None, password=None, mqhost=None, virtual_host=None):
        self.username = username
        self.password = password
        self.conn = None
        self.host = mqhost
        self.virtual_host = virtual_host
        self.auto_ack = True

    def set_default(self):
        self.host = "192.168.31.79"
        self.virtual_host = "vhost_NetDataGather"
        self.username = "vip"
        self.password = "piv$*123"

    def connect_str(self,amqp_str):
        parameters = pika.URLParameters(amqp_str)
        self.conn = pika.BlockingConnection(parameters)

    def connect(self):
        """
        设置用户名 密码 进行连接
        :return:
        """
        credentials = pika.PlainCredentials(self.username, self.password)
        # parameters = pika.URLParameters('amqp://guest:guest@rabbit-server1:5672/%2F')
        # 可以通过将 heartbeat 设为 0，关闭 rabbitmq 的心跳检测
        parameters = pika.ConnectionParameters(host=self.host,
                                               virtual_host=self.virtual_host,
                                               credentials=credentials,
                                               heartbeat=0)
        self.conn = pika.BlockingConnection(parameters)

    def close(self):
        # 关闭消息队列
        self.conn.close()

    def create_channel(self):
        self.channel = self.conn.channel()

    def __del__(self):
        self.channel.close()
        self.conn.close()

    def random_queue_declare(self):
        """
        这样, result.method.queue 包含一个随机的队列名, 比如：看起来像 amq.gen-JzTY20BRgKO-HjmUJj0wLg.
        其次：
        一旦我们断开consumer连接，这个队列名将自动删除。这里有一个标识设置：
        :return:
        """
        return self.channel.queue_declare("", exclusive=True)

    def queue_declare(self, queue="hello", durable=False):
        """
        创建目的地队列hello 取消息时也可以调用
        取消息和发送消息都调用 保证队列存在，也保证了不管服务端还是客户端先启动都有队列
        durable True 为持久化
        :return:
        """
        return self.channel.queue_declare(queue=queue, durable=durable)

    def get_queue_size(self, queue="hello"):
        """
        获取某个队列的长度
        :param queue:
        :return:
        """
        queue = self.queue_declare(queue=queue, durable=True)
        return queue.method.message_count

    def get_properties(self):
        """
        与 queue_declare里的 durable = True 配合使用，
        设置给 easy_send_msg的properties
        :return:
        """
        return pika.BasicProperties(
            delivery_mode=2,  # 设置消息为持久化的
        )

    def easy_send_msg(self, exchange="", routing_key="hello", body="hello world", properties=None):
        """
        空字符串标识默认的或者匿名的exchange,如果存在routing_key, 消息路由到routing_key指定的队列中。
        routing_key 标识发送到哪个队列,就是服务器上的队列名
        body 发送的消息

        basic_publish 如果 exchange 不是"" 但没有绑定队列 消息会消失
        :return:
        """
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=body,
                                   properties=properties)

    def basic_ack(self, ch, method):
        """
        callback的消息确认
        :param ch:
        :param method:
        :return:
        """
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def callback(self, ch, method, properties, body):
        """
        从队列接收消息要更复杂一些，它需要为队列订阅一个 callback 函数来进行接收。
        当我们接收一个消息后，这个 callback 函数将会被 pika函数库自动调用，
        在我们的这个实例里面这个函数将用来打印接收的消息内容到屏幕
        :param method:
        :param properties:
        :param body:
        :return:
        """
        print(type(body))
        print(" [x] Received %r" % body)
        if self.auto_ack is False:
            self.basic_ack(ch, method)

    def set_get_msg_callback(self, routing_key="hello", callback=None, auto_ack=True):
        """
        设置取消息的callback
        no_ack 如果设置为True，将使用自动确认模式
        no_ack 如果设置为False，在callback中确认
        :return:
        """
        self.auto_ack = auto_ack
        if callback is None:
            callback = self.callback
        self.channel.basic_consume(routing_key,
                                   callback,
                                   auto_ack=auto_ack)

    def start_get_msg(self):
        """
        开始取消息,会循环不停的取消息
        :return:
        """
        self.channel.start_consuming()

    def basic_qos(self, prefetch_count=1):
        """
        可以提前发送几个消息来，当auto_ack=True时无效
        prefetch_count==1 消息未处理完前不要发送信息的消息
        :return:
        """
        self.channel.basic_qos(prefetch_count=prefetch_count)

    def exchange_declare(self, exchangename="logs", type="fanout"):
        """
        fanout exchange非常简单，你从这个名字中就能猜出来，它将从Producer方收到的消息广播给所有他知道的receiver方。而这正是我们的logger记录所需要的消息。
        交换的类型
        直接交换（direct exchange）的路由算法很简单 --  消息发送到绑定键值(binding key) 刚好完全符合路由键值( routing key) 的消息队列中。

        消息发送到一个 topic交换不能是一个任意的 routing_key -- 它必须是一个用小数点 分割的单词列表。 这个字符可以是任何单词，但是通常是指定一些连接特定消息的功能。一些有效的路由键(routing key）比如：“stock.usd.nyse",
        topic 是 直接交换的升级版

        headers Exchange ：headers交换器允许你匹配AMQP消息的header而非路由键。除此之外，headers交换器和direct交换器完全一致，但性能会差很多。因此它并不太实用，而且几乎再也用不到了。
        exchangename接下来会与队列绑定
         direct  ,  topic ,  headers  和 fanout
        :return:
        """
        return self.channel.exchange_declare(exchange=exchangename,
                                             exchange_type=type)

    def queue_bind(self, exchange="logs", queue="", routing_key=""):
        """
        queue 临时队列获取 self.random_queue_declare().method.queue
        :param exchange:
        :param queue:
        :return:
        """
        self.channel.queue_bind(exchange=exchange,
                                queue=queue,
                                routing_key=routing_key)
