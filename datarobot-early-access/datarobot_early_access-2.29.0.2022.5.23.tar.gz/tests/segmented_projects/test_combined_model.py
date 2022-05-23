# -*- coding: utf-8 -*-
#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import json

import numpy as np
import pandas as pd
import pytest
import responses
import six
from trafaret import DataError

from datarobot.models.model import CombinedModel
from datarobot.models.project import Project
from tests.utils import add_response, request_body_to_json

_project_id = "projectId"
_target = "target"
_model_id = "modelId"
_base_url = "https://host_name.com/projects/{}/combinedModels/".format(_project_id)
_valid_combined_model_id = "validCombinedModelId"
_valid_active_combined_model_id = "validActiveCombinedModelId"
_invalid_combined_model_id = "validCombinedModelId"
_valid_combined_model_url = "{0}{1}/".format(_base_url, _valid_combined_model_id)
_invalid_combined_model_url = "{0}{1}/".format(_base_url, _invalid_combined_model_id)
_combined_model_segments_dl_url = "{0}{1}/segments/download/".format(
    _base_url, _valid_combined_model_id
)
_segment_champion_url = "https://host_name.com/projects/{}/segmentChampion/".format(_project_id)


@pytest.fixture
def combined_model_record():
    return {
        "combinedModelId": _valid_combined_model_id,
        "projectId": _project_id,
        "segmentationTaskId": "segmentationTaskId",
        "isActiveCombinedModel": False,
    }


@pytest.fixture
def active_combined_model_record():
    return {
        "combinedModelId": _valid_active_combined_model_id,
        "projectId": _project_id,
        "segmentationTaskId": "segmentationTaskId",
        "isActiveCombinedModel": True,
    }


@pytest.fixture
def combined_model_list_response(combined_model_record, active_combined_model_record):
    return {
        "count": 2,
        "next": None,
        "previous": None,
        "data": [combined_model_record, active_combined_model_record],
    }


@pytest.fixture
def combined_model_get_json(combined_model_record):
    return json.dumps(combined_model_record)


@pytest.fixture
def invalid_json():
    return json.dumps({"message": "Not Found"})


@pytest.fixture
def combined_model_list_json(combined_model_list_response):
    return json.dumps(combined_model_list_response)


@pytest.fixture
def mock_segment_csv():
    row_indexes = [u"row_{}".format(i) for i in range(10)]
    column_names = [u"カテゴリー_{}".format(i) for i in range(5)]
    rs = np.random.RandomState(1234)
    df = pd.DataFrame(
        data=rs.uniform(-1, 1, (len(row_indexes), len(column_names))),
        columns=column_names,
        index=row_indexes,
    )
    return df.to_csv(encoding="utf-8")


@responses.activate
def test_combined_model_list(combined_model_list_json):
    responses.add(
        responses.GET,
        _base_url,
        body=combined_model_list_json,
        status=200,
        content_type="application/json",
    )
    project = Project(id=_project_id)
    combined_models = project.get_combined_models()
    assert len(combined_models) == 2

    for combined_model in combined_models:
        assert isinstance(combined_model, CombinedModel)
        assert combined_model.project_id == _project_id
        assert combined_model.id in (_valid_combined_model_id, _valid_active_combined_model_id)
        if combined_model.id == _valid_combined_model_id:
            assert not combined_model.is_active_combined_model
        else:
            assert combined_model.is_active_combined_model


@responses.activate
def test_get_active_combined_model(combined_model_list_json):
    responses.add(
        responses.GET,
        _base_url,
        body=combined_model_list_json,
        status=200,
        content_type="application/json",
    )
    project = Project(id=_project_id)
    combined_model = project.get_active_combined_model()
    assert isinstance(combined_model, CombinedModel)
    assert combined_model.id == _valid_active_combined_model_id
    assert combined_model.project_id == _project_id
    assert combined_model.is_active_combined_model


@responses.activate
def test_combined_model_get_valid(combined_model_get_json):
    responses.add(
        responses.GET,
        _valid_combined_model_url,
        body=combined_model_get_json,
        status=200,
        content_type="application/json",
    )
    combined_model = CombinedModel.get(_project_id, _valid_combined_model_id)

    assert isinstance(combined_model, CombinedModel)
    assert combined_model.id == _valid_combined_model_id
    assert combined_model.project_id == _project_id
    assert not combined_model.is_active_combined_model


@responses.activate
def test_combined_model_invalid_get(invalid_json):
    responses.add(responses.GET, _invalid_combined_model_url, body=invalid_json)
    with pytest.raises(DataError):
        CombinedModel.get(_project_id, _invalid_combined_model_id)


@responses.activate
def test_combined_model_get_segments_as_dataframe(mock_segment_csv):
    add_response(_combined_model_segments_dl_url, mock_segment_csv, content_type="text/csv")
    combined_model = CombinedModel(_valid_combined_model_id, _project_id)
    df = combined_model.get_segments_as_dataframe()

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (10, 5)


@responses.activate
def test_combined_model_get_segments_as_csv(mock_segment_csv):
    add_response(_combined_model_segments_dl_url, mock_segment_csv, content_type="text/csv")
    combined_model = CombinedModel(_valid_combined_model_id, _project_id)
    file_buffer = six.StringIO()
    combined_model.get_segments_as_csv(file_buffer)
    file_buffer.seek(0)

    # Assert the values contained in the output reasonably match the inputs
    actual_values = pd.read_csv(six.StringIO(file_buffer.read())).values
    expected_values = pd.read_csv(six.StringIO(mock_segment_csv)).values[:, 1:]
    np.testing.assert_almost_equal(actual_values, expected_values)


@responses.activate
@pytest.mark.parametrize("clone", [True, False, None])
def test_combined_model_valid_set_segment_champion(invalid_json, clone):
    responses.add(
        responses.PUT,
        _segment_champion_url,
        body=json.dumps({"combinedModelId": str(_model_id)}),
        status=200,
        content_type="application/json",
    )

    if clone is not None:
        combined_model = CombinedModel.set_segment_champion(_project_id, _model_id, clone=clone)
    else:
        combined_model = CombinedModel.set_segment_champion(_project_id, _model_id)
    assert combined_model == "modelId"
    request = request_body_to_json(responses.calls[0].request)
    assert request.get("clone") == bool(clone)
