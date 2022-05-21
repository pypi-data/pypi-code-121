from typing import List
from .connector.amqp_client import Amqp_Connector
from .connector.mqtt_client import Mqtt_Connector
from .connector.prom_connector import Prom_Connector
from .probes import Gauge, Counter, Summary, Histogram
import json, uuid
import threading
from threading import Thread

class Qoa_Client(object):
    # Init QoA Client
    def __init__(self, client_conf: dict, connector_conf: dict, metric_conf: dict):
        '''
        Client configuration contains the information about the client and its configuration in form of dictionary
        Example: 
        { 
            "client_id": "aaltosea1",
            "component_id": "data_processing"
        }
        The `connector_conf` is the dictionary containing multiple connector configuration (amqp, mqtt, kafka)
        Example: 
        {
            "amqp_connector":{
                "class": "amqp",
                "conf":{
                    "end_point": "195.148.22.62",
                    "exchange_name": "qoa4ml",
                    "exchange_type": "topic",
                    "out_routing_key": "qoa.report.ml"
                }
            }
        }
        '''

        self.config = client_conf
        self.metrics = {}
        self.connector = {}
        # Init all connectors in for loop 
        for key in connector_conf:
            self.connector[key] = self.init_connector(connector_conf[key])
        
        # Set default connector for sending monitoring data if not specify
        self.default_connector = list(self.connector.keys())[0]
        self.add_metric(metric_conf)
        self.lock = threading.Lock()
        

    def init_connector(self, configuration: dict):
        if configuration["class"] == "amqp":
            return Amqp_Connector(configuration["conf"])
        if configuration["class"] == "mqtt":
            return Mqtt_Connector(configuration["conf"])
        # if configuration["class"] == "kafka":
        #     return Kafka_Connector(configuration["conf"])
        
    def add_metric(self, metric_conf: dict):
        # Add multiple metrics 
        for key in metric_conf:
            self.metrics[key] = self.init_metric(key, metric_conf[key])

    def init_metric(self, name, configuration: dict):
        # init individual metrics
        if configuration["class"] == "Gauge":
            return Gauge(name, configuration["description"], configuration["default"])
        elif configuration["class"] == "Counter":
            return Counter(name, configuration["description"], configuration["default"])
        elif configuration["class"] == "Summary":
            return Summary(name, configuration["description"], configuration["default"])
        elif configuration["class"] == "Histogram":
            return Histogram(name, configuration["description"], configuration["default"])

    def get(self):
        # TO DO:
        return self.config

    def get_metric(self, key=None):
        # TO DO:
        if key == None:
            return self.metrics
        elif isinstance(key, list):
            return dict((k, self.metrics[k]) for k in key)
        else: 
            return self.metrics[key]

    def set(self, key, value):
        # TO DO:
        try:
            self.config[key] = value
        except Exception as e:
            print("{} not found - {}".format(key,e))
    
    
    def generate_report(self, metric:list=None):
        report = self.config
        report["metric"] = {}
        if metric == None:
            metric = list(self.metrics.keys())
        for key in metric:
            report["metric"][key] = self.metrics[key].get_val()
        return report
    

    def asyn_report(self, metrics:list=None, connectors:list=None):
        report = self.generate_report(metrics)
        body_mess = json.dumps(report)
        self.lock.acquire()
        if connectors == None:
            self.connector[self.default_connector].send_data(body_mess,str(uuid.uuid4()))
        else:
            for connector in connectors:
                print(connector)
        self.lock.release()

    def report(self, metrics:list=None, connectors:list=None):
        sub_thread = Thread(target=self.asyn_report, args=(metrics,connectors))
        sub_thread.start()


    def __str__(self):
        return str(self.config) + '\n' + str(self.connector)