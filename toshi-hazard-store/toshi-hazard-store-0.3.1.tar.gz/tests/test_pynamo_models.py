import datetime as dt
import json
import unittest

from dateutil.tz import tzutc
from moto import mock_dynamodb

from toshi_hazard_store import model


@mock_dynamodb
class PynamoTest(unittest.TestCase):
    def setUp(self):

        # model.set_local_mode()
        # model.ToshiOpenquakeHazardCurveRlzs.create_table(wait=True)
        model.migrate()
        super(PynamoTest, self).setUp()

    def tearDown(self):
        model.drop_tables()
        return super(PynamoTest, self).tearDown()

    def test_table_exists(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveRlzs.exists(), True)

    def test_save_one_realization_object(self):

        lvps = list(map(lambda x: model.LevelValuePairAttribute(lvl=x / 1e3, val=(x / 1e6)), range(1, 51)))
        print(lvps)

        obj = model.ToshiOpenquakeHazardCurveRlzs(
            haz_sol_id="ABCDE",
            imt_loc_rlz_rk="350:PGA:WLG:rlz-010",
            loc="WLG",
            rlz="rlz-010",
            imt="PGA",
            values=lvps,
        )

        print(f'obj: {obj} {obj.version}')
        obj.save()
        print(f'obj: {obj} {obj.version}')
        print(dir(obj))

        self.assertEqual(obj.values[0].lvl, 0.001)
        self.assertEqual(obj.values[0].val, 0.000001)
        self.assertEqual(obj.values[9].lvl, 0.01)
        self.assertEqual(obj.values[9].val, 0.00001)

    def test_save_one_stats_object(self):

        lvps = list(map(lambda x: model.LevelValuePairAttribute(lvl=x / 1e3, val=(x / 1e6)), range(1, 51)))
        print(lvps)

        obj = model.ToshiOpenquakeHazardCurveStats(
            haz_sol_id="ABCDE",
            imt_loc_agg_rk="350:SA(0.5):WLG:quantile-0.1",
            loc="WLG",
            agg="quantile-0.1",
            imt="SA(0.5)",
            values=lvps,
        )

        print(f'obj: {obj} {obj.version}')
        self.assertEqual(obj.version, None)

        obj.save()
        self.assertEqual(obj.version, 1)
        print(dir(obj))

        self.assertEqual(obj.values[0].lvl, 0.001)
        self.assertEqual(obj.values[0].val, 0.000001)
        self.assertEqual(obj.values[9].lvl, 0.01)
        self.assertEqual(obj.values[9].val, 0.00001)

    def test_save_one_meta_object(self):

        obj = model.ToshiOpenquakeHazardMeta(
            partition_key="ToshiOpenquakeHazardMeta",
            haz_sol_id="AMCDEF",
            hazsol_vs30_rk="UnicodeAttribute(range_key=True)",
            updated=dt.datetime.now(tzutc()),
            # known at configuration
            vs30=350,  # vs30 value
            imts=['PGA', 'SA(0.5)'],  # list of IMTs
            locs=['WLG', 'AKL'],  # list of Location codes
            srcs=['A', 'B'],  # list of source model ids
            # extracted from the OQ HDF5
            src_lt=json.dumps(dict(sources=[1, 2])),  # sources meta as DataFrame JSON
            gsim_lt=json.dumps(dict(gsims=[1, 2])),  # gmpe meta as DataFrame JSON
            rlz_lt=json.dumps(dict(rlzs=[1, 2])),  # realization meta as DataFrame JSON
        )

        print(f'obj: {obj} {obj.version}')
        self.assertEqual(obj.version, None)

        obj.save()
        self.assertEqual(obj.version, 1)

        # self.assertEqual(obj.values[0].lvl, 0.001)
        # self.assertEqual(obj.values[0].val, 0.000001)
        # self.assertEqual(obj.values[9].lvl, 0.01)
        # self.assertEqual(obj.values[9].val, 0.00001)
