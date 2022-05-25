"""Simple Pool object"""

from queue import Queue

"""
Adapted from http://pythonwise.blogspot.com/2016/09/simple-object-pools.html
"""
class InstancePool:
    """Pool of objects"""
    def __init__(self, objects):
        self._queue = Queue()
        for obj in objects:
            self._queue.put(obj)

    def lease(self):
        """Lease an object from the pool, should be used as contect manger. e.g.:

            with pool.lease() as conn:
                cur = conn.cursor()
                cur.execute('SELECT ...')
        """
        return self._queue.get()

    def _put(self, obj):
        self._queue.put(obj)


