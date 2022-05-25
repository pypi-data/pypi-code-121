import json
import time
import boto3
from datetime import datetime
from decimal import Decimal
from time import sleep
from boto3.dynamodb.conditions import Key, Attr

class DecimalEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, Decimal):
			if abs(o) % 1 > 0:
				return float(o)
			else:
				return int(o)
		elif isinstance(o, list):
			for i in xrange(len(o)):
				o[i] = self.default(o[i])
			return o
		elif isinstance(o, set):
			new_list = []
			for index, data in enumerate(o):
				new_list.append(self.default(data))
				
			return new_list
		elif isinstance(o, dict):
			for k in o.iterkeys():
				o[k] = self.default(o[k])
			return o
		elif isinstance(o, (datetime.date, datetime)):
			return o.isoformat()
		return super(DecimalEncoder, self).default(o)

class talk_with_dynamo():
	def __init__(self, table, boto_session, region='us-east-1', check_index=False, debug=False):
		self.boto_session = boto_session
		self.dynamodb = self.boto_session.resource('dynamodb', region_name=region)
		self.table = self.dynamodb.Table(table)
		self.check_index = check_index

	def query(self, partition_key, partition_key_attribute, sorting_key=False, sorting_key_attribute=False, index=False, queryOperator=False, betweenValue=False):
		"""
		Query a DynamoDB Table.\n
		queryOperator can now be set to one of the following: gt, gte, lt, lte, between
		\tgt: greater than (>)
		\tgte: greater than or equal to (>=)
		\tlt: less than (<)
		\tlte: less than or equal to (<=)
		\tbetween: condition where the attribute is greater than or equal to the low value and less than or equal to the high value.

		betweenValue: Expecting a tuple of two values and is intended to be used with the between queryOperator
		"""

		if self.check_index:
			# When adding a global secondary index to an existing table, you cannot query the index until it has been backfilled.
			# This portion of the script waits until the index is in the “ACTIVE” status, indicating it is ready to be queried.
			while True:
				if not self.table.global_secondary_indexes or self.table.global_secondary_indexes[0]['IndexStatus'] != 'ACTIVE':
					print('[{}]  Waiting for index to backfill...'.format('INFO'))
					sleep(5)
					self.table.reload()
				else:
					break

		if index:
			response = self.table.query(
				IndexName=index,
				KeyConditionExpression=Key(partition_key).eq(partition_key_attribute),
			)
		elif index and sorting_key and sorting_key_attribute:
			response = self.table.query(
				IndexName=index,
				KeyConditionExpression=Key(partition_key).eq(partition_key_attribute) & Key(sorting_key).eq(sorting_key_attribute),
			)
		elif partition_key and partition_key_attribute and sorting_key and sorting_key_attribute and not queryOperator:
			response = self.table.query(
				KeyConditionExpression=Key(partition_key).eq(partition_key_attribute) & Key(sorting_key).eq(sorting_key_attribute),
			)
		elif partition_key and partition_key_attribute and sorting_key and sorting_key_attribute and queryOperator and not betweenValue:
			if queryOperator == 'gt': 
				response = self.table.query(
					KeyConditionExpression=Key(partition_key).eq(partition_key_attribute) & Key(sorting_key).gt(sorting_key_attribute),
				)
			elif queryOperator == 'gte': 
				response = self.table.query(
					KeyConditionExpression=Key(partition_key).eq(partition_key_attribute) & Key(sorting_key).gte(sorting_key_attribute),
				)
			elif queryOperator == 'lt': 
				response = self.table.query(
					KeyConditionExpression=Key(partition_key).eq(partition_key_attribute) & Key(sorting_key).lt(sorting_key_attribute),
				)
			elif queryOperator == 'lte': 
				response = self.table.query(
					KeyConditionExpression=Key(partition_key).eq(partition_key_attribute) & Key(sorting_key).lte(sorting_key_attribute),
				)
			else:
				response = ""

		elif partition_key and partition_key_attribute and sorting_key and queryOperator and betweenValue:
			if queryOperator == 'between' and betweenValue: 
				lowValue, highValue = betweenValue

				response = self.table.query(
					KeyConditionExpression=Key(partition_key).eq(partition_key_attribute) & Key(sorting_key).between(lowValue, highValue),
				)
			else:
				response = ""
		elif partition_key and partition_key_attribute:
			response = self.table.query(
				KeyConditionExpression=Key(partition_key).eq(partition_key_attribute),
			)
		else:
			response = ""

		return response

	def getItem(self, partition_key, partition_key_attribute, sorting_key=False, sorting_key_attribute=False):
		if partition_key and partition_key_attribute and sorting_key and sorting_key_attribute:
			response = self.table.get_item(
				Key={
					partition_key: partition_key_attribute,
					sorting_key: sorting_key_attribute
				}
			)
		elif partition_key and partition_key_attribute:
			response = self.table.get_item(
				Key={
					partition_key: partition_key_attribute
				}
			)
		else:
			response = ""

		return response

	def batchGetItem(self, batch_keys):
		"""
		Gets a batch of items from Amazon DynamoDB. Batches can contain keys from
		more than one table.\n
		When Amazon DynamoDB cannot process all items in a batch, a set of unprocessed
		keys is returned. This function uses an exponential backoff algorithm to retry
		getting the unprocessed keys until all are retrieved or the specified
		number of tries is reached.\n
		:param batch_keys: The set of keys to retrieve. A batch can contain at most 100 keys. Otherwise, Amazon DynamoDB returns an error.\n
		:return: The dictionary of retrieved items grouped under their respective table names.\n\n
		Input Object Shape Example: {'tableName': {'Keys': [{'PartitionKey': 'PartitionKeyAttribute', 'SortingKey': 'SortingKey'}]}}
		"""
		tries = 0
		max_tries = 5
		sleepy_time = 1  # Start with 1 second of sleep, then exponentially increase.
		retrieved = {key: [] for key in batch_keys}
		while tries < max_tries:
			response = self.dynamodb.batch_get_item(RequestItems=batch_keys)
			# Collect any retrieved items and retry unprocessed keys.
			for key in response.get('Responses', []):
				retrieved[key] += response['Responses'][key]
			unprocessed = response['UnprocessedKeys']
			if len(unprocessed) > 0:
				batch_keys = unprocessed
				unprocessed_count = sum(
					[len(batch_key['Keys']) for batch_key in batch_keys.values()])
				if self.debug:
					print(f"{unprocessed_count} unprocessed keys returned. Sleep, then retry.")
				tries += 1
				if tries < max_tries:
					if self.debug:
						print(f"Sleeping for {sleepy_time} seconds.")
					time.sleep(sleepy_time)
					sleepy_time = min(sleepy_time * 2, 32)
			else:
				break

		return retrieved

	def update(self, partition_key_attribute, sorting_key_attribute, update_key, update_attribute):
		"""
		This method is deprecated and should not be used. 
		"""
		response = self.table.update_item(
			Key={
			'UniqueID': partition_key_attribute,
			'Category': sorting_key_attribute
			},
			UpdateExpression="set #k = :a",
			ExpressionAttributeNames = {
				"#k" : update_key
			},
			ExpressionAttributeValues={
				':a': update_attribute
			},
			ReturnValues="UPDATED_NEW"
		)
		return response

	def updateV2(self, partition_key_attribute, update_key, update_attribute, sorting_key_attribute=None, conditionExpression=None, conditionCheck=None):
		"""
		Edits an existing item's attributes, or adds a new item to the table if it does not already exist. You can also perform a conditional update on an existing item (insert a new attribute name-value pair if it doesn't exist, or replace an existing name-value pair if it has certain expected attribute values).
		updateV2(partition_key_attribute, update_key, update_attribute, sorting_key_attribute=None, conditionExpression=None, conditionCheck=None)
		"""
		key = {}
		key['UniqueID'] = partition_key_attribute

		if sorting_key_attribute:
			key['Category'] = sorting_key_attribute

		try:
			if conditionExpression and conditionCheck:
				response = self.table.update_item(
					Key=key,
					UpdateExpression="set #k = :a",
					ExpressionAttributeNames = {
						"#k" : update_key
					},
					ExpressionAttributeValues={
						':a': update_attribute
					},
					ConditionExpression=Attr(conditionExpression).eq(conditionCheck),
					ReturnValues="UPDATED_NEW"
				)
			else: 
				response = self.table.update_item(
					Key=key,
					UpdateExpression="set #k = :a",
					ExpressionAttributeNames = {
						"#k" : update_key
					},
					ExpressionAttributeValues={
						':a': update_attribute
					},
					ReturnValues="UPDATED_NEW"
				)
		except Exception as e:
			if "ConditionalCheckFailedException" in str(e):
				response = {'error': 'ConditionalCheckFailedException'}
			else:
				response = {'error': str(e)}
		return response

	def insert(self, payload):
		response = self.table.put_item(Item=payload)

		return response

	def delete(self, partition_key_attribute, sorting_key_attribute=False):
		key = {}
		key['UniqueID'] = partition_key_attribute

		if sorting_key_attribute:
			key['Category'] = sorting_key_attribute
		
		response = self.table.delete_item(
			Key=key
		)
		return response
