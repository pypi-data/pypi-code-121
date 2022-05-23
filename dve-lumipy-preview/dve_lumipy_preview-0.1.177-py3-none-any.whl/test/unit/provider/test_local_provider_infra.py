import unittest
import pandas as pd
from sklearn.datasets import load_iris, load_digits, load_diabetes
import lumipy.provider as lp
import requests as r
import datetime as dt
import pytz

from lumipy.query.expression.sql_value_type import SqlValType
import time


class TestLocalProviderInfra(unittest.TestCase):

    def setUp(self) -> None:

        def get_df_from_load_fn(load_fn):
            data = load_fn(as_frame=True)
            return pd.concat([data['data'], data['target']], axis=1)

        self.test_dfs = {
            "Test": pd.DataFrame([{"A": i, "B": i**2, "C": i**0.5} for i in range(25)]),
            "Iris": get_df_from_load_fn(load_iris),
            "Diabetes": get_df_from_load_fn(load_diabetes),
            "Digits": get_df_from_load_fn(load_digits),
        }

    def test_local_provider_creation(self):

        for name, df in self.test_dfs.items():

            prv = lp.PandasProvider(df, name)

            self.assertEqual(len(prv.parameters), 1)
            self.assertEqual(prv.name, f'Pandas.{name}')
            self.assertEqual(prv.path_name, f'pandas-{name.lower()}')
            self.assertEqual(prv.df.shape[0],  df.shape[0])
            self.assertEqual(prv.df.shape[1],  df.shape[1])
            self.assertEqual(len(prv.columns), df.shape[1])

            for c1, c2 in zip(sorted(prv.columns.keys()), sorted(df.columns)):
                col = prv.columns[c1]
                self.assertEqual(col.name, str(c2).replace('.', '_'))

    def test_manager_creation(self):

        providers = []
        for name, df in self.test_dfs.items():
            providers.append(lp.PandasProvider(df, name))

        manager = lp.ProviderManager(providers)

        prs = manager.provider_roots
        self.assertEqual(manager.host, 'localhost')
        self.assertEqual(manager.port, 5001)
        self.assertIsNotNone(manager.name)

        for pr in prs:
            name = pr['Name']
            url = pr['ApiPath']
            self.assertEqual(url, f'http://{manager.host}:{manager.port}/api/v1/{name.replace(".", "-").lower()}/')

        app = manager.app
        self.assertEqual(len(app.blueprints), len(manager.provider_roots))

    def test_manager_operation_bernoulli(self):

        # Tests that parameters can be supplied to a provider

        providers = [lp.BernoulliDistProvider()]

        host = 'localhost'
        port = 5004
        manager = lp.ProviderManager(providers, dry_run=True, host=host, port=port)

        with manager:
            # Test home page
            res = r.get(f'http://{host}:{port}')
            res.raise_for_status()

            # Test index endpoint
            res = r.get(f'http://{host}:{port}/api/v1/index')
            res.raise_for_status()
            index_json = res.json()
            self.assertEqual(len(index_json), 1)

            # Test provider metadata endpoint
            pr = manager.provider_roots[0]
            p = manager.providers[0]

            res = r.get(pr['ApiPath'] + 'metadata')
            res.raise_for_status()
            meta_json = res.json()
            self.assertEqual(len(meta_json['Columns']), len(p.columns))
            self.assertEqual(len(meta_json['Params']), len(p.parameters))
            self.assertEqual(meta_json['Name'], p.name)
            self.assertEqual(meta_json['Description'], p.description)

            # Test provider data endpoint
            res = r.post(pr['ApiPath'] + 'data', json={'params': [
                {'name': 'Probability', 'data_type': 'Double', 'value': 0.5},
                {'name': 'NumDraws', 'data_type': 'Int', 'value': 10000}
            ]})
            res.raise_for_status()
            data_json = res.json()
            self.assertEqual(len(data_json), 10000)
            self.assertTrue(all(len(row) == len(p.columns) for row in data_json))

            # Test that the manager has cleaned itself and its dependencies up
        with self.assertRaises(Exception) as e:
            res = r.get(f'http://{host}:{port}')
            res.raise_for_status()

    def test_manager_operation_pandas(self):

        time.sleep(3)

        providers = [lp.PandasProvider(df, name) for name, df in self.test_dfs.items()]

        host = 'localhost'
        port = 5006

        manager = lp.ProviderManager(providers, dry_run=True, host=host, port=port)

        with manager:

            # Test home page
            res = r.get(f'http://{host}:{port}')
            res.raise_for_status()

            # Test index endpoint
            res = r.get(f'http://{host}:{port}/api/v1/index')
            res.raise_for_status()
            index_json = res.json()
            self.assertEqual(len(index_json), len(manager.provider_roots))

            for p, pr in zip(providers, manager.provider_roots):

                # Test provider metadata endpoint
                res = r.get(pr['ApiPath']+'metadata')
                res.raise_for_status()
                meta_json = res.json()
                self.assertEqual(len(meta_json['Columns']), len(p.columns))
                self.assertEqual(len(meta_json['Params']), len(p.parameters))
                self.assertEqual(meta_json['Name'], p.name)
                self.assertEqual(meta_json['Description'], p.description)

                # Test provider data endpoint
                res = r.post(pr['ApiPath']+'data')
                res.raise_for_status()
                data_json = res.json()
                self.assertEqual(len(data_json), p.df.shape[0])
                self.assertTrue(all(len(row) == len(p.columns) for row in data_json))

        # Test that the manager has cleaned itself and its dependencies up
        with self.assertRaises(Exception) as e:
            res = r.get(f'http://{host}:{port}')
            res.raise_for_status()

    def test_pandas_provider_construction_with_datetimes(self):
        t = dt.datetime(2021, 7, 9)
        d = [{'A': k, 'T': t + dt.timedelta(days=i)} for i, k in enumerate('ABCDEFG')]
        df = pd.DataFrame(d)

        # non-tz-aware fails
        with self.assertRaises(ValueError) as ve:
            lp.PandasProvider(df, name='DatetimeTest')
            self.assertIn("Datetime values in pandas providers must be tz-aware", str(ve))
            self.assertIn("df['column'] = df['column'].dt.tz_localize(tz='utc')", str(ve))

        # tz-aware is fine and the col has the right type
        t = dt.datetime(2021, 7, 9, tzinfo=pytz.UTC)
        d = [{'A': k, 'T': t + dt.timedelta(days=i)} for i, k in enumerate('ABCDEFG')]
        df = pd.DataFrame(d)
        p = lp.PandasProvider(df, name='DatetimeTest')

        self.assertEqual(p.columns['A'].data_type, SqlValType.Text)
        self.assertEqual(p.columns['T'].data_type, SqlValType.DateTime)
