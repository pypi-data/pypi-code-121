#!/usr/bin/env python3

import logging
from datetime import datetime
import pymongo

from metatools.config.mongodb import get_collection
from metatools.store import Store, FileStorageBackend, DerivedKey, NotFoundError, StoreObject

log = logging.getLogger('metatools.autogen')

class FetchCache:

	async def write(self, key_dict, body=None):
		pass

	async def read(self, key_dict, max_age=None, refresh_interval=None):
		pass

	async def record_fetch_failure(self, key_dict, failure_reason):
		pass


class FileStoreFetchCache(FetchCache):

	def __init__(self, db_base_path):
		self.store = Store(
			collection="fetch_cache",
			backend=FileStorageBackend(db_base_path=db_base_path),
			key_spec=DerivedKey(["method_name", "url", "encoding", "is_json"], optional_spec_list=["encoding", "is_json"])
		)

	async def write(self, key_dict, body=None):
		"""
		Write body (data, either string or JSON) to fetch cache. ``key_dict``
		must have ``method_name``, ``url``, and may also have ``is_json`` and
		``encoding``.
		"""
		now = datetime.utcnow()
		key_dict.update({
			"last_attempt": now,
			"fetched_on": now,
			"body": body
		})
		log.debug(f"Wrote to fetch cache, fetched_on: {now}")
		self.store.write(key_dict)

	async def read(self, key_dict, max_age=None, refresh_interval=None):
		log.debug(f"In FileStoreFetchCache.read, refresh_interval={refresh_interval}")
		# content_kwargs is stored at None if there are none, not an empty dict:
		try:
			result: StoreObject = self.store.read(key_dict)
		except NotFoundError:
			log.debug(f"File not found in store.")
			raise CacheMiss()
		if result is None or "fetched_on" not in result.data:
			log.debug(f"File found but fetched_on missing.")
			raise CacheMiss()
		elif refresh_interval is not None:
			if datetime.utcnow() - result.data["fetched_on"] <= refresh_interval:
				return result.data
			else:
				raise CacheMiss()
		elif max_age is not None and datetime.utcnow() - result.data["fetched_on"] > max_age:
			raise CacheMiss()
		else:
			return result.data

	async def record_fetch_failure(self, key_dict, failure_reason):
		now = datetime.utcnow()
		key_dict.update({
			"last_attempt": now,
			"last_failure_on": now,
			"failures": {"attempted_on": now, "failure_reason": failure_reason}
		})
		self.store.write(key_dict)


class MongoDBFetchCache(FetchCache):

	fc = None

	def __init__(self):
		self.fc = get_collection('fetch_cache')
		self.fc.create_index([("method_name", pymongo.ASCENDING), ("url", pymongo.ASCENDING)])
		self.fc.create_index("last_failure_on", partialFilterExpression={"last_failure_on": {"$exists": True}})

	async def write(self, key_dict, body=None):
		"""
		This method is called when we have successfully fetched something. In the case of a network resource such as
		a Web page, we will record the result of our fetching in the 'result' field so it is cached for later. In the
		case that we're recording that we successfully downloaded an Artifact (tarball), we don't store the tarball
		in MongoDB but we do store its metadata (hashes and filesize.)
		"""
		metadata = None
		now = datetime.utcnow()

		self.fc.update_one(
			key_dict,
			{"$set": {"last_attempt": now, "fetched_on": now, "metadata": metadata, "body": body}},
			upsert=True,
		)

	async def read(self, key_dict, max_age=None, refresh_interval=None):
		"""
		Attempt to see if the network resource or Artifact is in our fetch cache. We will return the entire MongoDB
		document. In the case of a network resource, this includes the cached value in the 'result' field. In the
		case of an Artifact, the 'metadata' field will include its hashes and filesize.
	
		``max_age`` and ``refresh_interval`` parameters are used to set criteria for what is acceptable for the
		caller. If criteria don't match, None is returned instead of the MongoDB document.
	
		In the case the document is not found or does not meet criteria, we will raise a CacheMiss exception.
		"""

		result = self.fc.find_one(key_dict)
		if result is None or "fetched_on" not in result:
			raise CacheMiss()
		elif refresh_interval is not None:
			if datetime.utcnow() - result["fetched_on"] <= refresh_interval:
				return result
			else:
				raise CacheMiss()
		elif max_age is not None and datetime.utcnow() - result["fetched_on"] > max_age:
			raise CacheMiss()
		else:
			return result

	async def record_fetch_failure(self, key_dict, failure_reason):
		"""
		It is important to document when fetches fail, and that is what this method is for.
		"""
		now = datetime.utcnow()
		self.fc.update_one(
			key_dict,
			{
				"$set": {"last_attempt": now, "last_failure_on": now},
				"$push": {"failures": {"attempted_on": now, "failure_reason": failure_reason}},
			},
			upsert=True
		)


class CacheMiss(Exception):
	pass
