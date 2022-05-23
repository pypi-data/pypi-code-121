#encoding=utf-8
import pika
import logging,traceback

class RabbitMQ:
    def __init__(self,mq_settings):
        self.settings=mq_settings
        self.conn=None

    def __connect(self):
        if self.conn is None:
            credentials = pika.PlainCredentials(self.settings.account, self.settings.password)
            self.conn=pika.BlockingConnection(pika.ConnectionParameters(self.settings.host,self.settings.port,'/',credentials))

    def send_msg(self,exchange,routing_key,message):
        try:
            self.__connect()
            channel = self.conn.channel()
            #channel.exchange_declare(exchange=exchange, durable=True, exchange_type='fanout')
            #channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message,  mandatory=True,properties=pika.BasicProperties(delivery_mode = 2))

            channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
            self.conn.close()
            self.conn = None
            return 200
        except Exception as e:
            traceback.print_exc()
            logging.warning(e,'while sending message to exchange: {} with key: {}'.format(exchange,routing_key))
            try:
                self.conn.close()
            finally:
                self.conn=None
                return 500


    """
credentials = pika.PlainCredentials('admin', '1qaz2wsx')
connection = pika.BlockingConnection(pika.ConnectionParameters('10.5.16.213',5672,'/',credentials))

exchange='exchange.iot'
routing=sys.argv[3]#'device.5b865291b9d8210005d679cc.shadow.update.resp'
vid=sys.argv[1]
count=sys.argv[2]
channel = connection.channel()
#channel.exchange_declare(exchange=exchange)
#channel.queue_declare('smartfleet.condition')

#message = '{"timestamp": "2016-10-1'+str(count)+'T22:00:00","content": "PLC1温度高过60摄氏度了","type": "E123","group": "temperature", "level": 2,"state": "on"}'

message='[{"fields": {"altitude": 0.0,"latitude": 40.067412,"speed": 0.0,"longitude": 116.319018},"metric": "location_data","tags": {'\
            +'"mid": "5b911037ea40310005350e09","category": "gps","did": "5b865291b9d8210005d679cc"},"ts": "2018-09-10T17:09:59+0800"}]'
#message = '{"trans_id":'+str(count)+',"address":"ç´¢é©¬é","createDate": ' +str(int(time.time())) +',"p":{"coordinates":{23:25},"type":"POINT"},"status":{"cd":"cidg"},"vid":"'+vid+'"}'
channel.basic_publish(exchange=exchange,routing_key=routing,body=message)
print(" [x] ->"+message)
connection.close()

    """