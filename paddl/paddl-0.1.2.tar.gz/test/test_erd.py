from pytest import fixture
from paddl import erd, Table, Schema


FOO_EXPECTED = """table(foo) {
column (col1): int
column (col2): int
}"""


class TestERD:
    @fixture
    def schema(self):
        tables = [
            Table(
               name="foo",
               columns=[
                   {"name": "col1", "type": "int"},
                   {"name": "col2", "type": "int"},
               ]
            )
        ]
        return Schema("blah", tables=tables)

    def test_erd(self, schema):
        diagram = erd.render(schema)
        assert 'foo' in diagram
        assert 'col1' in diagram
        assert 'col2' in diagram
