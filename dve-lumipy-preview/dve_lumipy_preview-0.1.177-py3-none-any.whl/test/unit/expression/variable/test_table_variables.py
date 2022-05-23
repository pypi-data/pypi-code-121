import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from lumipy.query.expression.sql_value_type import SqlValType
from lumipy.query.expression.variable.base_variable import BaseVariable
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string


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
        elif p.get_type() == SqlValType.Table:
            pass
        else:
            raise ValueError(f"{p.name}: {p.get_type()}")
    return out_dict


class TestTableVariable(unittest.TestCase):

    def test_table_at_var_creation(self):

        atlas = make_test_atlas()
        for provider in atlas.list_providers():

            param_input = generate_params_input(provider)

            if len(provider.list_columns()) == 0:
                continue

            table_var_name = 'test'
            inst = provider(**param_input).select('*')
            table_var = inst.to_table_var(table_var_name)

            # Test that the result inherits from BaseVariable
            self.assertTrue(issubclass(type(table_var), BaseVariable))

            # Test that the variable assignment is present and correct
            self.assertEqual(
                table_var.get_assignment_sql(),
                f"@{table_var_name} = {inst.get_table_sql()};"
            )

            # Test that the var name is correct
            self.assertEqual(table_var.get_at_var_name(), table_var_name)

            # Test that argument to the from keyword is correct
            self.assertEqual(table_var.get_from_arg_string(), f"@{table_var_name}")

            # Test that the entire sql string is correct with select('*')
            selected_table_var = table_var.select('*')
            self.assertIn(
                standardise_sql_string(table_var.get_assignment_sql()),
                standardise_sql_string(selected_table_var.get_sql())
            )

    def test_table_at_var_creation_with_aliased_columns(self):
        atlas = make_test_atlas()
        for provider in atlas.list_providers():

            if provider.get_provider_type() != 'DataProvider':
                continue

            param_input = generate_params_input(provider)

            inst = provider(**param_input)

            aliased_cols = [c.with_alias(f"Alias{i}") for i, c in enumerate(inst.get_columns()[:4])]
            if len(aliased_cols) != 4:
                continue
            aliased_select = inst.select(*aliased_cols)
            from_aliased = aliased_select.to_table_var("from_alias")

            self.assertTrue(issubclass(type(from_aliased), BaseVariable))

            # Test that the aliased columns are present on the variable table with alias name
            self.assertEqual(
                {'alias0', 'alias1', 'alias2', 'alias3'},
                set([c.get_name() for c in from_aliased.get_columns()])
            )

            # Test that the variable assignment string is correct
            self.assertEqual(
                standardise_sql_string(from_aliased.get_assignment_sql()),
                standardise_sql_string(f"@from_alias = {aliased_select.get_sql()};")
            )

            # Test that the entire sql string is correct with select('*')
            selected = from_aliased.select('*')
            sql = selected.get_sql()
            self.assertIn(
                standardise_sql_string("SELECT [Alias0], [Alias1], [Alias2], [Alias3] FROM @from_alias"),
                standardise_sql_string(selected.get_sql())
            )

            # Test that select works with explicit columns from the table var instance
            cols = from_aliased.get_columns()[:2]
            selected = from_aliased.select(*cols)
            self.assertEqual(len(selected.get_columns()), 2)

    def test_table_creation_with_derived_columns(self):

        atlas = make_test_atlas()
        rtrace = atlas.lusid_logs_requesttrace()

        main_cols = [c for c in rtrace.get_columns() if c.is_main()]
        derived = rtrace.select(
            *main_cols,
            non_self_time=rtrace.duration - rtrace.self_time
        ).to_table_var("WithDerived")

        selected = derived.select('*')
        self.assertEqual(len(selected.get_columns()), len(main_cols)+1)

    def test_table_at_var_creation_from_join_columns(self):

        # Given two data providers
        atlas = make_test_atlas()
        app_req = atlas.lusid_logs_apprequest()
        rtrace = atlas.lusid_logs_requesttrace()

        # When they're joined, a single column is selected, and scalar var is derived from the result
        join = app_req.inner_join(
            rtrace,
            on=app_req.request_id == rtrace.request_id
        ).select('^')
        table = join.to_table_var("JoinMain")

        # Then it should be a subclass of BaseVariable
        self.assertTrue(issubclass(type(table), BaseVariable))
        # Then it should have a sql string that's its name with the @@ prefix
        self.assertEqual(table.get_sql(), '@JoinMain')
        # Then the definition of the variable in the assignment string should equal the @@name = (table sql)
        flat1 = ' '.join(table.get_assignment_sql().split())
        flat2 = ' '.join(f'@JoinMain = {join.get_sql()};'.split())
        self.assertEqual(flat1, flat2)
        self.assertEqual(len(table.get_columns()), len(join.get_columns()))

    def test_table_at_var_creation_error_protected_names(self):

        atlas = make_test_atlas()
        app_req = atlas.lusid_logs_apprequest().select('*')
        with self.assertRaises(ValueError):
            app_req.to_table_var('from')

    def test_table_at_var_from_union_expression(self):

        atlas = make_test_atlas()
        rtrace = atlas.lusid_logs_requesttrace()
        end_at = datetime.utcnow()
        app_req = atlas.lusid_logs_apprequest(
            start_at=end_at - timedelta(days=1),
            end_at=end_at
        )

        lhs = app_req.select('^').to_table_var('table1')
        rhs = rtrace.select('^').to_table_var('table2')

        lhs_select = lhs.select(*lhs.get_columns()[:4])
        rhs_select = rhs.select(*rhs.get_columns()[:4])

        union = lhs_select.union_all(rhs_select).to_table_var('union_var')

        sql = union.select('*').get_sql()
        self.assertIn(
            standardise_sql_string(lhs.get_assignment_sql()),
            standardise_sql_string(sql)
        )
        self.assertIn(
            standardise_sql_string(rhs.get_assignment_sql()),
            standardise_sql_string(sql)
        )

    def test_table_at_var_column_source_table_hash(self):

        atlas = make_test_atlas()
        rtrace = atlas.lusid_logs_requesttrace()
        table_var = rtrace.select('^').to_table_var("TestVar")

        self.assertEqual(hash(table_var), table_var.self_time.source_table_hash())
