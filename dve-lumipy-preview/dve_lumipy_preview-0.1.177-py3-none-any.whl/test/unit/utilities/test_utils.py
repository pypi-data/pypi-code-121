from lumipy.atlas.atlas import Atlas
from lumipy.atlas.utility_functions import _build_data_provider_factories, _build_direct_provider_factories
import pandas as pd
import os
import json
from test.unit.utilities.temp_file_manager import TempFileManager

from lumipy.client import Client
import inspect


def get_atlas_test_data():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = file_dir + '/../../data/'
    data_df = pd.read_csv(test_data_dir + 'data_meta.csv').sort_values('FieldName')
    direct_df = pd.read_csv(test_data_dir + 'direct_meta.csv')
    direct_df['BodyStrNames'] = direct_df.BodyStrNames.apply(lambda x: [s.replace("'", '') for s in x[1:-1].split(',') if s != ''])
    return data_df, direct_df


def make_test_atlas():

    data_df, direct_df = get_atlas_test_data()

    sample_secrets = {
        "api": {
            "tokenUrl": "sample",
            "username": "sample",
            "password": "sample",
            "clientId": "sample",
            "clientSecret": "sample",
            "apiUrl": "sample",
            "lumiApiUrl": "sample"
        }
    }

    secrets_file = TempFileManager.create_temp_file(sample_secrets)

    client = Client(api_secrets_filename=secrets_file.name)

    data_p_factories = _build_data_provider_factories(data_df, client)
    direct_p_factories = _build_direct_provider_factories(direct_df, client)

    TempFileManager.delete_temp_file(secrets_file)

    return Atlas(
        data_p_factories + direct_p_factories,
        atlas_type='All available data providers'
    )


def assert_locked_lockable(test_case, instance):

    from lumipy.common.lockable import Lockable
    test_case.assertTrue(issubclass(type(instance), Lockable))

    with test_case.assertRaises(TypeError) as ar:
        instance.new_attribute = 'some new attribute'
    e = str(ar.exception)

    str1 = "Can't change attributes on "
    str2 = "they are immutable."
    test_case.assertTrue(str1 in e)
    test_case.assertTrue(str2 in e)

    test_case.assertFalse(hasattr(instance, 'new_attribute'))


def standardise_sql_string(sql_str):
    return " ".join(sql_str.split())


def load_secrets_into_env_if_local_run():

    if 'LOCAL_INT_TEST_SECRETS_PATH' in os.environ:
        path = os.environ['LOCAL_INT_TEST_SECRETS_PATH']
        print(f'Loading secrets from {path}')
        env_var_map = {
            'lumiApiUrl': 'FBN_LUMI_API_URL',
            'tokenUrl': 'FBN_TOKEN_URL',
            'username': 'FBN_USERNAME',
            'password': 'FBN_PASSWORD',
            'clientId': 'FBN_CLIENT_ID',
            'clientSecret': 'FBN_CLIENT_SECRET'
        }

        os.environ['FBN_LUSID_DRIVE_URL'] = 'https://fbn-ci.lusid.com/drive/'
        with open(path, 'r') as f:
            creds = json.load(f)['api']
            for k1, k2 in env_var_map.items():
                os.environ[k2] = creds[k1]


def test_prefix_insertion(test_case, table, expression):

    aliased_table = table.with_alias('test')

    prefixed = aliased_table.apply_prefix(expression)

    observed_sql = prefixed.get_sql()
    expected_sql = expression.get_sql()

    for c in set(expression.get_col_dependencies()):
        expected_sql = expected_sql.replace(c.get_sql(), 'test.'+c.get_sql())

    test_case.assertEqual(
        standardise_sql_string(observed_sql),
        standardise_sql_string(expected_sql)
    )


def check_class_docstrings_in_module(test_case, module):

    def is_lumipy_cls(m):
        return hasattr(m[1], '__module__') \
               and m[1].__module__.startswith(module.__name__) \
               and inspect.isclass(m[1])

    classes = filter(is_lumipy_cls, inspect.getmembers(module))

    for cls_name, cls in classes:

        docstrings = {a: getattr(cls, a).__doc__ for a in dir(cls)}
        missing_docstrs = [
            a for a, d in docstrings.items()
            if d is None and (not a.startswith('_') or a == '__doc__')
        ]
        missing_strs = "\n  ".join(missing_docstrs)
        test_case.assertEqual(
            len(missing_docstrs), 0,
            msg=f"Documentation check failed for {cls.__name__}."
                f"\nMissing docstrings for"
                f"\n  {missing_strs}"
        )
