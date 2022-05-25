import builtins
import json
import sys
import os
from unittest.mock import patch, mock_open
import pandas as pd
import pytest
from azureml.automl.dnn.nlp.common._utils import save_deploy_script

df = pd.DataFrame({"text": ["this is a test"], "label": [["3"]]})
save_deploy_script("score_nlp_ner_v2.txt",
                   "\"This\\nis\\nan\\nexample\"",
                   "\"This O\\nis O\\nan O\\n example B-OBJ\"",
                   "StandardPythonParameterType",
                   os.path.join(".", "score_ner.py"))

sys.path.append(os.getcwd())


class MockModel:

    def __init__(self):
        pass

    def predict(self, data):
        return "this label0\nis label1\nan label1\nexample label0"


def test_init():
    import score_ner as score

    mocked_file = mock_open()

    with patch("os.getenv", return_value="some_dir"):
        with patch.object(builtins, 'open', mocked_file, create=True):
            with patch("pickle.load", return_value="mocked_model"):
                score.init()

    assert mocked_file.call_count == 1
    assert score.model == "mocked_model"


def test_score():
    import score_ner as score

    mock_model = MockModel()
    data = "this is an example"
    score.model = mock_model
    result = score.run({"data": data})

    assert result["Results"] == "this label0\nis label1\nan label1\nexample label0"


def test_score_raises_error_bad_model():
    import score_ner as score

    mock_model = "bad model that fails prediction"
    data = "this is an example"
    score.model = mock_model

    with pytest.raises(BaseException):
        json.loads(score.run({"data": data}))
