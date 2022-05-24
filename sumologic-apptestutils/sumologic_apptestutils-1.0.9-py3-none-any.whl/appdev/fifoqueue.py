import json
import os
from time import sleep

import boto3
from botocore.exceptions import ClientError
from sumoappclient.common.logger import get_logger

logger = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log", LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))


class FifoQueue(object):

    def __init__(self, queue_name, force_create=False):
        queue_name = queue_name+".fifo"
        self.region_name = os.getenv('AWS_REGION', 'us-east-1')
        self.sqscli = boto3.resource('sqs', region_name=self.region_name)
        self.queue = self.get_or_create_queue(queue_name, force_create=force_create)

    def enque(self, msgdict):
        # assuming number of messages will not exceed 20k hence hardcoding groupid
        payload = json.dumps(msgdict)
        response = self.queue.send_message(MessageBody=payload, MessageGroupId='queue0')
        logger.debug("MessageId created: {0}".format(response.get('MessageId')))

    def deque(self, NUM_JOBS_TO_TRIGGER=5):
        # Todo ideally message should not be deleted unless job triggered
        jobs = []
        for message in self.queue.receive_messages(MaxNumberOfMessages = NUM_JOBS_TO_TRIGGER):
            jobs.append(json.loads(message.body))
            message.delete()
        return jobs

    @classmethod
    def create_queue(cls, queue_name, region_name):
        sqscli = boto3.resource('sqs', region_name=region_name)
        queue = sqscli.create_queue(QueueName=queue_name, Attributes={
            'MessageRetentionPeriod': str(7 * 24 * 60 * 60),
            'VisibilityTimeout': str(1 * 60 * 60),
            'FifoQueue': 'true',
            'ContentBasedDeduplication': 'true'
        })
        return queue

    def get_or_create_queue(self, queue_name, force_create=False):
        # Todo evaluate setting ContentBasedDeduplication by repo url

        try:
            queue =  self.sqscli.get_queue_by_name(QueueName=queue_name)
            if force_create:
                queue.delete()
                sleep(100) # after deleting queue wait for atleast 60sec
                queue = self.create_queue(queue_name, self.region_name)
        except ClientError as exc:
            non_existent_code = 'AWS.SimpleQueueService.NonExistentQueue'
            if exc.response['Error']['Code'] == non_existent_code:
                queue = self.create_queue(queue_name, self.region_name)
            else:
                raise
        logger.debug("Queue url retrieved: {0}".format(queue.url))
        return queue

    def destroy(self):
        self.queue.delete()
