#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import unittest
from os import environ

from os.path import join

from ibm_watson_machine_learning import APIClient
from ibm_watson_machine_learning.helpers.connections import DataConnection, ContainerLocation
from ibm_watson_machine_learning.tests.utils.cleanup import space_cleanup
from ibm_watson_machine_learning.utils.autoai.errors import WMLClientError
from ibm_watson_machine_learning.tests.utils import create_connection_to_cos, get_wml_credentials, get_cos_credentials, \
    get_space_id

from ibm_watson_machine_learning.utils.autoai.enums import PredictionType


class TestAutoAIRemote(unittest.TestCase):
    """
    The test can be run on CLOUD, and CPD
    """

    ## beginning of base class vars

    bucket_name = environ.get('BUCKET_NAME', "wml-autoaitests-qa-lc")
    pod_version = environ.get('KB_VERSION', None)
    space_name = environ.get('SPACE_NAME', 'regression_tests_sdk_space')

    cos_endpoint = "https://s3.us.cloud-object-storage.appdomain.cloud"
    results_cos_path = 'results_wml_autoai'

    # to be set in every child class:
    OPTIMIZER_NAME = "AutoAI regression test"

    SPACE_ONLY = True
    HISTORICAL_RUNS_CHECK = True

    experiment_info = dict(name=OPTIMIZER_NAME,
                           desc='test description',
                           prediction_type=PredictionType.MULTICLASS,
                           prediction_column='species',
                           autoai_pod_version=pod_version
                           )

    wml_client: 'APIClient' = None
    experiment: 'AutoAI' = None
    remote_auto_pipelines: 'RemoteAutoPipelines' = None
    wml_credentials = None
    cos_credentials = None
    pipeline_opt: 'RemoteAutoPipelines' = None
    service: 'WebService' = None
    service_batch: 'Batch' = None

    cos_resource_instance_id = None
    experiment_info: dict = None

    trained_pipeline_details = None
    run_id = None
    prev_run_id = None
    data_connection = None
    results_connection = None
    train_data = None

    pipeline: 'Pipeline' = None
    lale_pipeline = None
    deployed_pipeline = None
    hyperopt_pipelines = None
    new_pipeline = None
    new_sklearn_pipeline = None
    X_df = None
    X_values = None
    y_values = None

    project_id = None
    space_id = None

    asset_id = None
    connection_id = None

    ## end of base class vars

    cos_resource = None
    file_names = ['autoai_exp_cfpb_Small.csv', 'height.xlsx', 'japanese_gb18030.csv']
    data_locations = [join('./autoai/data/read_issues', name) for name in file_names]
    data_cos_paths = [join('data', name) for name in file_names]

    SPACE_ONLY = True
    OPTIMIZER_NAME = "read issues"
    target_space_id = None
    connections_ids = []
    assets_ids = []
    data_connections = []
    results_connections = []

    #
    # experiment_info = dict(
    #     name=OPTIMIZER_NAME,
    #     desc='test description',
    #     prediction_type=PredictionType.REGRESSION,
    #     prediction_column='SalePrice',
    #     scoring=Metrics.MEAN_ABSOLUTE_ERROR,
    #     holdout_size=0.18,
    #     include_only_estimators=[RegressionAlgorithms.SnapBM,
    #                              RegressionAlgorithms.SnapRF,
    #                              RegressionAlgorithms.SnapDT],
    #     max_number_of_estimators=3,
    # )

    @classmethod
    def setUpClass(cls) -> None:
        """
        Load WML credentials from config.ini file based on ENV variable.
        """
        cls.wml_credentials = get_wml_credentials()
        cls.wml_client = APIClient(wml_credentials=cls.wml_credentials.copy())

        cls.cos_credentials = get_cos_credentials()
        cls.cos_endpoint = cls.cos_credentials.get('endpoint_url')
        cls.cos_resource_instance_id = cls.cos_credentials.get('resource_instance_id')

        cls.project_id = cls.wml_credentials.get('project_id')

    def test_00a_space_cleanup(self):
        space_checked = False
        while not space_checked:
            space_cleanup(self.wml_client,
                          get_space_id(self.wml_client, self.space_name,
                                       cos_resource_instance_id=self.cos_resource_instance_id),
                          days_old=7)
            space_id = get_space_id(self.wml_client, self.space_name,
                                    cos_resource_instance_id=self.cos_resource_instance_id)
            try:
                self.assertIsNotNone(space_id, msg="space_id is None")
                space_checked = True
            except AssertionError:
                space_checked = False

        TestAutoAIRemote.space_id = space_id

        if self.SPACE_ONLY:
            self.wml_client.set.default_space(self.space_id)
        else:
            self.wml_client.set.default_project(self.project_id)

    def test_00b_prepare_connection_to_COS(self):
        for location, cos_path in zip(self.data_locations, self.data_cos_paths):
            TestAutoAIRemote.connection_id, TestAutoAIRemote.bucket_name = create_connection_to_cos(
                wml_client=self.wml_client,
                cos_credentials=self.cos_credentials,
                cos_endpoint=self.cos_endpoint,
                bucket_name=self.bucket_name,
                save_data=True,
                data_path=location,
                data_cos_path=cos_path)

            self.connections_ids.append(TestAutoAIRemote.connection_id)

        self.assertIsInstance(self.connection_id, str)

    def test_00d_prepare_connected_data_asset(self):

        for connection_id, cos_path in zip(self.connections_ids, self.data_cos_paths):
            asset_details = self.wml_client.data_assets.store({
                self.wml_client.data_assets.ConfigurationMetaNames.CONNECTION_ID: connection_id,
                self.wml_client.data_assets.ConfigurationMetaNames.NAME: "training asset",
                self.wml_client.data_assets.ConfigurationMetaNames.DATA_CONTENT_NAME: join(self.bucket_name,
                                                                                           cos_path)
            })

            self.assets_ids.append(self.wml_client.data_assets.get_id(asset_details))

        self.assertEqual(len(self.assets_ids), 3)

    def test_02_data_reference_setup(self):

        for asset_id in self.assets_ids:
            self.data_connections.append(DataConnection(data_asset_id=asset_id))
            self.results_connections.append(DataConnection(
                location=ContainerLocation()
            ))

        self.assertEqual(len(self.data_connections), 3)
        self.assertEqual(len(self.results_connections), 3)

    def test_03a_get_train_data_autoai_exp_cfpb_Small(self):  # test data
        self.data_connections[0].set_client(self.wml_client)
        test_df = self.data_connections[0].read(use_flight=True)
        print(test_df.head())
        print(test_df.shape)
        self.assertEqual(test_df.shape, (5000, 2))

    @unittest.skip("Extra columns added by Flight issue https://github.ibm.com/wdp-gov/tracker/issues/86059")
    def test_03a_get_train_data_autoai_exp_cfpb_Small_Flight(self):  # test data
        self.data_connections[0].set_client(self.wml_client)
        test_df = self.data_connections[0].read(use_flight=True)
        print(test_df.head())
        print(test_df.shape)
        self.assertEqual(test_df.shape, (5000, 2))

    def test_03b_get_train_data_height(self):  # test data
        self.data_connections[1].set_client(self.wml_client)
        test_df = self.data_connections[1].read(use_flight=False)
        print(test_df.head())
        print(test_df.shape)
        self.assertEqual(test_df.shape, (199, 3))

    def test_03b_get_train_data_height_Flight(self):  # test data
        self.data_connections[1].set_client(self.wml_client)
        test_df = self.data_connections[1].read(use_flight=True, excel_sheet='height')
        print(test_df.head())
        print(test_df.shape)
        self.assertEqual(test_df.shape, (199, 3))

    def test_03c_get_train_data_japanese_gb18030(self):  # test data
        self.data_connections[2].set_client(self.wml_client)
        test_df =self.data_connections[2].read(use_flight=False, encoding='gb18030')
        print(test_df.head())
        target = u'温度'
        self.assertTrue(target in str(test_df.columns))

    def test_03d_get_train_data_japanese_gb18030_Flight(self):  # test data
        self.data_connections[2].set_client(self.wml_client)
        test_df =self.data_connections[2].read(use_flight=True)
        print(test_df.head())
        target = u'温度'
        self.assertTrue(target in str(test_df.columns))

    def test_99_delete_connection_and_connected_data_asset(self):
        for asset_id, connection_id in zip(self.assets_ids, self.connections_ids):
            self.wml_client.data_assets.delete(asset_id)
            self.wml_client.connections.delete(connection_id)

            with self.assertRaises(WMLClientError):
                self.wml_client.data_assets.get_details(asset_id)
                self.wml_client.connections.get_details(connection_id)


if __name__ == '__main__':
    unittest.main()
