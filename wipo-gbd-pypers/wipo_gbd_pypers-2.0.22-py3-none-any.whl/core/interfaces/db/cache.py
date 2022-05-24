import os
import json
from pypers.core.interfaces import db
from pypers.utils.filelock import FileLock
import shutil


def clear_cache(output_dir):
    if not output_dir:
        return
    path = os.path.join(output_dir, '_cache')
    if os.path.exists(path):
        shutil.rmtree(path)


def cache(func):
    def decorator(self, *args, **kwargs):
        if self.in_manager:
            return _apply_wrapper(self, func, *args, **kwargs)
        else:
            with FileLock(self.output_dir, self.key):
                return _apply_wrapper(self, func, *args, **kwargs)

    return decorator


def _apply_wrapper(self, func, *args, **kwargs):
    payload = getattr(self, 'get_document')(*args, *kwargs)
    kwargs['_cache_payload'] = payload
    result = func(self, *args, **kwargs)
    return getattr(self, 'save_document')(result)


class CacheBase:
    def __init__(self, output_dir, key, get_existing=False, document=None):
        self.output_dir = output_dir
        self.key = key
        self.path = os.path.join(output_dir,
                                 '_cache',
                                 '%s.json' % key)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if document:
            with open(self.path, 'w') as f:
                json.dump(document, f)
        self.get_existing = get_existing
        self.in_manager = False
        self.document = None
        self.lock = None

    def __enter__(self):
        """ Activated when used in the with statement.
            Should automatically acquire a lock to be used in the with block.
        """
        self.lock = FileLock(self.output_dir, self.key)
        if not self.in_manager:
            self.lock.acquire()
            self.in_manager = True
        return self

    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
        """
        self.lock.release()
        if self.in_manager:
            self.in_manager = False
            self.save_document(self.document)

    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a lockfile
            lying around.
        """
        if self.lock:
            self.lock.release()
        if self.in_manager:
            self.in_manager = False
            self.save_document(self.document)

    def get_document(self, *args, **kwargs):
        if self.document:
            return self.document
        elif os.path.exists(self.path):
            with open(self.path, 'r') as f:
                payload = json.load(f)
                if self.in_manager:
                    self.document = payload
                return payload
        else:
            if self.get_existing:
                payload = self.get_db_document(*args, **kwargs)
                if not payload:
                    payload = self.create_new_entry(*args, **kwargs)
            else:
                payload = self.create_new_entry(*args, **kwargs)
            if self.in_manager:
                self.document = payload
            return self.save_document(payload)


    def save_document(self, payload):
        if not self.in_manager:
            with open(self.path, 'w') as f:
                json.dump(payload, f)
        return payload


class CachedCopy(CacheBase):

    def save_db_documnet(self, items):
        cached_path = [os.path.join(
            self.output_dir, '_cache', '%s.json' % key) for key in items]
        db.get_pre_prod_db_history().put_items(cached_path)

    def get_db_document(self, collection, appnum, office_extraction_date, *args, **kwargs):
        return db.get_pre_prod_db_history().get_document(
            collection, appnum, office_extraction_date)

    def create_new_entry(self, collection, appnum, office_extraction_date, run_id, *args, **kwargs):
        raise NotImplemented()
