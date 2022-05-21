from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer
from confluent_avro import AvroKeyValueSerde, SchemaRegistry
import json 


"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    KafkaBase :  Initializes KafkaBootstrapServer
    Methods   :  To be buit as per requirement
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
class KafkaBase:
    
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers


"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    KafkaTopic :  Used in the creation and deletion of topics, along with streaming data into the topics
    Methods    :  create_topic - Creation of a new topic
                  delete_topic - Deletion of a topic
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
      
class KafkaTopic(KafkaBase):

    def __init__(self, bootstrap_servers, client_id):
        self.client_id = client_id
        super(KafkaTopic, self).__init__(bootstrap_servers)

    def create_topic(self, topic_name_list):    
        admin_client = KafkaAdminClient(
            bootstrap_servers= self.bootstrap_servers, 
            client_id= 'test'
        )
        topic_list = []
        for topic_name in topic_name_list:
            topic_list.append(NewTopic(name=topic_name, num_partitions=1, replication_factor=1))

        admin_client.create_topics(new_topics=topic_list, validate_only=False)

    def delete_topic(self, topic_name_list):    
        admin_client = KafkaAdminClient(
            bootstrap_servers= self.bootstrap_servers, 
            client_id=self.client_id
        )
        admin_client.delete_topics(topics=topic_name_list)

"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    KafkaProducerConsumer   :  Used in producing and consuming data to and from kafka
    Methods                 :  kafka_json_producer - Produces data in json format
                               kafka_json_consumer - Consumes data which is in json format
                               kafka_avro_consumer - Consumes data which is in avro format
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

class KafkaProducerConsumer(KafkaBase):

    # Messages will be serialized as JSON 
    def json_serializer(self, messages):
        return json.dumps(messages).encode('utf-8')

    def kafka_json_producer(self, topic_name,  message_type, key = None, messages_list = None,):
        producer = KafkaProducer(
                        bootstrap_servers=self.bootstrap_servers
                    )
        if message_type == 'list':
            for messages in messages_list:
                producer.send(topic_name, self.json_serializer(messages))
        elif  message_type == 'dict':
            producer.send(topic_name, self.json_serializer(messages_list))


    def kafka_json_consumer(self, topic_name, auto_offset_reset, consumer_group, consumer_timeout_ms = -1):
        consumer = KafkaConsumer( bootstrap_servers=self.bootstrap_servers, 
                                    auto_offset_reset=auto_offset_reset,
                                    consumer_timeout_ms=consumer_timeout_ms, 
                                    enable_auto_commit=True,
                                    group_id= consumer_group,
                                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                                )
        consumer.subscribe(topic_name)
        for i in consumer:
            yield (i)

    def kafka_avro_consumer(self, topic_name, auto_offset_reset, schema_registry_url, consumer_group, consumer_timeout_ms = -1, Key=None):
        registry_client = SchemaRegistry(schema_registry_url)
        avroSerde = AvroKeyValueSerde(registry_client, topic_name)
        consumer = KafkaConsumer(   topic_name, 
                                    auto_offset_reset= auto_offset_reset,
                                    consumer_timeout_ms=consumer_timeout_ms,
                                    enable_auto_commit=True,
                                    group_id= consumer_group,
                                    bootstrap_servers=self.bootstrap_servers
                                )
        try:
            for msg in consumer:
                v = avroSerde.value.deserialize(msg.value)
                if( Key != None):
                    v[Key] = ((msg.key).decode("utf-8"))
                yield(v)
            consumer.close()
        except: 
            raise StopIteration