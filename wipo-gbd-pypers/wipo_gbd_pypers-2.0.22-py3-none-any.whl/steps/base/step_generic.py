from pypers.core.step import FunctionStep
from pypers.steps.base import merge_spec_dict
from pypers.core.interfaces.db.cache import CacheBase
import concurrent.futures
import os


class EmptyStep(FunctionStep):
    base_spec = {
        "args": {
            "inputs": [],
            "outputs": [],
            "params": []
        }
    }

    def _sub_arry_offset(self, max_paralel, length, offset):
        if offset + max_paralel < length:
            return offset + max_paralel
        return length

    def worker_parallel(self, items, caller, *args, **kwargs):
        CacheBase(self.meta['pipeline']['output_dir'], '')
        max_workers = int(os.environ.get('GBD_PYPERS_MAX_WORKERS', '250'))

        task_counter = 0
        # Make the list an iterator, so the same tasks don't get run repeatedly.

        with concurrent.futures.ThreadPoolExecutor() as executor:

            # Schedule the initial batch of futures.  Here we assume that
            # max_scans_in_parallel < total_segments, so there's no risk that
            # the queue will throw an Empty exception.
            futures = {
                executor.submit(caller, item, *args, **kwargs): item
                for item in items[task_counter:self._sub_arry_offset(
                    max_workers, len(items), task_counter)]
            }
            task_counter = len(futures)
            while futures:
                # Wait for the first future to complete.
                done, _ = concurrent.futures.wait(
                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                )
                for fut in done:
                    res = fut.result()
                    futures.pop(fut)
                    yield res
                # Schedule the next batch of futures.  At some point we might run out
                # of entries in the queue if we've finished scanning the table, so
                # we need to spot that and not throw.
                for item in items[task_counter:self._sub_arry_offset(
                        len(done), len(items), task_counter)]:
                    task_counter += 1
                    futures[executor.submit(caller, item, *args, **kwargs)] = item

    def __init__(self, *args, **kwargs):
        merge_spec_dict(self.spec, self.base_spec)
        super(EmptyStep, self).__init__(*args, **kwargs)
        self.logger = self.log

