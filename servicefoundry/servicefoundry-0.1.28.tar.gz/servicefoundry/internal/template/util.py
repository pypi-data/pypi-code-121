import json
from os import listdir
from os.path import exists, isfile, join
from pathlib import Path

import yaml
from jsonschema import validate

from ..clients.service_foundry_client import ServiceFoundryServiceClient
from ..const import BUILD_DIR
from ..exceptions import ConfigurationException
from ..util import download_file, read_text, uncompress_tarfile


def validate_schema(template, schema):
    schema = read_text(schema)
    schema = json.loads(schema)
    validate(instance=template, schema=schema)


def get_or_create_template_folder(template_id):
    Path(f"{BUILD_DIR}/template").mkdir(parents=True, exist_ok=True)
    template_folder = f"{BUILD_DIR}/template/{template_id}"

    if not Path(template_folder).is_dir():
        tfs_client = ServiceFoundryServiceClient.get_client(auth_required=False)
        package_url = tfs_client.get_template_by_id(template_id)["url"]
        package_file = f"{BUILD_DIR}/template/{template_id}.tgz"
        download_file(package_url, package_file)
        uncompress_tarfile(package_file, template_folder)
    return template_folder


def load_yaml_from_file(file):
    with open(file) as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ConfigurationException(f"File {file} is not in yaml format. {exc}")


def list_dir_and_files(path, rpath=""):
    dirs = []
    files = []
    for f in listdir(path):
        _path = join(path, f)
        _rpath = join(rpath, f)
        if isfile(_path):
            files.append(_rpath)
        else:
            dirs.append(_rpath)
            _dirs, _files = list_dir_and_files(_path, _rpath)
            dirs.extend(_dirs)
            files.extend(_files)
    return dirs, files


def check_common(out_folder, files):
    common_files = []
    for file in files:
        path = join(out_folder, file)
        if exists(path):
            common_files.append(file)
    return common_files
