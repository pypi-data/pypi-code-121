import pytest
from nubium_utils.confluent_utils.rocksdb_utils import RDB


class TestRdb:
    @pytest.fixture(scope='session')
    def rdb_instance(self, tmp_path_factory):
        table_path = tmp_path_factory.mktemp('rdb_table')
        return RDB(table_name='test', table_path=table_path)

    def test_rdb_read_write(self, rdb_instance):
        rdb_instance.write('test_key', 'test_value')
        assert rdb_instance.read('test_key') == 'test_value'

    def test_rdb_write_batch(self, rdb_instance):
        rdb_instance.write_batch({'test_key1': 'test_value1', 'test_key2': 'test_value2'})
        assert rdb_instance.read('test_key1') == 'test_value1'
        assert rdb_instance.read('test_key2') == 'test_value2'
        
    def test_rdb_delete(self, rdb_instance):
        rdb_instance.write('delete_test', 'delete_me')
        assert rdb_instance.read('delete_test') == 'delete_me'
        rdb_instance.delete('delete_test')
        assert rdb_instance.read('delete_test') is None

    def test_rdb_close(self, rdb_instance):
        assert len(rdb_instance.rdb.column_families) > 0
        rdb_instance.close()
        assert len(rdb_instance.rdb.column_families) == 0


if __name__ == '__main__':
    pytest.main([__file__])
