import unittest
from datetime import datetime, timedelta

from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string


class TestAtVariables(unittest.TestCase):

    def test_scalar_var_and_table_var_together(self):

        atlas = make_test_atlas()
        prior_24hrs = atlas.lusid_logs_apprequest(
            start_at=datetime.utcnow() - timedelta(hours=48),
            end_at=datetime.utcnow() - timedelta(hours=24)
        )

        duration_group_by = prior_24hrs.select(
            '*'
        ).where(
            (prior_24hrs.event_type != 'started') &
            (prior_24hrs.method != '')
        ).group_by(
            prior_24hrs.method,
            prior_24hrs.application
        ).aggregate(
            SumDuration=prior_24hrs.duration.sum()
        )
        self.assertEqual(len(duration_group_by._group_columns), 2)
        self.assertEqual(len(duration_group_by.get_columns()), len(prior_24hrs.get_columns())+1)

        duration_groups = duration_group_by.to_table_var("DurationGroups")
        self.assertEqual(len(duration_groups.get_columns()), len(prior_24hrs.get_columns())+1)

        total_duration = duration_groups.select(
            total_duration=duration_groups.sum_duration.sum()
        ).to_scalar_var("TotalDuration")

        source_table_hash = hash(duration_groups)
        self.assertEqual(source_table_hash, duration_groups.method.source_table_hash())

        qry = duration_groups.select(
            duration_groups.method,
            duration_groups.application,
            duration_groups.sum_duration,
            total_duration=total_duration,
            frac_duration=duration_groups.sum_duration/total_duration
        )
        self.assertEqual(
            len(qry.get_columns()),
            5
        )

        sql = qry.get_sql()
        self.assertIn(
            standardise_sql_string("@@TotalDuration = SELECT total([SumDuration]) AS [total_duration] FROM @DurationGroups;"),
            standardise_sql_string(sql)
        )

        # Check at var dependency resolution is working:
        # -- Content and type of at_var_dependencies is correct
        deps = qry._at_var_dependencies
        self.assertEqual(
            type(deps), list,
            msg=f'@/@@ variable dependency storage in expression (at_var_dependencies) '
                f'should be a list. Was {type(deps).__name__}.'
        )
        self.assertEqual(
            len(deps),
            2,
            msg=f'@/@@ number of at var dependencies is incorrect. Expect 2 was {len(deps)}.'
        )

        # -- Ordering: @DurationGroups should be above @@TotalDuration because the latter depends on the former
        lines = [" ".join(line.split()[:2]) for line in qry.get_sql().split('\n') if len(line) > 0]
        dg_ind = lines.index('@DurationGroups =')
        td_ind = lines.index('@@TotalDuration =')
        self.assertGreater(td_ind, dg_ind, msg='@/@@ variable dependency resolution has failed.')

