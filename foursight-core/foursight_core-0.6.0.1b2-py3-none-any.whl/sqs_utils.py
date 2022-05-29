from datetime import datetime
import boto3
import json
from .stage import Stage


class SQS(object):
    """
    class SQS is a collection of utils related to Foursight queues
    """

    def __init__(self, foursight_prefix):
        self.stage = Stage(foursight_prefix)

    def invoke_check_runner(self, runner_input):
        """
        Simple function to invoke the next check_runner lambda with runner_input
        (dict containing {'sqs_url': <str>})
        """
        client = boto3.client('lambda')
        # InvocationType='Event' makes asynchronous
        # try/except while async invokes are problematic
        try:
            response = client.invoke(
                FunctionName=self.stage.get_runner_name(),
                InvocationType='Event',
                Payload=json.dumps(runner_input)
            )
        except Exception:
            response = client.invoke(
                FunctionName=self.stage.get_runner_name(),
                Payload=json.dumps(runner_input)
            )
        return response

    def delete_message_and_propogate(self, runner_input, receipt, propogate=True):
        """
        Delete the message with given receipt from sqs queue and invoke the next
        lambda runner.

        Args:
            runner_input (dict): runner info, should minimally have 'sqs_url'
            receipt (str): SQS message receipt
            propogate (bool): if True (default), invoke another check runner lambda

        Returns:
            None
        """
        sqs_url = runner_input.get('sqs_url')
        if not sqs_url or not receipt:
            return
        client = boto3.client('sqs')
        client.delete_message(
            QueueUrl=sqs_url,
            ReceiptHandle=receipt
        )
        if propogate is True:
            self.invoke_check_runner(runner_input)

    def recover_message_and_propogate(self, runner_input, receipt, propogate=True):
        """
        Recover the message with given receipt to sqs queue and invoke the next
        lambda runner.

        Changing message VisibilityTimeout to 15 seconds means the message will be
        available to the queue in that much time. This is a slight lag to allow
        dependencies to process.
        NOTE: VisibilityTimeout should be less than WaitTimeSeconds in run_check_runner

        Args:
            runner_input (dict): runner info, should minimally have 'sqs_url'
            receipt (str): SQS message receipt
            propogate (bool): if True (default), invoke another check runner lambda

        Returns:
            None
        """
        sqs_url = runner_input.get('sqs_url')
        if not sqs_url or not receipt:
            return
        client = boto3.client('sqs')
        client.change_message_visibility(
            QueueUrl=sqs_url,
            ReceiptHandle=receipt,
            VisibilityTimeout=15
        )
        if propogate is True:
            self.invoke_check_runner(runner_input)

    def get_sqs_queue(self):
        """
        Returns boto3 sqs resource
        """
        queue_name = self.stage.get_queue_name()
        sqs = boto3.resource('sqs')
        try:
            queue = sqs.get_queue_by_name(QueueName=queue_name)
        except Exception:
            queue = sqs.create_queue(
                QueueName=queue_name,
                Attributes={
                    'VisibilityTimeout': '900',
                    'MessageRetentionPeriod': '3600'
                }
            )
        return queue

    @classmethod
    def send_sqs_messages(cls, queue, environ, check_vals, uuid=None):
        """
        Send messages to SQS queue. Check_vals are entries within a check_group.
        Optionally, provide a uuid that will be queued as the uuid for the run; if
        not provided, datetime.utcnow is used

        Args:
            queue: boto3 sqs resource (from get_sqs_queue)
            environ (str): foursight environment name
            check_vals (list): list of formatted check vals, like those from
                check_utils.CheckHandler().get_check_schedule
            uuid (str): optional string uuid

        Returns:
            str: uuid of queued messages
        """
        # uuid used as the MessageGroupId
        if not uuid:
            uuid = datetime.utcnow().isoformat()
        # append environ and uuid as first elements to all check_vals
        proc_vals = [[environ, uuid] + val for val in check_vals]
        for val in proc_vals:
            queue.send_message(MessageBody=json.dumps(val))
        return uuid

    @classmethod
    def get_sqs_attributes(cls, sqs_url):
        """
        Returns a dict of the desired attributes form the queue with given url
        """
        backup = {
            'ApproximateNumberOfMessages': 'ERROR',
            'ApproximateNumberOfMessagesNotVisible': 'ERROR'
        }
        client = boto3.client('sqs')
        try:
            result = client.get_queue_attributes(
                QueueUrl=sqs_url,
                AttributeNames=[
                    'ApproximateNumberOfMessages',
                    'ApproximateNumberOfMessagesNotVisible'
                ]
            )
        except Exception:
            return backup
        return result.get('Attributes', backup)
