import pika, json

class Amqp_Collector(object):
    # Init an amqp client handling the connection to amqp servier
    def __init__(self, configuration:dict, host_object:object=None):
        self.host_object = host_object  
        self.exchange_name = configuration["exchange_name"]
        self.exchange_type = configuration["exchange_type"]
        self.in_routing_key = configuration["in_routing_key"]

        # Connect to RabbitMQ host
        self.in_connection = pika.BlockingConnection(pika.ConnectionParameters(host=configuration["end_point"]))
        
        # Create a channel
        self.in_channel = self.in_connection.channel()
        
        # Init an Exchange 
        self.in_channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)
        
        # Declare a queue to receive prediction response
        self.queue = self.in_channel.queue_declare(queue=configuration["in_queue"], exclusive=False)
        self.queue_name = self.queue.method.queue
        # Binding the exchange to the queue with specific routing
        self.in_channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=self.in_routing_key)
        

        
    def on_request(self, ch, method, props, body):
        # Process the data on request: sending back to host object
        if self.host_object != None:
            self.host_object.message_processing(ch, method, props, body)
        else:
            mess = json.loads(str(body.decode("utf-8")))
            print(mess)

    def start(self):
        # Start rabbit MQ
        self.in_channel.basic_qos(prefetch_count=1)
        self.in_channel.basic_consume(queue=self.queue_name,on_message_callback=self.on_request,auto_ack=True)
        self.in_channel.start_consuming()

    def stop(self):
        self.in_channel.close()

    def get_queue(self):
        return self.queue.method.queue