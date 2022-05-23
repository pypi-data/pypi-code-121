import unittest
from test.unit.utilities.test_utils import check_class_docstrings_in_module


class TestTableOpDocumentation(unittest.TestCase):

    def test_docstrings(self):

        import lumipy.query.expression.table_op as table_op

        check_class_docstrings_in_module(self, table_op.base_table_op)
        check_class_docstrings_in_module(self, table_op.select_op)
        check_class_docstrings_in_module(self, table_op.where_op)
        check_class_docstrings_in_module(self, table_op.group_by_op)
        check_class_docstrings_in_module(self, table_op.group_aggregate_op)
        import lumipy.query.expression.table_op.having_op as having_op
        check_class_docstrings_in_module(self, having_op)
        check_class_docstrings_in_module(self, table_op.order_by_op)
        check_class_docstrings_in_module(self, table_op.limit_op)
