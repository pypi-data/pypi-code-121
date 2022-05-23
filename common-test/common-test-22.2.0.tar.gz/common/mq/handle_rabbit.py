import json
import pymssql
import sysconfig
import yaml
import os
import pika
class YamlHandler:
    def __init__(self, file):
        self.file = file

    def read_yaml(self, encoding='utf-8'):
        """读取yaml数据"""
        with open(self.file, encoding=encoding) as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)

    def write_yaml(self, data, encoding='utf-8'):
        """向yaml文件写入数据"""
        with open(self.file, encoding=encoding, mode='w') as f:
            return yaml.dump(data, stream=f, allow_unicode=True)


if __name__ == '__main__':
    # 读取config.yaml配置文件数据
    read_data = YamlHandler('../config/config.yaml').read_yaml()
    # 将data数据写入config1.yaml配置文件
    # write_data = YamlHandler('../config/config1.yaml').write_yaml(data)
    print(read_data)


username = read_data['shopping']['test']['test1']['host']   #指定远程rabbitmq的用户名密码
pwd = read_data['shopping']['test']['test1']["port"]
print(username,pwd)



username = 'xxxxxxxx'   #指定远程rabbitmq的用户名密码
pwd = '111111'
user_pwd = pika.PlainCredentials(username, pwd)
s_conn = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1', credentials=user_pwd))#创建连接
chan = s_conn.channel()  #在连接上创建一个频道

chan.queue_declare(queue='hello') #声明一个队列，生产者和消费者都要声明一个相同的队列，用来防止万一某一方挂了，另一方能正常运行
chan.basic_publish(exchange='',  #交换机
                   routing_key='hello',#路由键，写明将消息发往哪个队列，本例是将消息发往队列hello
                   body='hello world')#生产者要发送的消息
print("[生产者] send 'hello world")

s_conn.close()#当生产者发送完消息后，可选择关闭连接


username = 'xxxxxxxx'#指定远程rabbitmq的用户名密码
pwd = '111111'
user_pwd = pika.PlainCredentials(username, pwd)
s_conn = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.240', credentials=user_pwd))#创建连接
chan = s_conn.channel()#在连接上创建一个频道
chan.queue_declare(queue='hello')#声明一个队列，生产者和消费者都要声明一个相同的队列，用来防止万一某一方挂了，另一方能正常运行

def callback(ch,method,properties,body): #定义一个回调函数，用来接收生产者发送的消息
        print("[消费者] recv %s" % body)

chan.basic_consume(callback,  #调用回调函数，从队列里取消息
                                     queue='hello',#指定取消息的队列名
                                     no_ack=True) #取完一条消息后，不给生产者发送确认消息，默认是False的，即  默认给rabbitmq发送一个收到消息的确认，一般默认即可print('[消费者] waiting for msg .')
chan.start_consuming()#开始循环取消息
