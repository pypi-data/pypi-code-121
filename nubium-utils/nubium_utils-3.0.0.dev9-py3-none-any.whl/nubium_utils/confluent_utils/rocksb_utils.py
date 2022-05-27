from pathlib import Path
import rocksdb
from os import environ


class RDB:
    def __init__(self, table_name):
        opts = rocksdb.Options()
        opts.create_if_missing = True
        opts.max_open_files = 300000
        opts.write_buffer_size = 67108864
        opts.max_write_buffer_number = 3
        opts.target_file_size_base = 67108864

        opts.table_factory = rocksdb.BlockBasedTableFactory(
            filter_policy=rocksdb.BloomFilterPolicy(10),
            block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
            block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)))

        self.rdb = rocksdb.DB(f"{environ['TABLE_PATH']}/{table_name}.rocksdb", opts)

    def write(self, key, value):
        self.rdb.put(key.encode(), value.encode())

    def write_batch(self, write_dict):
        batch = rocksdb.WriteBatch()
        for k, v in write_dict.items():
            try:
                v = v.encode()
            except ValueError:
                pass
            batch.put(k.encode(), v)
        self.rdb.write(batch)

    def read(self, k):
        result = self.rdb.get(k.encode())
        if result:
            return result.decode()
        return result

    def delete(self, key):
        self.rdb.delete(key.encode())

    def close(self):
        # TODO: Add flush method
        self.rdb.close()
