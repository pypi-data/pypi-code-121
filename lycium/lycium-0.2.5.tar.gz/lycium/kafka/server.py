#!/bin/bash
# encoding: utf-8
""" 

"""
from lycium.kafka.kafkaWorker import KafkaWorker
import json

hosts = ["localhost:9092","localhost:9093","localhost:9094"]

async def work(message):
    """ """
    value = message.body
    print(value)
    value = json.loads(value)
    return json.dumps({"method":"11","reply_method":value['action']})

def run():
    kafak_worker = KafkaWorker(hosts,private_topic="server11")
    kafak_worker.subscribe("test", work)
    kafak_worker.event_loop.run_forever()


if __name__ == '__main__':
    run()