import unittest
from importlib.util import find_spec

import numpy as np
import pandas as pd
import sklearn.datasets as datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

import lumipy as lm
from test.integration.base_intergration_test import BaseIntegrationTest


class TestMLIntegration(BaseIntegrationTest):
    """Integration tests for ONNX file upload and serving in luminesce

    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.drive = lm.get_drive()

    @unittest.skipIf(find_spec('onnx') is None, "ONNX unavailable - this test is onnx-dependent.")
    def test_sklearn_workflow(self):

        import lumipy.ml as ml

        path = '/lumipy-int-tests/machine-learning-test/'
        try:
            # Enforce fresh start for test...
            self.drive.delete(path)
            self.drive.create_folder(path)
        except:
            self.drive.create_folder(path)

        # Get data
        iris_data = datasets.load_iris(as_frame=True)
        iris_df = pd.concat([iris_data['data'], iris_data['target']], axis=1)
        train, test = train_test_split(iris_df, test_size=0.3, random_state=0)
        # Upload test set df as csv
        test_set_path = path + 'iris_test.csv'
        self.drive.upload(test, test_set_path)
        # Assert test csv is there
        list_df = self.drive.list_files(path)
        self.assertEqual(list_df.shape[0], 1)

        # Train model, convert then upload
        x_train, y_train = train.iloc[:, :-1], train.iloc[:, -1]
        clf = SVC(probability=True)
        clf.fit(x_train, y_train)

        onnx_model = ml.sklearn_to_onnx(clf, x_train)
        onnx_path = path + 'test_onnx_model.onnx'
        self.drive.upload(onnx_model, onnx_path)
        list_df = self.drive.list_files(path)
        self.assertEqual(list_df.shape[0], 2)

        # Run inference in Luminesce
        cols_str = ', '.join(map(lambda x: f"[{x}]", x_train.columns))
        lumi_res = self.client.query_and_fetch(f"""
            @ch_data = use Drive.csv
                --file={test_set_path}
            enduse;

            @ch_features = select 
                {cols_str}
            from @ch_data;

            @inference = use Tools.ML.Inference.Sklearn with @ch_features
                --onnxFilePath={onnx_path}
            enduse;

            select * from @inference
        """)
        self.assertEqual(lumi_res.shape[0], test.shape[0])
        self.assertEqual(lumi_res.shape[1], 4)

        # Local inference
        x_test, y_test = test.iloc[:, :-1], test.iloc[:, -1]
        local_res = np.hstack([
            clf.predict(x_test).reshape(-1, 1),
            clf.predict_proba(x_test)
        ])

        diffs = local_res - lumi_res.values
        self.assertAlmostEqual(np.abs(diffs).mean(), 0.0, 7)

        # Clean up
        self.drive.delete(path)
