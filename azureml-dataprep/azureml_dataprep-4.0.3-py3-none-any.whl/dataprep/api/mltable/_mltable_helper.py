# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains helper methods for mltable apis."""
import re
import yaml
import json
import os
from jsonschema import validate

from enum import Enum

from azureml.dataprep.api._loggerfactory import _LoggerFactory

logger = _LoggerFactory.get_logger("MLTableHelper")

def _download_mltable_yaml(path: str):
    from azureml.dataprep.rslex import Copier, PyLocationInfo, PyIfDestinationExists

    # normalize path to MLTable yaml path
    normalized_path = "{}/MLTable".format(path.rstrip("/"))
    if_destination_exists = PyIfDestinationExists.MERGE_WITH_OVERWRITE
    try:

        from tempfile import mkdtemp
        local_path = mkdtemp()
        Copier.copy_uri(PyLocationInfo('Local', local_path, {}),
                        normalized_path, if_destination_exists, "")

        return local_path
    except Exception as e:
        if "InvalidUriScheme" in e.args[0] or \
            "StreamError(NotFound)" in e.args[0] or \
                "DataAccessError(NotFound)" in e.args[0]:
            raise ValueError(e.args[0])
        else:
            raise SystemError(e.args[0])


def _is_tabular(mltable_yaml):
    if mltable_yaml is None:
        return False

    transformations_key = "transformations"
    if transformations_key not in mltable_yaml.keys():
        return False

    tabular_transformations = [
        "read_delimited",
        "read_parquet",
        "read_json_lines"
    ]

    if mltable_yaml['transformations'] and all(isinstance(e, dict) for e in mltable_yaml['transformations']):
        list_of_transformations = [k for d in mltable_yaml['transformations'] for k, v in d.items()]
    else:
        # case where transformations section is a list[str], not a list[dict].
        list_of_transformations = mltable_yaml['transformations']
    return any(key in tabular_transformations for key in list_of_transformations)


def _validate(mltable_yaml_dict):
    cwd = os.path.dirname(os.path.abspath(__file__))
    schema_path = "{}/schema/MLTable.json".format(cwd.rstrip("/"))
    with open(schema_path, "r") as stream:
        try:
            schema = json.load(stream)
        except yaml.YAMLError:
            raise SystemError("MLTable schema is invalid.")
    try:
        validate(mltable_yaml_dict, schema)
    except Exception as e:
        logger.warn("MLTable validation failed with error: {}".format(e.args))
        raise ValueError("Given MLTable does not adhere to the AzureML MLTable schema: {}".format(e.args))


def _read_yaml(uri):
    local_yaml_path = "{}/MLTable".format(uri.rstrip("/"))
    mltable_yaml_dict = None
    with open(local_yaml_path, "r") as stream:
        try:
            mltable_yaml_dict = yaml.safe_load(stream)
        except yaml.YAMLError:
            raise ValueError("MLTable yaml is invalid: {}".format(mltable_yaml_dict))
    return mltable_yaml_dict


def _path_has_parent_directory_redirection(path):
    if path.startswith('..') or '/..' in path or '\\..' in path:
        return True
    return False


def _make_all_paths_absolute(mltable_yaml_dict, local_path):
    if 'paths' in mltable_yaml_dict:
        for path_dict in mltable_yaml_dict['paths']:
            for path_prop, path in path_dict.items():
                path_type, _, _ = _parse_path_format(path)
                if path_type == _PathType.local and not os.path.isabs(path):
                    if _path_has_parent_directory_redirection(path):
                        logger.info("Path has parent directory redirection. path: {}".format(path))
                    path_dict[path_prop] = os.path.normpath(os.path.join(local_path, path))
                    if os.path.commonprefix([path_dict[path_prop], local_path]) != local_path:
                        raise ValueError("Path is outside the mltable directory. path: {}".format(path))
                    path_dict[path_prop] = "file://" + path_dict[path_prop]
    return mltable_yaml_dict


class _PathType(Enum):
    local = 1
    cloud = 2
    legacy_dataset = 3


def _parse_path_format(path: str, workspace=None):
    regular_cloud_uri_patterns = re.compile(r'^https?://|adl://|wasbs?://|abfss?://|azureml://subscriptions',
                                            re.IGNORECASE)
    if regular_cloud_uri_patterns.match(path):
        return _PathType.cloud, path, None

    dataset_uri_pattern = re.compile(
        r'^azureml://locations/(.*)/workspaces/(.*)/data/([0-9a-z_-]+)/versions/([0-9a-z_-]+)',
        re.IGNORECASE)
    dataset_uri_match = dataset_uri_pattern.match(path)
    if dataset_uri_match:
        return _PathType.legacy_dataset, dataset_uri_match.group(3), dataset_uri_match.group(4)

    return _PathType.local, path, None
