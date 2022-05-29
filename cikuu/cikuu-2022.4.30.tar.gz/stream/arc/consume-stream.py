
from rabbitmq_client import RMQConsumer, ConsumeParams, QueueParams
#from some_other_module import handle_msg

def on_message(msg, ack=None):
    print ("got:", msg, flush=True)

consumer = RMQConsumer()
consumer.start()
consumer.consume(ConsumeParams(on_message),
                 queue_params=QueueParams("xessay_log"))