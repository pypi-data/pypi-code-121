import numpy as np
import pandas as pd
import pytest

from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import (
    ColumnOrderingMismatch,
    ColumnSetMismatch,
    ColumnTypeMismatch,
    DuplicateColumnNames
)
from azureml.automl.dnn.nlp.validation.multilabel_validator import NLPMultilabelDataValidator
from azureml.automl.dnn.nlp.validation.multiclass_validator import NLPMulticlassDataValidator


def test_duplicate_column_names():
    good_data = pd.DataFrame({"col": np.repeat(np.array(["Philodendron Gloriosum",
                                                         "Philodendron El Choco",
                                                         "Philodendron Nanegalense"]), 20),
                              "col2": np.repeat(np.array(["Anthurium Clarinervium",
                                                          "Anthurium Crystallinum",
                                                          "Anthurium Forgetii"]), 20),
                              "labels": np.repeat(np.array(["Best", "Cool", "Cool"]), 20)})
    bad_data = good_data.copy()
    bad_data.rename(columns={"col": "Plants", "col2": "Plants"}, inplace=True)

    for validator_class in [NLPMulticlassDataValidator, NLPMultilabelDataValidator]:
        validator = validator_class()
        with pytest.raises(DataException) as exc:
            validator.validate(label_col_name="labels", train_data=bad_data, valid_data=None)
        assert exc.value.error_code == DuplicateColumnNames.__name__

        with pytest.raises(DataException) as exc:
            validator.validate(label_col_name="labels", train_data=good_data, valid_data=bad_data)
        assert exc.value.error_code == DuplicateColumnNames.__name__


def test_column_set_mismatch():
    train_data = pd.DataFrame({"bird": np.repeat(np.array(["Willow Ptarmigan",
                                                           "California quail",
                                                           "Mountain bluebird",
                                                           "Willow goldfinch",
                                                           "Hermit thrush"]), 10),
                               "state": np.repeat(np.array(["Alaska",
                                                            "California",
                                                            "Idaho",
                                                            "Washington",
                                                            "Vermont"]), 10)})
    valid_data = train_data.rename(columns={"bird": "animal"})

    for validator_class in [NLPMulticlassDataValidator, NLPMultilabelDataValidator]:
        validator = validator_class()
        with pytest.raises(DataException) as exc:
            validator.validate(label_col_name="state", train_data=train_data, valid_data=valid_data)
        assert exc.value.error_code == ColumnSetMismatch.__name__


def test_column_ordering_mismatch():
    train_data = pd.DataFrame({1: np.repeat(np.arange(5), 10).astype(str),
                               2: np.repeat(np.arange(5), 10).astype(str),
                               "labels": np.repeat(np.arange(5), 10)}).reindex(columns=[1, 2, "labels"])
    valid_data = train_data.reindex(columns=[2, 1, "labels"])

    for validator_class in [NLPMulticlassDataValidator, NLPMultilabelDataValidator]:
        validator = validator_class()
        with pytest.raises(DataException) as exc:
            validator.validate(label_col_name="labels", train_data=train_data, valid_data=valid_data)
        assert exc.value.error_code == ColumnOrderingMismatch.__name__


def test_column_type_mismatch():
    train_data = pd.DataFrame({1: np.repeat(np.arange(5), 10),
                               2: np.repeat(np.arange(5), 10),
                               "labels": np.repeat(np.arange(5), 10)})
    valid_data = train_data.copy()
    valid_data[1] = valid_data[1].astype(object)

    for validator_class in [NLPMulticlassDataValidator, NLPMultilabelDataValidator]:
        validator = validator_class()
        with pytest.raises(DataException) as exc:
            validator.validate(label_col_name="labels", train_data=train_data, valid_data=valid_data)
        assert exc.value.error_code == ColumnTypeMismatch.__name__
