from unittest.mock import patch, mock_open

import pytest

from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import (
    ConsecutiveBlankNERLines,
    EmptyFileBeginning,
    EmptyFileEnding,
    EmptyTokenNER,
    InsufficientExamples,
    MalformedNERLabels,
    MalformedNERLine
)
from azureml.automl.dnn.nlp.validation.ner_validator import NLPNERDataValidator


def multi_file_mock_opener(*file_contents):
    mock_files = [mock_open(read_data=content).return_value for content in file_contents]
    mock_opener = mock_open()
    mock_opener.side_effect = mock_files
    return mock_opener


def test_empty_file_beginning():
    samples = ["token1sample1 B-label\ntoken2sample1 I-label\n",
               "token1sample2 B-label\ntoken2sample2 I-label\ntoken3sample2 O\n"] * 25
    content = '\n'.join(samples)
    validator = NLPNERDataValidator()
    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=mock_open(read_data='\n' + content)):
            validator.validate(dir="", train_file="train", valid_file=None)
    assert exc.value.error_code == EmptyFileBeginning.__name__

    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=multi_file_mock_opener(content, '\n' + content)):
            validator.validate(dir="", train_file="train", valid_file="valid")
    assert exc.value.error_code == EmptyFileBeginning.__name__


def test_optional_docstart_does_not_error():
    content = '\n'.join(["token1sample1 B-label\n", "token1sample2 I-label\n"] * 25)
    validator = NLPNERDataValidator()
    for data in [content, "-DOCSTART- O\n\n" + content]:
        with patch("builtins.open", new=mock_open(read_data=data)):
            validator.validate(dir="", train_file="train", valid_file=None)  # passes just fine.


def test_consecutive_blank_lines():
    samples = ["token1sample1 B-label\ntoken2sample1 I-label\n",
               "token1sample2 B-label\ntoken2sample2 I-label\ntoken3sample2 O\n"] * 25
    samples[25] += '\n'  # Introduce extra new line in some middle sample.
    content = '\n'.join(samples)

    validator = NLPNERDataValidator()
    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=mock_open(read_data=content)):
            validator.validate(dir="", train_file="train", valid_file=None)
    assert exc.value.error_code == ConsecutiveBlankNERLines.__name__

    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=multi_file_mock_opener('\n'.join(samples[:10] * 5), content)):
            validator.validate(dir="", train_file="train", valid_file="valid")
    assert exc.value.error_code == ConsecutiveBlankNERLines.__name__


def test_empty_file_ending():
    samples = ["token1sample1 B-label\ntoken2sample1 I-label\n",
               "token1sample2 B-label\ntoken2sample2 I-label\ntoken3sample2 O\n"] * 25
    content = '\n'.join(samples)

    validator = NLPNERDataValidator()
    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=mock_open(read_data=content + '\n')):
            validator.validate(dir="", train_file="train", valid_file=None)
    assert exc.value.error_code == EmptyFileEnding.__name__

    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=multi_file_mock_opener(content, content + '\n')):
            validator.validate(dir="", train_file="train", valid_file="valid")
    assert exc.value.error_code == EmptyFileEnding.__name__


def test_insufficient_ner_examples():
    samples = ["token1sample1 B-label\ntoken2sample1 I-label\n",
               "token1sample2 B-label\ntoken2sample2 I-label\ntoken3sample2 O\n"]

    validator = NLPNERDataValidator()
    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=mock_open(read_data='\n'.join(samples * 24))):
            validator.validate(dir="", train_file="train", valid_file=None)
    assert exc.value.error_code == InsufficientExamples.__name__

    with patch("builtins.open", new=multi_file_mock_opener('\n'.join(samples * 25),
                                                           '\n'.join(samples * 24))):
        validator.validate(dir="", train_file="train", valid_file="valid")  # passes fine.


def test_malformed_ner_line():
    validator = NLPNERDataValidator()
    with pytest.raises(DataException) as exc:
        validator._check_line_format(line="token  I-label", split="train")
    assert exc.value.error_code == MalformedNERLine.__name__

    content = "token1sample1 B-label\ntoken2sample1  I-label"
    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=mock_open(read_data=content)):
            validator.validate(dir="", train_file="train", valid_file=None)
    assert exc.value.error_code == MalformedNERLine.__name__

    samples = ["token1sample1 B-label\ntoken2sample1 I-label\n",
               "token1sample2 B-label\ntoken2sample2 I-label\ntoken3sample2 O\n"] * 25
    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=multi_file_mock_opener('\n'.join(samples), content)):
            validator.validate(dir="", train_file="train", valid_file="valid")
    assert exc.value.error_code == MalformedNERLine.__name__


def test_empty_ner_token():
    validator = NLPNERDataValidator()
    with pytest.raises(DataException) as exc:
        validator._check_line_format(line=" I-label", split="train")
    assert exc.value.error_code == EmptyTokenNER.__name__

    content = "token1sample1 B-label\n I-label\n"
    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=mock_open(read_data=content)):
            validator.validate(dir="", train_file="train", valid_file=None)
    assert exc.value.error_code == EmptyTokenNER.__name__

    samples = ["token1sample1 B-label\n", "token1sample2 O\n"] * 25
    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=multi_file_mock_opener('\n'.join(samples), content)):
            validator.validate(dir="", train_file="train", valid_file="valid")
    assert exc.value.error_code == EmptyTokenNER.__name__


def test_malformed_ner_label():
    validator = NLPNERDataValidator()
    with pytest.raises(DataException) as exc:
        validator._check_line_format(line="token N-label", split="train")
    assert exc.value.error_code == MalformedNERLabels.__name__

    with pytest.raises(DataException) as exc:
        validator._check_line_format(line="token O-label", split="train")
    assert exc.value.error_code == MalformedNERLabels.__name__

    with pytest.raises(DataException) as exc:
        validator._check_line_format(line="token ", split="train")
    assert exc.value.error_code == MalformedNERLabels.__name__

    content = "token1sample1 label"
    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=mock_open(read_data=content)):
            validator.validate(dir="", train_file="train", valid_file=None)
    assert exc.value.error_code == MalformedNERLabels.__name__

    samples = ["token1sample1 B-label\n", "token1sample2 O\n"] * 25
    with pytest.raises(DataException) as exc:
        with patch("builtins.open", new=multi_file_mock_opener('\n'.join(samples), content)):
            validator.validate(dir="", train_file="train", valid_file="valid")
    assert exc.value.error_code == MalformedNERLabels.__name__
