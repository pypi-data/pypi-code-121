import numpy as np
import pandas as pd
import pytest

from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import (
    InsufficientExamples, InsufficientUniqueLabels, MissingLabelColumn
)
from azureml.automl.dnn.nlp.common.constants import ValidationLiterals
from azureml.automl.dnn.nlp.validation.multiclass_validator import NLPMulticlassDataValidator


class TestDataValidation:
    def test_multiclass_insufficient_unique_labels(self):
        good_data = pd.DataFrame({"input_text_col": np.repeat(np.array(["First", "Second!", "Third",
                                                                        "Fourth", "Fifth"]), 10),
                                  "labels": np.repeat(np.arange(5), 10)})
        bad_data = good_data.copy()
        bad_data["labels"] = np.ones((50,))

        validator = NLPMulticlassDataValidator()
        with pytest.raises(DataException) as exc:
            validator.validate(label_col_name="labels", train_data=bad_data, valid_data=None)
        assert exc.value.error_code == InsufficientUniqueLabels.__name__

        with pytest.raises(DataException) as exc:
            validator.validate(label_col_name="labels", train_data=bad_data, valid_data=good_data)
        assert exc.value.error_code == InsufficientUniqueLabels.__name__

        # Only care about train label diversity.
        validator.validate(label_col_name="labels", train_data=good_data, valid_data=bad_data)

    def test_multiclass_bad_label_column_name(self):
        data = pd.DataFrame({"input_col": np.repeat(np.array(["Sphinx of black quartz, judge my vow",
                                                              "A quick brown fox jumps over the lazy dog",
                                                              "The above examples are caled pangrams",
                                                              "A pangram uses every letter of the alphabet",
                                                              "Isn't that neat?"]), 10),
                             "label_col": np.random.randint(0, 5, (50,))})
        validator = NLPMulticlassDataValidator()
        with pytest.raises(DataException) as exc:
            validator.validate(label_col_name="Bad value",
                               train_data=data,
                               valid_data=None)
        assert exc.value.error_code == MissingLabelColumn.__name__

    def test_multiclass_too_many_nan_labels_causes_insufficient_examples(self):
        data = pd.DataFrame({"input_col": np.repeat(np.array(["Anthurium Clarinervium",
                                                              "Anthurium Crystallinum",
                                                              "Anthurium Magnificum",
                                                              "Anthurium Warocqueanum",
                                                              "Anthurium Forgetii"]), 10),
                             "labels": np.repeat(np.array(["$$$", "$$", "$$", "$$$$", None]), 10)})
        good_data = data.copy()
        good_data["labels"] = np.repeat(np.array(["$$$", "$$", "$$", "$$$$", "$$"]), 10)

        assert data.shape[0] >= ValidationLiterals.MIN_TRAINING_SAMPLE  # We meet the minimum threshold.

        validator = NLPMulticlassDataValidator()
        with pytest.raises(DataException) as exc:
            validator.validate(label_col_name="labels", train_data=data.copy(), valid_data=None)
        assert exc.value.error_code == InsufficientExamples.__name__

        # Okay if validation dataset falls below threshold.
        validator.validate(label_col_name="labels", train_data=good_data, valid_data=data)
        assert data.shape[0] < ValidationLiterals.MIN_TRAINING_SAMPLE
