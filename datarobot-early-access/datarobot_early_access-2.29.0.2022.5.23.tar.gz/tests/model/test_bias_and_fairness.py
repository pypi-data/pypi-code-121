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

from datarobot import Job, ModelJob, Project
from datarobot.enums import BiasMitigationTechnique, FairnessMetricsSet


@pytest.fixture
def fairness_insights_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/fairnessInsights/".format(
        project_id, model_id
    )


@pytest.fixture
def data_disparity_insights_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/dataDisparityInsights/".format(
        project_id, model_id
    )


@pytest.fixture
def cross_class_accuracy_scores_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/crossClassAccuracyScores/".format(
        project_id, model_id
    )


@pytest.fixture
def bias_mitigated_models_url(project_id):
    return "https://host_name.com/projects/{}/biasMitigatedModels/".format(project_id)


@pytest.fixture
def fairness_insights_job_creation_response(fairness_insights_url, job_url):
    responses.add(
        responses.POST,
        fairness_insights_url,
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


@pytest.fixture
def data_disparity_insights_job_creation_response(data_disparity_insights_url, job_url):
    responses.add(
        responses.POST,
        data_disparity_insights_url,
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


@pytest.fixture
def cross_class_accuracy_scores_job_creation_response(cross_class_accuracy_scores_url, job_url):
    responses.add(
        responses.POST,
        cross_class_accuracy_scores_url,
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


def fairness_insights_server_data(model_id, fairness_metric):
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "data": [
            {
                "modelId": "".format(model_id),
                "fairnessMetric": fairness_metric,
                "fairnessThreshold": 0.8,
                "predictionThreshold": 0.5,
                "protectedFeature": "race",
                "perClassFairness": [
                    {
                        "className": "Amer-Indian-Eskimo",
                        "value": 0.35355038390571986,
                        "absoluteValue": 0.07547169811320754,
                        "entriesCount": 53,
                        "isStatisticallySignificant": False,
                    },
                    {
                        "className": "Asian-Pac-Islander",
                        "value": 1,
                        "absoluteValue": 0.23417721518987342,
                        "entriesCount": 158,
                        "isStatisticallySignificant": False,
                    },
                    {
                        "className": "White",
                        "value": 1.0,
                        "absoluteValue": 0.21346801346801347,
                        "entriesCount": 4455,
                        "isStatisticallySignificant": True,
                    },
                ],
            },
        ],
        "totalCount": 1,
    }


@pytest.fixture
def feature():
    return "race"


@pytest.fixture
def class_name1():
    return "Amer-Indian-Eskimo"


@pytest.fixture
def class_name2():
    return "Black"


@pytest.fixture
def data_disparity_insights_server_data(feature, class_name1, class_name2):
    return {
        "count": 2,
        "next": None,
        "previous": None,
        "totalCount": 2,
        "data": {
            "protectedFeature": feature,
            "metric": "psi",
            "values": [{"label": class_name1, "count": 53}, {"label": class_name2, "count": 511}],
            "features": [
                {
                    "name": "salary",
                    "disparityScore": 0.019521590824952226,
                    "featureImpact": 1,
                    "status": "Healthy",
                    "detailsHistogram": [
                        {
                            "bin": ">50K",
                            "bars": [
                                {"label": class_name1, "value": 0.09433962264150944},
                                {"label": class_name2, "value": 0.13894324853228962},
                            ],
                        },
                    ],
                },
                {
                    "name": "capital_gain",
                    "disparityScore": 0.03430540040461845,
                    "featureImpact": 1.0,
                    "status": "Healthy",
                    "detailsHistogram": [
                        {
                            "bin": "[0.0, 9999.9)",
                            "bars": [
                                {"label": class_name1, "value": 0.9811320754716981},
                                {"label": class_name2, "value": 0.9804305283757339},
                            ],
                        },
                        {
                            "bin": "[9999.9, 19999.8)",
                            "bars": [
                                {"label": class_name1, "value": 0.018867924528301886},
                                {"label": class_name2, "value": 0.009784735812133072},
                            ],
                        },
                    ],
                },
            ],
        },
    }


@pytest.fixture
def cross_class_accuracy_scores_server_data(model_id, feature, class_name1, class_name2):
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "data": [
            {
                "feature": feature,
                "modelId": model_id,
                "predictionThreshold": 0.5,
                "perClassAccuracyScores": [
                    {
                        "className": class_name1,
                        "metrics": [
                            {"metric": "LogLoss", "value": 0.15817195767047793},
                            {"metric": "f1", "value": 0.7175572519083969},
                            {"metric": "AUC", "value": 0.9645006402048656},
                            {"metric": "accuracy", "value": 0.9275929549902152},
                        ],
                    },
                    {
                        "className": class_name2,
                        "metrics": [
                            {"metric": "LogLoss", "value": 0.10583976310412195},
                            {"metric": "f1", "value": 0.8888888888888888},
                            {"metric": "AUC", "value": 1.0},
                            {"metric": "accuracy", "value": 0.9811320754716981},
                        ],
                    },
                ],
            },
        ],
        "totalCount": 1,
    }


@pytest.fixture
def bias_mitigated_models_server_data(model_id, parent_model_id, feature):
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "data": [
            {
                "model_id": model_id,
                "parent_model_id": parent_model_id,
                "protected_feature": feature,
                "bias_mitigation_technique": BiasMitigationTechnique.PREPROCESSING_REWEIGHING,
                "include_bias_mitigation_feature_as_predictor_variable": False,
            },
        ],
        "totalCount": 1,
    }


@pytest.fixture
def bias_mitigation_feature_info_data():
    msg = "Some protected feature values are rare. (Less than or equal to 100 instances.)"
    return {
        "messages": [
            {
                "messageText": msg,
                "additionalInfo": ['The value "Female" appears only 53 times.'],
                "messageLevel": "WARNING",
            }
        ]
    }


@pytest.fixture
def fairness_insights_response_equal_parity(fairness_insights_url, model_id):
    body = json.dumps(fairness_insights_server_data(model_id, FairnessMetricsSet.EQUAL_PARITY))
    responses.add(
        responses.GET,
        "{}?offset=0&limit=100&fairnessMetricsSet={}".format(
            fairness_insights_url, FairnessMetricsSet.EQUAL_PARITY
        ),
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def data_disparity_insights_response(
    data_disparity_insights_url,
    data_disparity_insights_server_data,
    feature,
    class_name1,
    class_name2,
):
    body = json.dumps(data_disparity_insights_server_data)
    responses.add(
        responses.GET,
        "{}?feature={}&className1={}&className2={}".format(
            data_disparity_insights_url, feature, class_name1, class_name2
        ),
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def cross_class_accuracy_scores_response(
    cross_class_accuracy_scores_url, cross_class_accuracy_scores_server_data,
):
    body = json.dumps(cross_class_accuracy_scores_server_data)
    responses.add(
        responses.GET,
        cross_class_accuracy_scores_url,
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def get_bias_mitigated_models_response(
    bias_mitigated_models_url, bias_mitigated_models_server_data
):
    body = json.dumps(bias_mitigated_models_server_data)
    responses.add(
        responses.GET,
        bias_mitigated_models_url,
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def get_bias_mitigation_feature_info_response(
    project_id, feature, bias_mitigation_feature_info_data
):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/biasMitigationFeatureInfo/?featureName={}".format(
            project_id, feature
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(bias_mitigation_feature_info_data),
    )


@responses.activate
@pytest.mark.usefixtures(
    "fairness_insights_job_creation_response", "fairness_insights_response_equal_parity",
)
def test_request_fairness_insights(one_model, job_id):
    assert one_model.request_fairness_insights() == job_id

    fairness_metrics_set = FairnessMetricsSet.EQUAL_PARITY
    assert one_model.request_fairness_insights(fairness_metrics_set) == job_id

    fairness_insights = one_model.get_fairness_insights(fairness_metrics_set=fairness_metrics_set)
    assert fairness_insights["data"][0]["fairnessMetric"] == fairness_metrics_set


@responses.activate
@pytest.mark.usefixtures(
    "data_disparity_insights_job_creation_response",
    "data_disparity_insights_response",
    "data_disparity_insights_server_data",
)
def test_request_data_disparity_insights(one_model, job_id, feature, class_name1, class_name2):
    assert (
        one_model.request_data_disparity_insights(
            feature=feature, compared_class_names=[class_name1, class_name2]
        )
        == job_id
    )

    data_disparity_insights = one_model.get_data_disparity_insights(
        feature, class_name1, class_name2
    )
    assert data_disparity_insights["data"]["protectedFeature"] == feature


@responses.activate
@pytest.mark.usefixtures(
    "cross_class_accuracy_scores_job_creation_response",
    "cross_class_accuracy_scores_response",
    "cross_class_accuracy_scores_server_data",
)
def test_cross_class_accuracy_scores(one_model, job_id, feature):
    assert one_model.request_cross_class_accuracy_scores() == job_id

    data_disparity_insights = one_model.get_cross_class_accuracy_scores()
    assert data_disparity_insights["data"][0]["feature"] == feature


@responses.activate
@pytest.mark.usefixtures("get_bias_mitigated_models_response", "bias_mitigated_models_server_data")
def test_get_bias_mitigated_models(project, parent_model_id, model_id, feature):
    bias_mitigated_models_list = project.get_bias_mitigated_models()

    assert len(bias_mitigated_models_list) == 1

    bias_mitigated_model_info = bias_mitigated_models_list[0]

    assert bias_mitigated_model_info == {
        "model_id": model_id,
        "parent_model_id": parent_model_id,
        "protected_feature": feature,
        "bias_mitigation_technique": BiasMitigationTechnique.PREPROCESSING_REWEIGHING,
        "include_bias_mitigation_feature_as_predictor_variable": False,
    }


@responses.activate
def test_apply_bias_mitigation(project, parent_model_id, model_id, feature):
    """Test whether we can successfully submit a job to apply bias mitigation to a model."""

    # GIVEN the POST request for applying bias mitigation returns a location of the model job
    job_id = 1
    model_job_url = "https://host_name.com/projects/p-id/modelJobs/{}/".format(job_id)
    responses.add(
        responses.POST,
        "https://host_name.com/projects/p-id/biasMitigatedModels/",
        status=202,
        body="",
        adding_headers={"Location": model_job_url},
    )

    # AND the GET request for retrieving model jobs by job id works
    # (just copied this placeholder data from test_blend_return_job_id)
    model_job_data = {
        "status": "inprogress",
        "processes": [],
        "projectId": "p-id",
        "samplePct": 0,
        "modelType": "foo",
        "featurelistId": "foo",
        "modelCategory": "foo",
        "blueprintId": "foo",
        "isBlocked": False,
        "id": job_id,
    }
    responses.add(
        responses.GET,
        model_job_url,
        status=200,
        body=json.dumps(model_job_data),
        content_type="application/json",
    )

    # WHEN we apply bias mitigation
    result = Project("p-id").apply_bias_mitigation(
        parent_model_id, feature, BiasMitigationTechnique.PREPROCESSING_REWEIGHING, False
    )

    # THEN we get back a ModelJob with the correct job id
    assert isinstance(result, ModelJob)
    assert result.id == job_id


@responses.activate
@pytest.mark.usefixtures("get_bias_mitigation_feature_info_response",)
def test_request_bias_mitigation_feature_info(
    project_id, project, feature, bias_mitigation_feature_info_data
):
    """Test whether we can submit a compute job for the bias mitigation feature info."""

    # GIVEN the POST request returns a location of a status that can be polled
    job_id = 1
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/biasMitigationFeatureInfo/{}".format(
            project_id, feature
        ),
        status=200,
        content_type="application/json",
        body="",
        adding_headers={"Location": "https://host_name.com/v2/api/status/1"},
    )
    # AND a GET request to that status location that will return a location for the
    # bias mitigation feature info data once the status is COMPLETE
    model_job_data = {
        "status": "inprogress",
        "processes": [],
        "projectId": "p-id",
        "samplePct": 0,
        "modelType": "foo",
        "featurelistId": "foo",
        "modelCategory": "foo",
        "blueprintId": "foo",
        "isBlocked": False,
        "id": job_id,
        "url": "https://host_name.com/foo",
    }
    url = "https://host_name.com/projects/{}/biasMitigationFeatureInfo/?featureName={}"
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/jobs/status/".format(project_id),
        status=303,
        content_type="application/json",
        body=json.dumps(model_job_data),
        adding_headers={"Location": url.format(project_id, feature)},
    )

    # WHEN we call this route to compute the bias mitigation feature info data
    result = project.request_bias_mitigation_feature_info(feature)

    # THEN we get back a ModelJob with the correct job id
    assert isinstance(result, Job)
    assert result.id == job_id


@responses.activate
@pytest.mark.usefixtures("get_bias_mitigation_feature_info_response",)
def test_get_bias_mitigation_feature_info(
    project_id, project, feature, bias_mitigation_feature_info_data
):
    """Test whether we can compute and the fetch bias mitigation feature info."""
    # GIVEN a GET request to the data that will return the data (defined in the fixture)
    # WHEN we call this route to get the bias mitigation feature info data
    bias_mitigation_feature_info = project.get_bias_mitigation_feature_info(feature)
    # THEN we'll get the data we expect
    assert bias_mitigation_feature_info == bias_mitigation_feature_info_data
