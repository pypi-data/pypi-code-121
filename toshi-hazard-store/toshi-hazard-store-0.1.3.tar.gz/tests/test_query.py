import unittest

from moto import mock_dynamodb
from toshi_hazard_store import model, query
import itertools

TOSHI_ID = 'FAk3T0sHi1D=='
vs30s = [250, 350, 450]
imts = ['PGA', 'SA(0.5)']
locs = ['WLG', 'QZN']
stats = ['mean', 'quantile-0.1']
rlzs = [f"rlz-00{x}" for x in range(5)]
lvps = list(map(lambda x: model.LevelValuePairAttribute(level=x / 1e3, value=(x / 1e6)), range(1, 51)))


def build_stats_models():
    for (vs30, imt, loc, stat) in itertools.product(vs30s, imts, locs, stats):
        yield model.ToshiOpenquakeHazardCurveStats(
            vs30=vs30, location_code=loc, imt_code=imt, aggregation=stat, lvl_val_pairs=lvps
        )


def build_rlzs_models():
    for (vs30, imt, loc, rlz) in itertools.product(vs30s, imts, locs, rlzs):
        yield model.ToshiOpenquakeHazardCurveRlzs(
            vs30=vs30, location_code=loc, imt_code=imt, rlz_id=rlz, lvl_val_pairs=lvps
        )


@mock_dynamodb
class QueryModuleTest(unittest.TestCase):
    def setUp(self):

        model.migrate()
        super(QueryModuleTest, self).setUp()

    def tearDown(self):
        model.drop_tables()
        return super(QueryModuleTest, self).tearDown()

    def test_batch_save_stats_objects(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveStats.exists(), True)

        query.batch_save_hcurve_stats(TOSHI_ID, models=build_stats_models())
        saved = model.ToshiOpenquakeHazardCurveStats.query(TOSHI_ID)

        self.assertEqual(len(list(saved)), len(list(build_stats_models())))

    def test_batch_save_realizations_objects(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveRlzs.exists(), True)

        query.batch_save_hcurve_rlzs(TOSHI_ID, models=build_rlzs_models())
        saved = model.ToshiOpenquakeHazardCurveRlzs.query(TOSHI_ID)

        self.assertEqual(len(list(saved)), len(list(build_rlzs_models())))

    def test_query_stats_objects(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveStats.exists(), True)
        query.batch_save_hcurve_stats(TOSHI_ID, models=build_stats_models())
        res = list(query.get_hazard_curves_stats(TOSHI_ID, 350, 'PGA', ['WLG'], None))
        print(stats)
        self.assertEqual(len(res), len(stats))
        self.assertEqual(res[0].location_code, 'WLG')
        self.assertEqual(res[0].aggregation, 'mean')
        self.assertEqual(res[1].aggregation, 'quantile-0.1')

    def test_query_stats_objects_2(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveStats.exists(), True)
        query.batch_save_hcurve_stats(TOSHI_ID, models=build_stats_models())
        res = list(query.get_hazard_curves_stats(TOSHI_ID, 350, 'PGA', ['WLG', 'QZN'], None))
        print(stats)
        self.assertEqual(len(res), len(stats) * 2)
        self.assertEqual(res[0].location_code, 'QZN')
        self.assertEqual(res[2].location_code, 'WLG')
        self.assertEqual(res[0].aggregation, 'mean')
        self.assertEqual(res[1].aggregation, 'quantile-0.1')

    def test_query_stats_objects_3(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveStats.exists(), True)
        query.batch_save_hcurve_stats(TOSHI_ID, models=build_stats_models())
        res = list(query.get_hazard_curves_stats(TOSHI_ID, 350, 'PGA', None, None))
        print(res)
        self.assertEqual(len(res), len(stats) * len(locs))

    def test_query_stats_objects_4(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveStats.exists(), True)
        query.batch_save_hcurve_stats(TOSHI_ID, models=build_stats_models())
        res = list(query.get_hazard_curves_stats(TOSHI_ID, 350, 'PGA', ['WLG', 'QZN'], ['mean']))
        print(res)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].location_code, 'QZN')
        self.assertEqual(res[1].location_code, 'WLG')
        self.assertEqual(res[0].aggregation, 'mean')
        self.assertEqual(res[1].aggregation, 'mean')
