#!/usr/bin/env python

from google.cloud import secretmanager


def get_secret_manager_value(project_id, secret_id, version_id="latest"):
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    ssm = secretmanager.SecretManagerServiceClient()
    return ssm.access_secret_version(name=name).payload.data.decode('UTF-8')
