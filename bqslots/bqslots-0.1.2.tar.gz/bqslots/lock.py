"""
Try and create lock based off algorithm described here
https://www.joyfulbikeshedding.com/blog/2021-05-19-robust-distributed-locking-algorithm-based-on-google-cloud-storage.html
"""
from datetime import datetime, timedelta

import backoff
import uuid

from google.cloud import storage
from google.api_core.exceptions import PreconditionFailed, NotFound


class Client:

    def __init__(self, bucket, lock_file_path: str = "lock.txt", expiry=30, lock_id_prefix='default'):
        self.bucket = bucket
        self.lock_file_path = lock_file_path
        self.expiry = expiry
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.get_bucket(bucket)
        self.lock_file_path = lock_file_path
        self.blob = self.bucket.blob(lock_file_path)
        self.lock_id_prefix = lock_id_prefix
        self.lock_client_id = f"{lock_id_prefix}-{str(uuid.uuid4())[:8]}"

    def lock(self) -> bool:
        """
        Creates a lock with the specified GCS path.
        Returns: boolean on lock acquisition status
        """

        print(f"Acquiring lock: {self.lock_file_path}")

        try:
            self._upload_lock_file()
            print("Lock acquired: {}".format(self.lock_file_path))
            return True
        except PreconditionFailed:  # this means lock already exists
            print(f"Lock as its already in use, checking expiration: {self.lock_file_path}")

            # check if lock is expired
            blob_metadata = self.bucket.get_blob(self.lock_file_path).metadata
            expiration_timestamp = datetime.fromisoformat(blob_metadata.get('expiration_timestamp'))
            lock_client_id = blob_metadata.get('lock_id')

            if expiration_timestamp < datetime.utcnow():  # lock is stale so we bin it
                print(f"Lock is stale so removing lock:{lock_client_id}")
                self.free_lock()
                self.lock()
                return True

            print(f"Waiting for lock: {lock_client_id} to be freed or expire")
            return False

    def free_lock(self) -> bool:
        """
        Attempts to free lock
        Returns: boolean on success
        """
        try:
            self.bucket.blob(self.lock_file_path).delete()
        except NotFound:
            print("lock already freed so do nothing")

        print(f"Lock released: {self.lock_file_path}")
        return True

    def wait_for_lock(self, *backoff_args, **backoff_kwargs):
        """
        Wait for lock using backoff predicate variables
        Args:
            *backoff_args:
            **backoff_kwargs:

        Returns:

        """

        @backoff.on_predicate(*backoff_args, **backoff_kwargs)
        def backoff_lock():
            print(f"Backing off lock release: {self.lock_file_path}")
            return self.lock()

        return backoff_lock()

    def wait_for_lock_expo(self, base=2, factor=0.5, max_value=10, max_time=60, jitter=backoff.full_jitter, *args,
                           **kwargs):
        """
        A helper function for `wait_for_lock` that uses exponential backoff.
        :param base: waiting time (sec) is: factor * (base ** n)
        :param factor: waiting time (sec) is: factor * (base ** n)
        :param max_value: the ceiling value for retry time, in seconds
        :param max_time: total retry timeout, in seconds
        :param jitter: See backoff.on_predicate for details. Pass jitter=None for no jitter.
        :return: If the lock was acquired or not
        """
        return self.wait_for_lock(wait_gen=backoff.expo, base=base, factor=factor, max_value=max_value,
                                  max_time=max_time, jitter=jitter, *args, **kwargs)

    def _upload_lock_file(self) -> None:
        """
        Upload dummy lock file with id and ttl metadata
        Returns:

        """
        file = 'lock.txt'
        open(file, 'a').close()
        self.blob.upload_from_filename(file, if_generation_match=0)
        metadata = {'expiration_timestamp': datetime.utcnow() + timedelta(seconds=self.expiry),
                    'lock_id': self.lock_client_id
                    }
        self.blob.metadata = metadata
        self.blob.patch()
