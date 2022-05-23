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

import pytest
import responses

from datarobot import errors, ShapImpact


@pytest.fixture
def shap_impact_server_data():
    return {
        u"count": 2,
        u"rowCount": 10,
        u"shapImpacts": [
            {
                u"featureName": u"number_inpatient",
                u"impactNormalized": 1.0,
                u"impactUnnormalized": 0.07670175497683789,
            },
            {
                u"featureName": u"number_diagnoses",
                u"impactNormalized": 0.6238014237049752,
                u"impactUnnormalized": 0.047846663955221636,
            },
        ],
    }


@pytest.fixture
def shap_impact_server_data_without_row_count():
    return {
        u"count": 2,
        u"shapImpacts": [
            {
                u"featureName": u"number_inpatient",
                u"impactNormalized": 1.0,
                u"impactUnnormalized": 0.07670175497683789,
            },
            {
                u"featureName": u"number_diagnoses",
                u"impactNormalized": 0.6238014237049752,
                u"impactUnnormalized": 0.047846663955221636,
            },
        ],
    }


@pytest.fixture
def shap_impact_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/shapImpact/".format(project_id, model_id)


@pytest.fixture
def shap_impact_job_creation_response(shap_impact_url, job_url):
    responses.add(
        responses.POST, shap_impact_url, body="", status=202, adding_headers={"Location": job_url}
    )


@pytest.fixture
def shap_impact_response(shap_impact_server_data, shap_impact_url):
    body = json.dumps(shap_impact_server_data)
    responses.add(
        responses.GET, shap_impact_url, status=200, content_type="application/json", body=body
    )


@pytest.fixture
def shap_impact_without_row_count_response(
    shap_impact_server_data_without_row_count, shap_impact_url
):
    body = json.dumps(shap_impact_server_data_without_row_count)
    responses.add(
        responses.GET, shap_impact_url, status=200, content_type="application/json", body=body
    )


@pytest.fixture
def shap_impact_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType="shapImpact")


@pytest.fixture
def shap_impact_job_finished_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType="shapImpact")


@pytest.fixture
def shap_impact_running_response(shap_impact_job_running_server_data, job_url):
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(shap_impact_job_running_server_data),
        status=200,
        content_type="application/json",
    )


@pytest.fixture
def shap_impact_completed_response(shap_impact_job_finished_server_data, job_url, shap_impact_url):
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(shap_impact_job_finished_server_data),
        status=303,
        adding_headers={"Location": shap_impact_url},
        content_type="application/json",
    )


@pytest.fixture
def shap_impact_previously_ran_response(project_url, model_id, job_id, job_url):
    body = {
        "message": "SHAP impact already exists.",
        "errorName": "JobAlreadyAdded",
        "jobId": job_id,
    }
    responses.add(
        responses.POST,
        "{}models/{}/shapImpact/".format(project_url, model_id),
        body=json.dumps(body),
        status=202,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )


@responses.activate
@pytest.mark.usefixtures("shap_impact_job_creation_response", "shap_impact_running_response")
def test_get_shap_impact_job_result_not_finished(project_id, model_id):
    shap_impact_job = ShapImpact.create(project_id, model_id)
    with pytest.raises(errors.JobNotFinished):
        shap_impact_job.get_result()


@responses.activate
@pytest.mark.usefixtures("shap_impact_job_creation_response", "shap_impact_running_response")
def test_wait_for_shap_impact_never_finished(project_id, model_id, mock_async_time):
    mock_async_time.time.side_effect = (0, 5)
    shap_impact_job = ShapImpact.create(project_id, model_id)
    with pytest.raises(errors.AsyncTimeoutError):
        shap_impact_job.get_result_when_complete(max_wait=1)


def assert_shap_impact_result(shap_impact, shap_impact_server_data):
    assert shap_impact is not None
    assert shap_impact.count is not None
    assert shap_impact.shap_impacts is not None
    assert shap_impact.row_count == shap_impact_server_data.get("rowCount")
    assert shap_impact.count == len(shap_impact.shap_impacts)
    assert shap_impact.count == shap_impact_server_data["count"]
    assert len(shap_impact.shap_impacts) == len(shap_impact_server_data["shapImpacts"])
    for actual, expected in zip(shap_impact.shap_impacts, shap_impact_server_data["shapImpacts"]):
        assert actual["feature_name"] == expected["featureName"]
        assert actual["impact_normalized"] == expected["impactNormalized"]
        assert actual["impact_unnormalized"] == expected["impactUnnormalized"]


@responses.activate
@pytest.mark.usefixtures(
    "shap_impact_job_creation_response", "shap_impact_completed_response", "shap_impact_response"
)
def test_get_shap_impact_job_result_finished(project_id, model_id, shap_impact_server_data):
    shap_impact_job = ShapImpact.create(project_id, model_id)
    shap_impact = shap_impact_job.get_result()
    assert_shap_impact_result(shap_impact, shap_impact_server_data)


@responses.activate
@pytest.mark.usefixtures(
    "shap_impact_job_creation_response",
    "shap_impact_completed_response",
    "shap_impact_without_row_count_response",
)
def test_get_shap_impact_without_row_count_job_result_finished(
    project_id, model_id, shap_impact_server_data_without_row_count
):
    shap_impact_job = ShapImpact.create(project_id, model_id)
    shap_impact = shap_impact_job.get_result_when_complete()
    assert_shap_impact_result(shap_impact, shap_impact_server_data_without_row_count)


@responses.activate
@pytest.mark.usefixtures(
    "shap_impact_previously_ran_response", "shap_impact_completed_response", "shap_impact_response"
)
def test_get_or_request_shap_impact_previously_requested(
    project_id, model_id, shap_impact_server_data
):
    shap_impact_job = ShapImpact.create(project_id, model_id)
    assert shap_impact_job.job_type == "shapImpact"
    assert shap_impact_job.status == "COMPLETED"
    shap_impact = shap_impact_job.get_result()
    assert_shap_impact_result(shap_impact, shap_impact_server_data)


@responses.activate
@pytest.mark.usefixtures("shap_impact_response")
def test_shap_impact_get(project_id, model_id, shap_impact_server_data):
    shap_impact = ShapImpact.get(project_id, model_id)
    assert_shap_impact_result(shap_impact, shap_impact_server_data)
