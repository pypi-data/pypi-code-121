"""Test config settings for the mocked end-to-end tests."""
from typing import Callable, Dict, Tuple

import flask
from flask import Flask, jsonify
from flask import request as flask_request
from pytest import fixture

from bitfount.federated.transport.message_service import _S3_NETLOC_SUFFIX
from bitfount.hub.types import (
    _HubFailureResponseJSON,
    _HubSuccessResponseJSON,
    _PodDetailsResponseJSON,
    _PodRegistrationFailureJSON,
    _PodRegistrationResponseJSON,
)
from bitfount.types import _S3PresignedPOSTFields, _S3PresignedPOSTURL, _S3PresignedURL
from tests.utils import PytestRequest


@fixture
def s3_upload_url_builder() -> Callable[[str], _S3PresignedPOSTURL]:
    """Builds an S3 upload url with the specified pod name at the end."""

    def _create(pod_name: str) -> _S3PresignedPOSTURL:
        return _S3PresignedPOSTURL(
            f"https://an-s3-upload-url{_S3_NETLOC_SUFFIX}/some-resource/{pod_name}"
        )

    return _create


@fixture
def s3_download_url_builder() -> Callable[[str], _S3PresignedURL]:
    """Builds an S3 download url with the specified pod name at the end."""

    def _create(pod_name: str) -> _S3PresignedURL:
        return _S3PresignedURL(
            f"https://an-s3-download-url{_S3_NETLOC_SUFFIX}/some-resource/{pod_name}"
        )

    return _create


@fixture
def app(
    modeller_public_key_string: str,
    request: PytestRequest,
    s3_download_url_builder: Callable[[str], _S3PresignedURL],
    s3_upload_fields: _S3PresignedPOSTFields,
    s3_upload_url_builder: Callable[[str], _S3PresignedPOSTURL],
) -> Flask:
    """Creates the Bitfount Hub API."""
    register_pod_fail, access_request_fail, get_pod_fail = (
        False,
        False,
        False,
    )
    if hasattr(request, "param"):
        (
            register_pod_fail,
            access_request_fail,
            get_pod_fail,
        ) = request.param

    api = Flask(__name__)

    pod_public_keys: Dict[str, str] = {}

    @api.route("/")
    def index() -> str:
        """Top level of the app. Just used to retrieve the URL."""
        return ""  # needs to return _something_

    @api.route("/api/pods", methods=["POST", "PATCH"])
    def register_pod() -> Tuple[flask.Response, int]:
        if flask_request.method == "POST":
            if register_pod_fail:
                # 400 POST response has { success, errorMessage, alreadyExisted } JSON
                post_failure_response: _PodRegistrationFailureJSON = {
                    "success": False,
                    "errorMessage": "Fail!",
                    "alreadyExisted": False,
                }
                return (
                    jsonify(post_failure_response),
                    400,
                )
            content = flask_request.get_json()
            pod_name: str = content.get("name")
            pod_public_key: str = content.get("podPublicKey")
            pod_public_keys[pod_name] = pod_public_key
            upload_url = s3_upload_url_builder(pod_name)
            # 200/201 POST response has { success, alreadyExisted, message,
            # uploadUrl, uploadFields } JSON
            post_success_response: _PodRegistrationResponseJSON = {
                "success": True,
                "message": "Success!",
                "alreadyExisted": False,
                "uploadUrl": upload_url,
                "uploadFields": s3_upload_fields,
            }
            return jsonify(post_success_response), 200
        elif flask_request.method == "PATCH":
            content = flask_request.get_json()
            pod_name = content.get("name")
            pod_public_key = content.get("podPublicKey")
            pod_public_keys[pod_name] = pod_public_key
            # 200 PATCH response has { success, message } JSON
            success_response: _HubSuccessResponseJSON = {
                "success": True,
                "message": "Success!",
            }
            return (
                jsonify(success_response),
                200,
            )
        raise TypeError(f"Unrecognised HTTP method {flask_request.method}")

    @api.route("/api/pods/<username>/<pod_name>", methods=["GET"])
    def get_pod(username: str, pod_name: str) -> Tuple[flask.Response, int]:
        if get_pod_fail:
            failure_response: _HubFailureResponseJSON = {
                "success": False,
                "errorMessage": "Fail!",
            }
            return jsonify(failure_response), 500

        pod_details_json: _PodDetailsResponseJSON = {
            "podIdentifier": f"{username}/{pod_name}",
            "podName": pod_name,
            "podDisplayName": pod_name,
            "podPublicKey": pod_public_keys[pod_name],
            "accessManagerPublicKey": "not_a_real_am_key",
            "description": pod_name,
            "schemaStorageKey": "schema_storage_key",
            "isOnline": True,
            "providerUserName": "providerUserName",
            "visibility": "public",
            "schemaDownloadUrl": s3_download_url_builder(pod_name),
        }
        return jsonify(pod_details_json), 200

    api.testing = True

    return api
