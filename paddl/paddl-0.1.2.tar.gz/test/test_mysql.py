from pytest import fixture, mark
from paddl import parse, mysql, ColType


class TestMySQL:
    @fixture
    def lower(self):
        return open('test/fixtures/lower.sql').read().replace("\n", ' ')

    @fixture
    def ddl(self):
        return open('test/fixtures/hello.sql').read().replace("\n", ' ')

    @fixture
    def ddls(self):
        return open('test/fixtures/many.sql').read().replace("\n", ' ')

    def test_parse(self, ddl):
        schema = parse(ddl, engine='mysql')
        table = schema.tables[0]
        assert table.name == 'bob'
        assert len(table.columns) == 2
        assert table.columns[0].name == 'id'
        assert table.columns[0].type == ColType.INT
        assert table.columns[1].name == 'name'
        assert table.columns[1].type == ColType.VARCHAR

    def test_case_insensitive(self, ddl):
        schema = parse(ddl, engine='mysql')
        table = schema.tables[0]
        assert table.name == 'bob'
        assert len(table.columns) == 2
        assert table.columns[0].name == 'id'
        assert table.columns[0].type == ColType.INT
        assert table.columns[1].name == 'name'
        assert table.columns[1].type == ColType.VARCHAR

    def test_many(self, ddls):
        schema = parse(ddls, engine='mysql')
        table = schema.tables[1]
        assert table.name == 'sam'
        assert len(table.columns) == 4
        assert table.columns[0].name == 'sam_id'
        assert table.columns[0].type == ColType.INT

    # test mysql lib
    @mark.skip("meh")
    def test_hello(self, ddl):
        result = mysql.parseString(ddl)
        assert result['table_name'] == 'bob'
        assert list(result) == ['CREATE', 'TABLE', 'bob',
                                '(', 'id', 'int', 'name', 'varchar', ')']

