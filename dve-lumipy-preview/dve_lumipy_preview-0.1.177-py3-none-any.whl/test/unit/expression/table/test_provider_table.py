import unittest

from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.sql_value_type import SqlValType
from test.unit.utilities.test_utils import make_test_atlas, assert_locked_lockable
from lumipy.query.expression.column.column_literal import LiteralColumn
from lumipy.query.expression.table.table_alias import AliasedTable

from datetime import datetime
from decimal import Decimal


class TestProviderClasses(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()

    def test_provider_instance_ctor(self):

        def generate_params_input(p_descr):

            params = p_descr.list_parameters()
            out_dict = {}
            for p in params:
                if p.get_type() == SqlValType.Int:
                    out_dict[p.name] = 123
                elif p.get_type() == SqlValType.Double:
                    out_dict[p.name] = 123.456
                elif p.get_type() == SqlValType.Date or p.get_type() == SqlValType.DateTime:
                    out_dict[p.name] = datetime(2020, 1, 1)
                elif p.get_type() == SqlValType.Boolean:
                    out_dict[p.name] = True
                elif p.get_type() == SqlValType.Text:
                    out_dict[p.name] = 'TESTING'
                elif p.get_type() == SqlValType.Decimal:
                    out_dict[p.name] = Decimal(10000)
                else:
                    raise ValueError(f"{p.name}: {p.get_type()}")
            return out_dict

        for meta in self.atlas.list_providers():

            if meta.get_provider_type() != 'DataProvider':
                continue

            if any(p.get_type() == SqlValType.Table for p in meta.list_parameters()):
                # Just test ctors that take scalar values
                continue

            param_input = generate_params_input(meta)

            inst = meta(**param_input)
            for k, v in param_input.items():
                # Assert that the value is contained inside the param assignment

                # In this case it's in a Literal expression object so it's further down the lineage
                param_val = inst._param_assignments[k]._lineage[1]
                literal_v = LiteralColumn(v)
                self.assertEqual(
                    param_val.get_sql(),
                    literal_v.get_sql(),
                    msg=f"Value for parameter {k} not found in {type(meta).__name__} test instance."
                )

            # Instances of the class should be immutable
            assert_locked_lockable(self, meta())

    def test_provider_instance_columns(self):

        for meta in self.atlas.list_providers():

            # When make an instance of the provider class
            inst = meta()

            # There should be the full set of columns on the instance
            self.assertEqual(len(inst.get_columns()), len(meta.list_columns()))

            # The columns should be available on the instance as class attributes of type SourceColumn
            for col in meta.list_columns():
                self.assertTrue(
                    hasattr(inst, col.name),
                    msg=f"Column {col.name} not found as field on {type(meta).__name__} test instance."
                )
                # They should be column types
                col_attr = getattr(inst, col.name)
                self.assertTrue(
                    isinstance(col_attr, SourceColumn),
                    msg=f'Column attached to test instance of {type(meta).__name__} was '
                        f'not a Column but was {type(col_attr).__name__}.'
                )

                # Column belonging to source table should have a source_table_hash that matches the source table
                self.assertEqual(hash(inst), col_attr.source_table_hash())

    def test_provider_instance_columns(self):

        for meta in self.atlas.list_providers():

            if meta.get_provider_type() != 'DataProvider':
                continue

            # Make an instance of the provider class
            inst = meta()
            # Check that the params are not attributes on the table object
            for p in meta.list_parameters():
                pname = p.get_name()
                self.assertFalse(hasattr(inst, pname))

    def test_provider_with_alias(self):

        for factory in self.atlas.list_providers():
            if factory.get_provider_type() != 'DataProvider':
                continue

            # When we make an instance (provider class) of the metaclass
            # When make an instance of the provider class
            inst = factory()
            lhs_inst = inst.with_alias("LHS")

            # Should be an alias table type and have 'as LHS' in its from argument
            self.assertTrue(isinstance(lhs_inst, AliasedTable))
            self.assertEqual(lhs_inst.get_from_arg_string(), f"{inst.get_from_arg_string()} AS LHS")

    def test_provider_wrong_params_failure(self):
        cls = self.atlas.lusid_logs_apprequest

        with self.assertRaises(ValueError) as ve:
            cls(planet='Arrakis')

        msg = str(ve.exception)

        self.assertIn("'planet' is not a valid parameter", msg)
        self.assertIn(cls.get_name(), msg)
        for param in cls.list_parameters():
            self.assertIn(param.get_name(), msg)

    def test_provider_table_valued_parameter(self):

        branches = self.atlas.dev_gitlab_branch()

        # Create table var for input parameter
        l_branches = branches.select(
            branches.project_id,
            branches.project_name,
            BranchName=branches.name
        ).where(
            branches.project_name.like('lusid-p%') &
            (branches.name != 'master')
        ).order_by(branches.name.ascending()).limit(3).to_table_var('branches')

        # Try to use it in a provider class
        commits = self.atlas.dev_gitlab_branchcommit(projects_and_branches=l_branches)

        qry_sql = commits.select('*').get_sql()
        # Table var should be set
        self.assertIn('@branches = ', qry_sql)
        # Table var should show up in where to set the ProjectsAndBranches parameter
        self.assertIn('[ProjectsAndBranches] = @branches', qry_sql)
