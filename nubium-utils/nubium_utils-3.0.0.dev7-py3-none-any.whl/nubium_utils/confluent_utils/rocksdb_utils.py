import rocksdb
from rocksdb.errors import RocksIOError
from os import environ, makedirs
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars


class RdbTableInUse(Exception):
    def __init__(self, table_name):
        super().__init__(f'Table "{table_name}" is currently in use by another instance.')


class RDB:
    def __init__(self, table_name, table_path=None):
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

        if not table_path:
            table_path = env_vars()['NU_TABLE_PATH']
        makedirs(table_path, exist_ok=True)
        self.full_db_path = f"{table_path}/{table_name}.rocksdb"
        try:
            self.rdb = rocksdb.DB(self.full_db_path, opts)
        except RocksIOError as e:
            if 'Resource temporarily unavailable' in e.args[0].decode():
                raise RdbTableInUse(table_name)

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
