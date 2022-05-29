import itertools
import unittest

from moto import mock_dynamodb

from toshi_hazard_store import model, query

TOSHI_ID = 'FAk3T0sHi1D=='
# vs30s = [250, 350, 450]
imts = ['PGA', 'SA(0.5)']
locs = ['WLG', 'QZN']
rlzs = [f"rlz-00{x}" for x in range(5)]
lvps = list(map(lambda x: model.LevelValuePairAttribute(lvl=x / 1e3, val=(x / 1e6)), range(1, 51)))


def build_rlzs_models():
    for (imt, loc, rlz) in itertools.product(imts, locs, rlzs):
        yield model.ToshiOpenquakeHazardCurveRlzs(loc=loc, imt=imt, rlz=rlz, values=lvps)


@mock_dynamodb
class QueryRlzsTest(unittest.TestCase):
    def setUp(self):

        model.migrate()
        super(QueryRlzsTest, self).setUp()

    def tearDown(self):
        model.drop_tables()
        return super(QueryRlzsTest, self).tearDown()

    def test_batch_save_realizations_objects(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveRlzs.exists(), True)
        query.batch_save_hcurve_rlzs(TOSHI_ID, models=build_rlzs_models())
        saved = model.ToshiOpenquakeHazardCurveRlzs.query(TOSHI_ID)
        self.assertEqual(len(list(saved)), len(list(build_rlzs_models())))

    def test_query_stats_objects(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveStats.exists(), True)
        query.batch_save_hcurve_rlzs(TOSHI_ID, models=build_rlzs_models())
        res = list(query.get_hazard_rlz_curves(TOSHI_ID, ['PGA'], ['WLG'], None))
        print(res)
        self.assertEqual(len(res), len(rlzs))
        self.assertEqual(res[0].loc, 'WLG')

    def test_query_stats_objects_2(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveStats.exists(), True)
        query.batch_save_hcurve_rlzs(TOSHI_ID, models=build_rlzs_models())
        res = list(query.get_hazard_rlz_curves(TOSHI_ID, ['PGA'], ['WLG', 'QZN'], None))
        print(res)
        self.assertEqual(len(res), len(rlzs) * 2)
        self.assertEqual(res[0].loc, 'QZN')
        self.assertEqual(res[len(rlzs)].loc, 'WLG')

    def test_query_stats_objects_3(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveStats.exists(), True)
        query.batch_save_hcurve_rlzs(TOSHI_ID, models=build_rlzs_models())
        res = list(query.get_hazard_rlz_curves(TOSHI_ID, ['PGA'], None, None))
        print(res)
        self.assertEqual(len(res), len(rlzs) * len(locs))

    def test_query_stats_objects_4(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveStats.exists(), True)
        query.batch_save_hcurve_rlzs(TOSHI_ID, models=build_rlzs_models())
        res = list(query.get_hazard_rlz_curves(TOSHI_ID, ['PGA'], ['WLG', 'QZN'], ['rlz-001']))
        print(res)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].loc, 'QZN')
        self.assertEqual(res[1].loc, 'WLG')
        self.assertEqual(res[0].rlz, 'rlz-001')

    def test_query_stats_objects_all(self):
        self.assertEqual(model.ToshiOpenquakeHazardCurveStats.exists(), True)
        query.batch_save_hcurve_rlzs(TOSHI_ID, models=build_rlzs_models())
        res = list(query.get_hazard_rlz_curves(TOSHI_ID))
        print(res)
        self.assertEqual(len(res), len(list(build_rlzs_models())))
        self.assertEqual(res[0].loc, 'QZN')
        # self.assertEqual(res[0].agg, 'mean')
