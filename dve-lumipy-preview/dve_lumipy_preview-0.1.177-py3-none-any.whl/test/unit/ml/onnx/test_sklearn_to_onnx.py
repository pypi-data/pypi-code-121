import unittest

import numpy as np
import pandas as pd
import sklearn.datasets as datasets
from onnxruntime import InferenceSession
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.svm import SVC

import lumipy.ml as ml


class TestSklearnToOnnx(unittest.TestCase):

    def setUp(self):
        # Iris classification
        iris_data = datasets.load_iris(as_frame=True)
        iris_df = pd.concat([iris_data['data'], iris_data['target']], axis=1)
        self.iris_train, self.iris_test = train_test_split(iris_df, test_size=0.3, random_state=0)

        # California Housing Regression
        cali_data = datasets.fetch_california_housing(as_frame=True)
        cali_df = pd.concat([cali_data['data'], cali_data['target']], axis=1)
        self.cali_train, self.cali_test = train_test_split(cali_df, test_size=0.3, random_state=0)

        # Titanic Survival Classification
        titanic_data = datasets.fetch_openml("titanic", version=1, as_frame=True)
        titanic_df = pd.concat([titanic_data['data'], titanic_data['target']], axis=1)
        titanic_df['sex'] = titanic_df.sex.astype(str)
        titanic_df['embarked'] = titanic_df.embarked.astype(str)
        titanic_df['pclass'] = titanic_df.pclass.astype(str)
        titanic_df['survived'] = titanic_df.survived.astype(int)
        titanic_df['age'] = titanic_df.age.astype(np.float32)
        titanic_df['fare'] = titanic_df.fare.astype(np.float32)
        self.titanic_train, self.titanic_test = train_test_split(titanic_df, test_size=0.3, random_state=0)

    def test_convert_single_classifier(self):
        x_train, y_train = self.iris_train.iloc[:, :-1], self.iris_train.iloc[:, -1]

        clf = SVC(probability=True)
        clf.fit(x_train, y_train)

        onnx_model = ml.sklearn_to_onnx(clf, x_train)

        sess = InferenceSession(onnx_model.SerializeToString())

        self.assertEqual(len(sess.get_inputs()), 1)
        self.assertEqual(sess.get_inputs()[0].name, 'input_tensor')
        self.assertEqual(len(sess.get_outputs()), 2)
        for output in sess.get_outputs():
            if output.name == 'label':
                self.assertEqual(tuple(output.shape), (None,))
            elif output.name == 'probabilities':
                self.assertEqual(tuple(output.shape), (None, 3))
            else:
                raise ValueError(f"Unrecognised output tensor: {output.name}")

        x_test, y_test = self.iris_test.iloc[:, :-1], self.iris_test.iloc[:, -1]
        onnx_labels, onnx_probs = sess.run(
            ['label', 'probabilities'],
            {'input_tensor': x_test.values.astype(np.float32)}
        )
        skl_labels = clf.predict(x_test)
        skl_probs = clf.predict_proba(x_test)

        self.assertEqual(np.abs(onnx_labels-skl_labels).sum(), 0)
        self.assertAlmostEqual(np.abs(onnx_probs-skl_probs).mean(), 0, 6)

    def test_convert_single_regressor(self):
        x_train, y_train = self.cali_train.iloc[:, :-1], self.cali_train.iloc[:, -1]

        clf = RandomForestRegressor(n_estimators=10)
        clf.fit(x_train, y_train)

        onnx_model = ml.sklearn_to_onnx(clf, x_train)

        sess = InferenceSession(onnx_model.SerializeToString())

        self.assertEqual(len(sess.get_inputs()), 1)
        self.assertEqual(sess.get_inputs()[0].name, 'input_tensor')
        self.assertEqual(len(sess.get_outputs()), 1)
        for output in sess.get_outputs():
            if output.name == 'variable':
                self.assertEqual(tuple(output.shape), (None, 1))
            else:
                raise ValueError(f"Unrecognised output tensor: {output.name}")

        x_test, y_test = self.cali_test.iloc[:, :-1], self.cali_test.iloc[:, -1]
        onnx_vals = sess.run(
            ['variable'],
            {'input_tensor': x_test.values.astype(np.float32)}
        )[0].flatten()
        skl_vals = clf.predict(x_test)

        self.assertAlmostEqual(np.abs(onnx_vals-skl_vals).mean(), 0, 6)

    def test_convert_single_transform(self):
        x_train, y_train = self.iris_train.iloc[:, :-1], self.iris_train.iloc[:, -1]

        prepro = StandardScaler()
        prepro.fit(x_train)

        onnx_model = ml.sklearn_to_onnx(prepro, x_train)

        sess = InferenceSession(onnx_model.SerializeToString())

        self.assertEqual(len(sess.get_inputs()), 1)
        self.assertEqual(sess.get_inputs()[0].name, 'input_tensor')
        self.assertEqual(len(sess.get_outputs()), 1)
        for output in sess.get_outputs():
            if output.name == 'variable':
                self.assertEqual(tuple(output.shape), (None, 4))
            else:
                raise ValueError(f"Unrecognised output tensor: {output.name}")

        x_test, y_test = self.iris_test.iloc[:, :-1], self.iris_test.iloc[:, -1]
        onnx_vals = sess.run(
            ['variable'],
            {'input_tensor': x_test.values.astype(np.float32)}
        )[0]
        skl_vals = prepro.transform(x_test)

        self.assertAlmostEqual(np.abs(onnx_vals - skl_vals).mean(), 0, 6)

    def test_convert_pipeline_with_heterogeneous_features(self):

        x_train, y_train = self.titanic_train.iloc[:, :-1], self.titanic_train.iloc[:, -1]

        numeric_features = ['age', 'fare']
        numeric_transformer = Pipeline(
            steps=[
                ('imputer', SimpleImputer()),
                ('scaler', StandardScaler())
            ]
        )

        categorical_features = ['embarked', 'sex', 'pclass']
        categorical_transformer = Pipeline(
            steps=[
                ('onehot', OneHotEncoder(handle_unknown='ignore'))
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ('numeric', numeric_transformer, numeric_features),
                ('categorical', categorical_transformer, categorical_features)
            ]
        )

        pipe = Pipeline(
            steps=[
                ('preprocessor', preprocessor),
                ('pca', PCA()),
                ('classifier', LogisticRegressionCV())
            ]
        )

        pipe = pipe.fit(x_train, y_train)

        onnx_model = ml.sklearn_to_onnx(pipe, x_train)

        sess = InferenceSession(onnx_model.SerializeToString())

        targets = ['pclass', 'sex', 'age', 'fare', 'embarked']

        # Check the input ordering is attached as custom metadata
        custom_meta = sess.get_modelmeta().custom_metadata_map
        ordering = [int(custom_meta[f"{t}_index"]) for t in targets]
        self.assertEqual(tuple(ordering), (0, 1, 2, 3, 4))

        self.assertEqual(len(sess.get_inputs()), 5)
        self.assertEqual(len(sess.get_outputs()), 2)
        for in_tensor, target in zip(sess.get_inputs(), targets):
            self.assertEqual(in_tensor.name, target)
        for output in sess.get_outputs():
            if output.name == 'label':
                self.assertEqual(tuple(output.shape), (None,))
            elif output.name == 'probabilities':
                self.assertEqual(tuple(output.shape), (None, 2))
            else:
                raise ValueError(f"Unrecognised output tensor: {output.name}")

        x_test, y_test = self.titanic_test.iloc[:, :-1], self.titanic_test.iloc[:, -1]
        input_tensors = {t: x_test[t].values.reshape(-1, 1) for t in targets}
        onnx_labels, onnx_probs = sess.run(
            ['label', 'probabilities'],
            input_tensors
        )
        skl_labels = pipe.predict(x_test)
        skl_probs = pipe.predict_proba(x_test)

        self.assertEqual(np.abs(onnx_labels-skl_labels).sum(), 0)
        self.assertAlmostEqual(np.abs(onnx_probs-skl_probs).mean(), 0, 6)
