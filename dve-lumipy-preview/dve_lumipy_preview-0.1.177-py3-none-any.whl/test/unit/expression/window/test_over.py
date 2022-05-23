import unittest
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string
from lumipy.query.expression.window.over import Over
from lumipy.query.expression.window.partition import WindowPartition
from lumipy.query.expression.window.order import WindowOrder
from lumipy.query.expression.window.frame import WindowFrame
from lumipy.query.expression.window.over import window


class TestOver(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.ar = self.atlas.lusid_logs_apprequest()

    def test_create_over_with_partition_order_and_frame(self):

        partition = WindowPartition(self.ar.application, self.ar.method)
        ordering = WindowOrder(self.ar.timestamp.ascending())
        frame = WindowFrame.create(None, 0)

        over = Over(partition, ordering, frame, None)
        sql = over.get_sql()

        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string(f'''OVER(
                {partition.get_sql()}
                {ordering.get_sql()}
                {frame.get_sql()}
                )''')
            )

    def test_create_over_with_order_and_frame(self):
        ordering = WindowOrder(self.ar.timestamp.ascending())
        frame = WindowFrame.create(None, 0)

        over = Over(None, ordering, frame, None)
        sql = over.get_sql()

        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string(f'''OVER(
                {ordering.get_sql()}
                {frame.get_sql()}
                )''')
        )

    def test_create_over_with_only_frame(self):

        frame = WindowFrame.create(None, 0)
        over = Over(None, None, frame, None)
        sql = over.get_sql()

        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string(f'''OVER(
                {frame.get_sql()}
                )''')
        )

    def test_create_filtered_over_with_only_frame(self):

        frame = WindowFrame.create(None, 0)
        over = Over(None, None, frame, None)
        cond = self.ar.duration > 100
        filtered_over = over.filter(cond)
        sql = filtered_over.get_sql()

        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string(f'FILTER(WHERE {cond.get_sql()}) {over.get_sql()}')
        )

    def test_create_composite_filtered_over_with_only_frame(self):

        frame = WindowFrame.create(None, 0)
        over = Over(None, None, frame, None)
        cond1 = self.ar.duration > 100
        cond2 = self.ar.application == 'lusid'
        cond = cond1 & cond2
        filtered_over = over.filter(cond1).filter(cond2)

        sql = filtered_over.get_sql()

        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string(f'FILTER(WHERE {cond.get_sql()}) {over.get_sql()}')
        )

    def test_create_with_defaults(self):
        win = window()

        sql = win.get_sql()
        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string('''OVER(
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )''')
        )

    def test_create_with_multi_partition_multi_ordering_and_frame_defaults(self):
        ar = self.ar
        win = window(
            groups=[ar.application, ar.method],
            orders=[ar.timestamp.ascending()],
        )

        sql = win.get_sql()
        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string('''OVER(
                PARTITION BY [Application], [Method]
                ORDER BY [Timestamp] ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )''')
        )

    def test_create_with_single_partition_single_ordering_and_frame_defaults(self):
        ar = self.ar
        win = window(
            groups=ar.application,
            orders=ar.timestamp.ascending(),
        )

        sql = win.get_sql()
        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string('''OVER(
                PARTITION BY [Application]
                ORDER BY [Timestamp] ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )''')
        )
