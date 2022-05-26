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

from sklearn.metrics import get_scorer

from ibm_watson_machine_learning import APIClient
from ibm_watson_machine_learning.experiment import AutoAI
from ibm_watson_machine_learning.experiment.autoai.optimizers import RemoteAutoPipelines
from ibm_watson_machine_learning.helpers.connections import DataConnection
from ibm_watson_machine_learning.tests.utils import get_space_id, get_wml_credentials, get_cos_credentials
from ibm_watson_machine_learning.tests.utils.assertions import validate_autoai_experiment
from ibm_watson_machine_learning.tests.utils.cleanup import space_cleanup
from ibm_watson_machine_learning.utils.autoai.errors import WMLClientError

from ibm_watson_machine_learning.utils.autoai.enums import PredictionType, Metrics, ClassificationAlgorithms, \
    BatchedClassificationAlgorithms


tests_params = [(e[1], a) for e in enumerate(list(BatchedClassificationAlgorithms)[:-1]) \
     for a in list(BatchedClassificationAlgorithms)[e[0]+1:]]


class TestAutoAIRemote(unittest.TestCase):
    """
    The test can be run on CPD only
    """

    bucket_name = environ.get('BUCKET_NAME', "wml-autoaitests-qa")
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

    cos_resource = None
    data_location = './autoai/data/make_class_header.csv'

    data_cos_path = 'data/make_class_header.csv'

    SPACE_ONLY = False

    OPTIMIZER_NAME = "make_class_header test sdk"

    target_space_id = None
    df = None
    experiment_info = dict(
        name=OPTIMIZER_NAME,
        prediction_type=PredictionType.BINARY,
        prediction_column='class',
        scoring=Metrics.ROC_AUC_SCORE,
        max_number_of_estimators=1,
        autoai_pod_version='!>dev-incremental_learning-7',  # TODO to be removed
        include_only_estimators=["SnapRandomForestClassifier", "XGBClassifier", "LogisticRegression",
                                 "DecisionTreeClassifier"],
        include_batched_ensemble_estimators=["BatchedTreeEnsembleClassifier(SnapRandomForestClassifier)",
                                             "BatchedTreeEnsembleClassifier(XGBClassifier)"]
        #use_flight=True
    )

    pipeline_model = None
    data_loader = None

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

    def test_00d_prepare_data_asset(self):
        asset_details = self.wml_client.data_assets.create(
            name=self.data_location.split('/')[-1],
            file_path=self.data_location)

        TestAutoAIRemote.asset_id = self.wml_client.data_assets.get_id(asset_details)
        self.assertIsInstance(self.asset_id, str)

    def test_01_initialize_AutoAI_experiment__pass_credentials__object_initialized(self):

        if self.SPACE_ONLY:
            TestAutoAIRemote.experiment = AutoAI(wml_credentials=self.wml_credentials.copy(),
                                                        space_id=self.space_id)
        else:
            TestAutoAIRemote.experiment = AutoAI(wml_credentials=self.wml_credentials.copy(),
                                                        project_id=self.project_id)

        self.assertIsInstance(self.experiment, AutoAI, msg="Experiment is not of type AutoAI.")

    def test_02_data_reference_setup(self):
        TestAutoAIRemote.data_connection = DataConnection(data_asset_id=self.asset_id)
        TestAutoAIRemote.results_connection = None

        self.assertIsNotNone(obj=TestAutoAIRemote.data_connection)
        self.assertIsNone(obj=TestAutoAIRemote.results_connection)

    # def test_10_summary_listing_all_pipelines_from_wml(self):
    #     TestAutoAIRemote.summary = self.remote_auto_pipelines.summary()
    #     print(TestAutoAIRemote.summary)
    #     self.assertIn('Ensemble', TestAutoAIRemote.summary.Enhancements['Pipeline_5'])
    #
    # def test_90_partial_fit_BatchedTreeEnsmblePipeline(self):
    #     TestAutoAIRemote.pipeline_model = self.remote_auto_pipelines.get_pipeline('Pipeline_5', astype='lale')
    #     estimator = self.pipeline_model.steps[-1][1]
    #     pipeline_model = self.pipeline_model.remove_last().freeze_trained() >> estimator
    #     scorer = get_scorer(TestAutoAIRemote.experiment_info['scoring'])
    #
    #     for i in range(3):
    #         pipeline_model = pipeline_model.partial_fit(self.X_values, self.y_values, classes=[0, 1])
    #         print('score: ', scorer(pipeline_model, self.X_values, self.y_values))
    #
    # def test_91_data_loader(self):
    #     from ibm_watson_machine_learning.data_loaders import experiment as data_loaders
    #     from ibm_watson_machine_learning.data_loaders.datasets import experiment as datasets
    #
    #     TestAutoAIRemote.experiment_info['project_id'] = self.wml_credentials['project_id']
    #
    #     dataset = datasets.ExperimentIterableDataset(
    #         connection=self.data_connection,
    #         with_subsampling=False,
    #         experiment_metadata=self.experiment_info,
    #         _wml_client=self.wml_client
    #     )
    #
    #     TestAutoAIRemote.data_loader = data_loaders.ExperimentDataLoader(dataset=dataset)
    #
    # def test_92_partial_fit(self):
    #     from sklearn.metrics import get_scorer
    #
    #     scorer = get_scorer(self.experiment_info['scoring'])
    #
    #     from lale.lib.lale import Batching
    #
    #     TestAutoAIRemote.experiment_info['classes'] = [0, 1]
    #
    #     X_train_first_10 = None
    #
    #     for batch_df in self.data_loader:
    #         print(batch_df.shape)
    #         X_train = batch_df.drop([self.experiment_info['prediction_column']], axis=1).values
    #         y_train = batch_df[self.experiment_info['prediction_column']].values
    #         if not X_train_first_10:
    #             X_train_first_10 = X_train[:10]
    #         pipeline_model = self.pipeline_model.partial_fit(X_train, y_train, classes=self.experiment_info['classes'],
    #                                                     freeze_trained_prefix=True)
    #         print('score: ', scorer(pipeline_model, X_train, y_train))
    #
    #     self.pipeline_model.predict(X_train_first_10)
    #
    # def test_99_delete_data_asset(self):
    #     if not self.SPACE_ONLY:
    #         self.wml_client.set.default_project(self.project_id)
    #
    #     self.wml_client.data_assets.delete(self.asset_id)
    #
    #     with self.assertRaises(WMLClientError):
    #         self.wml_client.data_assets.get_details(self.asset_id)

    def test_estimator_pairs(self):
        for estimators in tests_params:
            with self.subTest(msg=f"Estimators: {estimators[0].name} and {estimators[1].name}"):
                experiment_info = self.experiment_info.copy()
                experiment_info['include_batched_ensemble_estimators'] = estimators
                experiment_info['include_only_estimators'] = [e.value.split('(')[1][:-1] for e in estimators]

                experiment_info = validate_autoai_experiment(experiment_info, self.pod_version)

                TestAutoAIRemote.remote_auto_pipelines = self.experiment.optimizer(
                    **experiment_info)

                self.assertIsInstance(self.remote_auto_pipelines, RemoteAutoPipelines,
                                      msg="experiment.optimizer did not return RemoteAutoPipelines object")

                parameters = self.remote_auto_pipelines.get_params()
                print(parameters)

                # TODO: params validation
                self.assertIsInstance(parameters, dict, msg='Config parameters are not a dictionary instance.')

                TestAutoAIRemote.trained_pipeline_details = self.remote_auto_pipelines.fit(
                    training_data_reference=[self.data_connection],
                    training_results_reference=self.results_connection,
                    background_mode=False)

                TestAutoAIRemote.run_id = self.trained_pipeline_details['metadata']['id']
                self.assertIsNotNone(self.data_connection.auto_pipeline_params,
                                     msg='DataConnection auto_pipeline_params was not updated.')

                print(self.trained_pipeline_details)
                self.assertTrue('batch_ensemble_output' in str(self.trained_pipeline_details))

                TestAutoAIRemote.train_data = self.remote_auto_pipelines.get_data_connections()[0].read()

                print("train data sample:")
                print(self.train_data.head())
                self.assertGreater(len(self.train_data), 0)

                TestAutoAIRemote.X_df = self.train_data.drop([self.experiment_info['prediction_column']],
                                                                    axis=1)[
                                               :10]
                TestAutoAIRemote.X_values = TestAutoAIRemote.X_df.values
                TestAutoAIRemote.y_values = self.train_data[self.experiment_info['prediction_column']][:10]

                predictions = self.remote_auto_pipelines.predict(X=self.X_values)
                print(predictions)
                self.assertGreater(len(predictions), 0)
