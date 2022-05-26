#!/bin/bash
# encoding: utf-8
""" 

"""

from lycium.kafka.kafkaWorker import KafkaWorker
import asyncio
import datetime
import json

hosts = ["localhost:9092", "localhost:9093", "localhost:9094"]


async def test_query(worker, message):
    print("start query {0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    resp = await worker.send(topic="test",
                             message=json.dumps(message).encode("utf-8"),
                             content_type='test',
                             content_encoding='GBK',
                             group_id='0',
                             message_id='1',
                             msg_type='msg_type',
                             user_id='user11',
                             app_id='10',
                             headers={'name1': '123', 'name2': '321'},
                             need_reply=True)
    print("end query {0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("client receive value:{0}".format(resp.body))


def run():
    kafak_worker = KafkaWorker(hosts, private_topic="client23")
    event_loop = kafak_worker.event_loop
    event_loop.call_later(1, event_loop.create_task, test_query(kafak_worker, {"action": "say"}))
    event_loop.call_later(2, event_loop.create_task, test_query(kafak_worker, {"action": "eat"}))
    event_loop.run_forever()


if __name__ == "__main__":
    run()
