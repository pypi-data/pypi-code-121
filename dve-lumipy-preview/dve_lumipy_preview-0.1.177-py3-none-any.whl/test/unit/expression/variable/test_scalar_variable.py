import unittest

from lumipy.query.expression.sql_value_type import SqlValType
from lumipy.query.expression.variable.base_variable import BaseVariable
from test.unit.utilities.test_utils import make_test_atlas
from datetime import datetime
from decimal import Decimal


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


class TestScalarVariable(unittest.TestCase):

    def test_scalar_at_var_creation_source_col(self):

        atlas = make_test_atlas()
        for cls in atlas.list_providers():

            if cls.get_provider_type() != 'DataProvider':
                continue

            param_input = generate_params_input(cls)

            # Given a table
            inst = cls(**param_input)

            # Given a source column
            for col in inst.get_columns():

                # When we select just this column and create a scalar variable
                scalar_table = inst.select(col)
                scalar = scalar_table.to_scalar_var("test")

                # Then it should be a subclass of BaseVariable
                self.assertTrue(issubclass(type(scalar), BaseVariable))
                # Then it should have a sql string that's its name with the @@ prefix
                self.assertEqual(scalar.get_sql(), '@@test')
                # Then the definition of the variable in the assignment string should equal the @@name = (table sql)
                flat1 = ' '.join(scalar.get_assignment_sql().split())
                flat2 = ' '.join(f'@@test = {scalar_table.get_sql()};'.split())
                self.assertEqual(flat1, flat2)
                # Then the type of the scalar should match the column it was derived from
                self.assertEqual(scalar.get_type(), col.get_type())

    def test_scalar_at_var_creation_derived_col(self):

        atlas = make_test_atlas()
        for provider in atlas.list_providers():

            if provider.get_provider_type() != 'DataProvider':
                continue

            param_input = generate_params_input(provider)

            inst = provider(**param_input)

            # Test a derived column expression (multiply by 2)
            from lumipy.query.expression.sql_value_type import numerics
            for col in inst.get_columns():

                if col.get_type() not in numerics:
                    continue

                scalar_table = inst.select(doubled=col*2)
                scalar = scalar_table.to_scalar_var("test")

                self.assertTrue(issubclass(type(scalar), BaseVariable))
                self.assertEqual(scalar.get_sql(), '@@test')
                flat1 = ' '.join(scalar.get_assignment_sql().split())
                flat2 = ' '.join(f'@@test = {scalar_table.get_sql()};'.split())
                self.assertEqual(flat1, flat2)

    def test_scalar_at_var_creation_aggregate_col(self):

        atlas = make_test_atlas()
        for provider_description in atlas.list_providers():

            if provider_description.get_provider_type() != 'DataProvider':
                continue

            param_input = generate_params_input(provider_description)

            inst = provider_description(**param_input)

            # Test an aggregate column expression (count)
            for col in inst.get_columns():

                scalar_table = inst.select(ColCount=col.count())
                scalar = scalar_table.to_scalar_var("test")

                self.assertTrue(issubclass(type(scalar), BaseVariable))
                self.assertEqual(scalar.get_sql(), '@@test')
                flat1 = ' '.join(scalar.get_assignment_sql().split())
                flat2 = ' '.join(f'@@test = {scalar_table.get_sql()};'.split())
                self.assertEqual(flat1, flat2)

    def test_scalar_at_var_creation_error(self):

        atlas = make_test_atlas()
        for cls in atlas.list_providers():

            if cls.get_provider_type() != 'DataProvider':
                continue

            param_input = generate_params_input(cls)

            inst = cls(**param_input).select('*')
            if len(inst.get_columns()) < 2:
                continue
            if len(inst.get_columns()) != 1:
                with self.assertRaises(ValueError):
                    inst.to_scalar_var("test")

    def test_scalar_at_var_creation_with_aliased_column(self):

        atlas = make_test_atlas()
        for cls in atlas.list_providers():

            if cls.get_provider_type() != 'DataProvider':
                continue

            param_input = generate_params_input(cls)

            # Given a table
            inst = cls(**param_input)

            # Given a source column
            for col in inst.get_columns():
                # When we select just this column with an alias and create a scalar variable
                scalar_table = inst.select(col.with_alias("TestAlias"))
                scalar = scalar_table.to_scalar_var("test")

                # Then it should be a subclass of BaseVariable
                self.assertTrue(issubclass(type(scalar), BaseVariable))
                # Then it should have a sql string that's its name with the @@ prefix
                self.assertEqual(scalar.get_sql(), '@@test')
                # Then the definition of the variable in the assignment string should equal the @@name = (table sql)
                flat1 = ' '.join(scalar.get_assignment_sql().split())
                flat2 = ' '.join(f'@@test = {scalar_table.get_sql()};'.split())
                self.assertEqual(flat1, flat2)

    def test_scalar_at_var_creation_from_join_columns(self):

        # Given two data providers
        atlas = make_test_atlas()
        app_req = atlas.lusid_logs_apprequest()
        rtrace = atlas.lusid_logs_requesttrace()

        # When they're joined, a single column is selected, and scalar var is derived from the result
        join = app_req.inner_join(
            rtrace,
            on=app_req.request_id == rtrace.request_id
        ).select(SelfTimeSum=rtrace.self_time.sum())
        scalar = join.to_scalar_var("TotalSelfTime")

        # Then it should be a subclass of BaseVariable
        self.assertTrue(issubclass(type(scalar), BaseVariable))
        # Then it should have a sql string that's its name with the @@ prefix
        self.assertEqual(scalar.get_sql(), '@@TotalSelfTime')
        # Then the definition of the variable in the assignment string should equal the @@name = (table sql)
        flat1 = ' '.join(scalar.get_assignment_sql().split())
        flat2 = ' '.join(f'@@TotalSelfTime = {join.get_sql()};'.split())
        self.assertEqual(flat1, flat2)

    def test_scalar_at_var_creation_error_protected_names(self):

        atlas = make_test_atlas()
        app_req = atlas.lusid_logs_apprequest()
        with self.assertRaises(ValueError):
            app_req.select(app_req.duration).to_scalar_var('from')

    def test_scalar_at_var_from_table_at_var(self):

        atlas = make_test_atlas()
        app_req = atlas.lusid_logs_apprequest()
        table_var = app_req.select('^').where(
            app_req.duration > 1000
        ).to_table_var("TestVar")

        scalar = table_var.select(
            MeanDuration=table_var.duration.mean()
        ).to_scalar_var("MeanDuration")
        self.assertEqual(len(scalar._at_var_dependencies), 1)
        self.assertTrue(list(scalar._at_var_dependencies)[0].hash_equals(table_var))

    def test_date_scalar(self):
        from lumipy import date_now

        start = date_now(-2)
        end = date_now(-1)

        atlas = make_test_atlas()
        qry = atlas.lusid_logs_apprequest(
            start_at=start,
            end_at=end
        ).select('^')

        qry_sql = qry.get_sql()

        self.assertIn("date('now', '-2 days');", qry_sql)
        self.assertIn("date('now', '-1 days');", qry_sql)
        self.assertEqual(qry_sql.count('@@'), 4)

    def test_scalar_in_select(self):

        atlas = make_test_atlas()
        app_req = atlas.lusid_logs_apprequest()
        sv = app_req.select(mu=app_req.duration.mean()).to_scalar_var()
        qry = app_req.select(scalar=sv)
