from __future__ import annotations
from sk_general import modeling as modeling_utils
from typing import Type
from sklearn import dummy


import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
import pytest




class TestModelInterface:

    def test_model_load_with_class(self) -> None:
        model = modeling_utils.Model(model_class=dummy.DummyRegressor, instantiate=True)
        assert isinstance(model.model_object, dummy.DummyRegressor)

    def test_model_load_with_object(self) -> None:
        model = modeling_utils.Model(model_object=dummy.DummyRegressor())
        assert isinstance(model.model_object, dummy.DummyRegressor)

    def test_model_instantiation(self) -> None:
        model = modeling_utils.Model(model_class=dummy.DummyRegressor, instantiate=False)
        model.instantiate()
        assert isinstance(model.model_object, dummy.DummyRegressor)

    def test_model_instantiation_with_kwargs(self) -> None:
        model = modeling_utils.Model(
            model_class=dummy.DummyRegressor,
            instantiate=True,
            model_params={"strategy": "mean"},
        )
        assert model.model_object.strategy == "mean"
    
    def test_model_instantiation_with_init_params(self) -> None:
        model = modeling_utils.Model(
            model_class=dummy.DummyRegressor,
            instantiate=True,
            strategy="mean",
        )
        assert model.model_object.strategy == "mean"
            
    @pytest.mark.skip(reason="Not implemented")
    def test_model_train():
        model = modeling_utils.Model(model_class=dummy.DummyRegressor, instantiate=True, )
        model.train(X_train=pd.DataFrame({"a": [1, 2, 3]}), y_train=pd.Series([1, 2, 3]))
        assert isinstance(model.model_object, dummy.DummyRegressor)

dummy.DummyRegressor().fit()

# def test_inheritance():
#     class TestFitter:
#         def fit(self, X, y, **kwargs):
#             ...

#     class TestPredictor:
#         def predict(self, X, **kwargs):
#             ...

#     class TestModel(TestFitter, TestPredictor):
#         ...

#     assert not issubclass(TestFitter, modeling_utils.AbstractGenericModel)
#     assert not issubclass(TestPredictor, modeling_utils.AbstractGenericModel)
#     assert issubclass(TestModel, modeling_utils.AbstractGenericModel)

# def test_target_model():
#     class TestFitter:
#         def fit(self, X, y, **kwargs):
#             ...

#     class TestPredictor:
#         def predict(self, X, **kwargs):
#             ...

#     class TestModel(TestFitter, TestPredictor):
#         ...

#     test_target_model = modeling_utils.TargetModel(TestModel, "target")
#     test_data = pd.DataFrame({"target": [1, 2, 3], "col1": [1, 2, 3]})
#     test_X, test_y = test_target_model.get_Xy_from_data(test_data)
#     expected_X = pd.DataFrame({"col1": [1, 2, 3]})
#     expected_y = pd.Series([1, 2, 3], name="target")
#     assert_frame_equal(test_X, expected_X)
#     assert_series_equal(test_y, expected_y)
