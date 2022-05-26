import numpy as np
import pandas as pd
import pytest

from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import (
    DuplicateLabelTypeMismatch,
    InsufficientUniqueLabels,
    MalformedLabelColumn,
    MissingLabelColumn,
    MixedMultilabelTypes,
    UnexpectedLabelFormat
)
from azureml.automl.dnn.nlp.validation.multilabel_validator import NLPMultilabelDataValidator


@pytest.fixture
def get_labels_in_old_format():
    labels = [
        'a',
        '1',
        'b,c',
        '2',
        ''
    ]
    train_labels = pd.DataFrame({"label": labels})
    valid_labels = pd.DataFrame({"label": labels})
    return train_labels, valid_labels


def _get_rich_text_df():
    return pd.DataFrame(
        {"input_text_col": np.repeat(np.array(["I tried to catch some fog. I mist.",  # These were found online.
                                               "When chemists die, they barium.",
                                               "I'm reading a book about anti-gravity and I can't put it down.",
                                               "I did a theatrical performance about puns. It was a play on words.",
                                               "The report said I had type A blood, but it was a type O."]), 20),
         "another_input_text_col":
             np.repeat(np.array(["While it would be more fun to come up with these puns personally,",
                                 "that's probably not the best use of my time at work.",
                                 "So instead I have sourced them from Googl--Bing. :)",
                                 "Just need two more lines...",
                                 "Yes, yes, there we go."]), 20)})


def test_malformed_label_column():
    train_data = _get_rich_text_df()
    train_data["labels"] = np.repeat(np.array(["[]; print('Did somebody say security?')",
                                               "import sys  # dangerous"]), 50)
    validator = NLPMultilabelDataValidator()
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=None)
    assert exc.value.error_code == MalformedLabelColumn.__name__

    valid_data = train_data.copy()
    valid_data["labels"] = np.repeat(np.array(["['lbl1', 'lbl2']",
                                               "['lbl1']"]), 50)  # Valid label column.
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=valid_data)
    assert exc.value.error_code == MalformedLabelColumn.__name__

    with pytest.raises(DataException) as exc:
        train_data, valid_data = valid_data, train_data
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=valid_data)
    assert exc.value.error_code == MalformedLabelColumn.__name__


def test_unexpected_label_format():
    train_data = _get_rich_text_df()
    train_data["labels"] = np.repeat(np.array(["['valid_label', 'another_valid_label']",
                                               "'invalid_label'"]), 50)
    validator = NLPMultilabelDataValidator()
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=None)
    assert exc.value.error_code == UnexpectedLabelFormat.__name__

    valid_data = _get_rich_text_df()
    valid_data["labels"] = np.repeat(np.array(["['valid_label', 'another_valid_label']",
                                               "['valid_label']"]), 50)
    train_data, valid_data = valid_data, train_data  # Train correct, valid is not.
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=valid_data)
    assert exc.value.error_code == UnexpectedLabelFormat.__name__


def test_all_examples_single_label_succeeds():
    train_data = _get_rich_text_df()
    train_data["labels"] = np.repeat(np.array(["['valid_label']",
                                               "['another_valid_label']"]), 50)
    validator = NLPMultilabelDataValidator()
    validator.validate(label_col_name="labels",
                       train_data=train_data, valid_data=None)  # Does not fail.


def test_check_label_types_happy_path():
    label_lists = np.array([list(('valid_label', 2)),
                            list((1,))])
    validator = NLPMultilabelDataValidator()
    int_set, str_set = validator._check_label_types(label_lists=label_lists)
    assert int_set == {'1', '2'}
    assert str_set == {'valid_label'}


def test_mixed_multilabel_types():
    train_data = _get_rich_text_df()
    train_data["labels"] = np.repeat(np.array(["['valid_label']",
                                               "['valid_label', 3.14]"]), 50)
    validator = NLPMultilabelDataValidator()
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=None)
    assert exc.value.error_code == MixedMultilabelTypes.__name__

    valid_data = train_data.copy()
    valid_data["labels"] = np.repeat(np.array(["['valid_label']",
                                               "['valid_label', 23]"]), 50)
    train_data, valid_data = valid_data, train_data
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=valid_data)
    assert exc.value.error_code == MixedMultilabelTypes.__name__


def test_check_eval_label_column_happy_path():
    train_data = _get_rich_text_df()
    train_data["labels"] = np.repeat(np.array(["['lbl1', 'lbl2']",
                                               "['lbl1']"]), 50)
    validator = NLPMultilabelDataValidator()
    labels = validator._check_eval_label_column(data=train_data,
                                                label_col_name="labels",
                                                data_source="")
    np.testing.assert_array_equal(np.repeat(np.array([list(('lbl1', 'lbl2')), list(('lbl1',))]), 50),
                                  labels)


def test_insufficient_unique_train_labels():
    train_data = _get_rich_text_df()
    train_data["labels"] = np.array(["[1]"] * 100)
    validator = NLPMultilabelDataValidator()

    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=None)
    assert exc.value.error_code == InsufficientUniqueLabels.__name__

    valid_data = _get_rich_text_df()
    valid_data["labels"] = np.array(["[1]", "[1, 2]"] * 50)

    # We require label diversity in the *training* set
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=valid_data)
    assert exc.value.error_code == InsufficientUniqueLabels.__name__

    train_data, valid_data = valid_data, train_data
    validator.validate(label_col_name="labels",
                       train_data=train_data, valid_data=valid_data)  # no error now.


def test_duplicate_label_type_mismatch():
    train_data = _get_rich_text_df()
    train_data["labels"] = np.repeat(np.array(["[1]",
                                               "['valid_label', '1']"]), 50)
    validator = NLPMultilabelDataValidator()

    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=None)
    assert exc.value.error_code == DuplicateLabelTypeMismatch.__name__

    valid_data = _get_rich_text_df()
    valid_data["labels"] = np.repeat(np.array(["['valid_label', 1]", "[1]"]), 50)
    train_data, valid_data = valid_data, train_data

    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=valid_data)
    assert exc.value.error_code == DuplicateLabelTypeMismatch.__name__

    valid_data["labels"] = np.repeat(np.array(["['1']", "['valid_label', '1']"]), 50)

    # Individually, the datasets are okay, but together they are not as they introduce an inconsistency.
    validator.validate(label_col_name="labels", train_data=train_data, valid_data=None)
    validator.validate(label_col_name="labels", train_data=valid_data, valid_data=None)
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels",
                           train_data=train_data, valid_data=valid_data)
    assert exc.value.error_code == DuplicateLabelTypeMismatch.__name__


def test_support_for_old_format():
    good_data = _get_rich_text_df()
    good_data["labels"] = np.repeat(np.array(["1", "1,2", "2", "2,3", "3"]), 20)

    bad_data = good_data.copy()
    bad_data["labels"] = np.repeat(np.arange(5), 20)

    validator = NLPMultilabelDataValidator()
    validator.validate(label_col_name="labels", train_data=good_data, valid_data=None)

    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels", train_data=bad_data, valid_data=None)
    assert exc.value.error_code == MalformedLabelColumn.__name__

    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels", train_data=bad_data, valid_data=good_data)
    assert exc.value.error_code == MalformedLabelColumn.__name__

    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels", train_data=good_data, valid_data=bad_data)
    assert exc.value.error_code == MalformedLabelColumn.__name__

    validator.validate(label_col_name="labels", train_data=good_data, valid_data=good_data)


def test_validator_drops_nan_rows():
    data = pd.DataFrame({"input_text_col": np.repeat(np.array(["Sphinx of black quartz",
                                                               "Judge my vow!",
                                                               "A quick brown fox jumped over ",
                                                               "the lazy dog?",
                                                               "No way!"]), 13),
                         "labels": np.repeat(np.array(["['Cool', 'Very Cool']", "['Cool']",
                                                       "['Cool', 'Very Cool']", "['Cool']", None]), 13)})
    valid_data = data.copy()

    validator = NLPMultilabelDataValidator()
    assert data.shape[0] == 65
    validator.validate(label_col_name="labels", train_data=data, valid_data=None)
    assert data.shape[0] == 52

    assert valid_data.shape[0] == 65
    validator.validate(label_col_name="labels", train_data=data, valid_data=valid_data)
    assert valid_data.shape[0] == 52


def test_validator_catches_bad_label_types():
    good_data = pd.DataFrame({"input_text_col": np.repeat(np.array(["Eeny", "Meeny", "Miny", "Moe", "You!"]), 10),
                              "labels": np.repeat(np.array(["[2]", "[1]", "[1, 2]", "[]", "[3]"]), 10)})
    bad_data = good_data.copy()
    bad_data["labels"] = np.repeat(np.arange(5), 10)  # Data that is not indexable.

    validator = NLPMultilabelDataValidator()
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels", train_data=bad_data, valid_data=None)
    assert exc.value.error_code == MalformedLabelColumn.__name__

    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels", train_data=good_data, valid_data=bad_data)


def test_validator_catches_empty_vocabulary_issues():
    good_data = pd.DataFrame({"input_text_col": np.repeat(np.array(list("Hello")), 10),
                              "labels": np.repeat(np.array(["[2]", "[1]", "[1, 2]", "[]", "[3]"]), 10)})
    bad_data = good_data.copy()
    bad_data["labels"] = np.array([""] * 50)

    validator = NLPMultilabelDataValidator()
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels", train_data=bad_data, valid_data=None)
    assert exc.value.error_code == MalformedLabelColumn.__name__

    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="labels", train_data=good_data, valid_data=bad_data)
    assert exc.value.error_code == MalformedLabelColumn.__name__


def test_multilabel_bad_label_column_name():
    data = pd.DataFrame({"input_col": np.repeat(np.array(["Sphinx of black quartz, judge my vow",
                                                          "A quick brown fox jumps over the lazy dog",
                                                          "The above examples are called pangrams",
                                                          "A pangram uses every letter of the alphabet",
                                                          "Isn't that neat?"]), 10),
                         "label_col": np.repeat(np.array(["['hello', 'world']"]), 50)})
    validator = NLPMultilabelDataValidator()
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="Bad value",
                           train_data=data,
                           valid_data=None)
    assert exc.value.error_code == MissingLabelColumn.__name__


def test_multilabel_only_first_row_correct():
    data = pd.DataFrame({"input_text_col": np.repeat(np.array(["This is a sentence.",
                                                               "Is this a question?",
                                                               "a fragment",
                                                               "This is a clause, and this is also a clause",
                                                               "word"]), 10),
                         "label_col": np.concatenate((np.array(["['Nicely formatted label']"]), np.arange(49)))})
    validator = NLPMultilabelDataValidator()
    with pytest.raises(DataException) as exc:
        validator.validate(label_col_name="label_col",
                           train_data=data,
                           valid_data=None)
    assert exc.value.error_code == UnexpectedLabelFormat.__name__
