import json
import logging
import tempfile
import os
import argparse
import requests
import urllib

import numpy as np
from pydantic import BaseModel, Field, PrivateAttr, root_validator, parse_obj_as, validator
from typing import Callable, Optional, List, Dict, Any, Type, Union, Iterable
from uuid import uuid4
from datetime import datetime
from urllib.parse import quote

from brevettiai import Module
from brevettiai.model import ModelMetadata
from brevettiai.interfaces import vue_schema_utils as vue
from brevettiai.interfaces.git_state import GitRepositoryState
from brevettiai.interfaces import package_validation
from brevettiai.io import IoTools, io_tools
from brevettiai.platform.models import PlatformBackend
from brevettiai.platform.models import backend as default_backend
from brevettiai.platform.platform_credentials import DefaultJobCredentialsChain
from brevettiai.platform.models import Dataset, Tag
from brevettiai.utils import argparse_utils, env_variables

log = logging.getLogger(__name__)

custom_json_encoders = {
    Module: lambda x: x.get_config()
}


def parse_job_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='path to platform host', default=None)
    parser.add_argument('--data_bucket', help='location of dataset bucket', default=None)
    parser.add_argument('--job_dir', help='location to write checkpoints and export models', default=None)
    parser.add_argument('--model_id', help='Assigned id to model', default='unknown')
    parser.add_argument('--test_id', help='Assigned id to model', default='unknown')
    parser.add_argument('--api_key', help="Job api key", default=None)
    parser.add_argument('--info_file', type=str, help='Info file with test job info', required=False)
    parser.add_argument('--cache_path', type=str, help='Cache path', required=False)
    parser.add_argument('--raygun_api_key', help='api key for raygun', default=None)
    parser.add_argument('--run_locally', help='Run the job locally', default=False)
    return parser.parse_known_args()


class JobSettings(BaseModel):
    """
    Baseclass for job settings
    """
    extra: Dict[str, Any] = Field(default_factory=dict, vue=vue.SchemaConfig(exclude=True))

    class Config:
        arbitrary_types_allowed = True
        json_encoders = custom_json_encoders

    @classmethod
    def platform_schema(cls):
        """Utility function to get vue schema"""
        builder = vue.from_pydantic_model(cls)
        return builder

    @root_validator(pre=True, allow_reuse=True)
    def parse_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Extra validator parsing settings from the platform"""

        # Parse extra args
        all_required_field_names = {field.alias for field in cls.__fields__.values() if
                                    field.alias != 'extra'}  # to support alias

        extra: Dict[str, Any] = values.get("Extra", {})
        for field_name in list(values):
            if field_name not in all_required_field_names:
                extra[field_name] = values.pop(field_name)
        values['extra'] = extra

        # Parse string as json variables
        properties = cls.schema()["properties"]
        try:
            for k, v in values.items():
                if isinstance(v, str) and (not "string" in [properties[k]["type"]] if "type" in properties[k] else [t["type"] for t in properties[k]["anyOf"]]):
                    if v == "":
                        values[k] = None
                    else:
                        values[k] = json.loads(v)
        except (ValueError, KeyError):
            pass

        return values


class Job(BaseModel):
    """
    Model defining a job on the Brevetti platform,
    Use it as base class for your jobs

    Local caching of remote files across jobs can be enabled via argv `--cache_path`
    or the `BREVETTI_AI_CACHE` environment variable
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%dT%H%M%S"))
    name: str
    datasets: List[Dataset] = Field(default_factory=list)
    models: List[dict] = Field(default_factory=list)
    settings: JobSettings = Field(default_factory=dict)
    tags: List[Tag] = Field(default_factory=list)
    api_key: Optional[str]
    host_name: Optional[str]
    charts_url: Optional[str]
    complete_url: Optional[str]
    remote_url: Optional[str]
    security_credentials_url: Optional[str]  # Deprecated
    parent: Optional[dict]
    model_path: Optional[str]

    _job_dir: str = PrivateAttr(default=None)
    _backend: PlatformBackend = PrivateAttr(default=None)
    _io: IoTools = PrivateAttr(default=None)
    _temp_dir_reference: Optional[tempfile.TemporaryDirectory] = PrivateAttr(default=None)
    _temp_dir: str = PrivateAttr(default=None)
    _job_output: dict = PrivateAttr(default_factory=dict)
    _is_started: bool = PrivateAttr(default=False)

    class Config:
        json_encoders = custom_json_encoders

    def __init__(self, io=io_tools, backend=default_backend, cache_path=None, job_dir=None, **data) -> None:
        # Inject backend and io into datasets that are not yet initialized
        for ds in data.get("datasets", []):
            if not isinstance(ds, Dataset):
                ds["io"] = io
                ds["backend"] = backend

        super().__init__(**data)

        self._io = io
        self._backend = backend
        self._temp_dir = cache_path
        self._job_dir = job_dir

    def get_metadata(self) -> Union[ModelMetadata]:
        """
        Build metadata object, containing information to transfer to external users of the model
        """
        return ModelMetadata(
            id=self.id,
            run_id=self.run_id,
            name=self.name,
            host_name=self.host_name,
            producer=type(self).__name__
        )

    def start(self, resolve_access_rights: bool = True, cache_remote_files: bool = True, set_credentials: bool = True, complete_job: bool = True):
        """
        Start the job
        """
        self._is_started = True
        self.prepare_temp_dir()

        if cache_remote_files:
            self.io.set_cache_root(self.temp_path(dir=True))

        if set_credentials:
            self.io.minio.credentials = self.io.minio.credentials or DefaultJobCredentialsChain()
            self.io.minio.credentials.set_credentials(type="JobCredentials", user=self.id, secret=self.api_key)

        if resolve_access_rights:
            self.resolve_access_rights()

        self.upload_job_output()
        package_path = self.run()

        if complete_job:
            self.complete(package_path=package_path)
        return package_path

    def run(self) -> Optional[str]:
        """
        Overwrite this to run your job
        Return path to model in temp dir to upload
        """
        return None

    def resolve_access_rights(self) -> None:
        """
        Resolve access rights of this job
        :return:
        """
        self.io.resolve_access_rights(path=self.job_dir, resource_id=self.id, resource_type="job", mode="w")
        for ds in self.datasets:
            ds.resolve_access_rights()
        for model in self.models:
            self.io.resolve_access_rights(path=model['bucket'], resource_id=model['id'], resource_type="job", mode="w")

    @property
    def io(self):
        """Io reference for file handling"""
        return self._io

    @property
    def backend(self):
        """Reference to the backend"""
        return self._backend

    def prepare_temp_dir(self):
        """Set the tempdir of the job, based on defaults if not already set"""
        self._temp_dir = os.getenv(env_variables.BREVETTI_AI_CACHE, self._temp_dir)
        if self._temp_dir is None:
            self._temp_dir_reference = tempfile.TemporaryDirectory(prefix=f"brevettiai-job-{self.id}-")
            self._temp_dir = self._temp_dir_reference.name

    @property
    def job_dir(self) -> str:
        return self._job_dir or self.backend.resource_path(self.id)

    def prepare_path(self, *paths, dir: bool = False) -> str:
        dir_ = paths if dir else paths[:-1]
        folder = self.io.path.join(*dir_)
        self.io.make_dirs(folder)
        return folder if dir else self.io.path.join(folder, paths[-1])

    def artifact_path(self, *paths, dir: bool = False) -> str:
        """
        Get path in the artifact directory tree
        :param paths: N path arguments
        :param dir: this is a directory
        :return:
        """
        return self.prepare_path(self.job_dir, "artifacts", *paths, dir=dir)

    def temp_path(self, *paths, dir=False):
        """
        Get path in the temp directory tree
        :param paths: N path arguments
        :param dir: this is a directory
        :return:
        """
        return self.prepare_path(self._temp_dir, *paths, dir=dir)

    def upload_artifact(self, artifact_name, payload, is_file=False):
        """
        Upload an artifact with a given name
        :param artifact_name: target artifact name
        :param payload: source
        :param is_file: payload is string to file location
        :return:
        """
        self.check_started()
        artifact_path = self.artifact_path(*((artifact_name,) if isinstance(artifact_name, str) else artifact_name))
        log.info('Uploading {} to {}'.format(artifact_name, artifact_path))
        if is_file:
            self.io.copy(payload, artifact_path)
        else:
            self.io.write_file(artifact_path, payload)

        return artifact_path

    def get_annotation_url(self, s3_image_path, annotation_name=None,
                           bbox=None, zoom=None, screen_size=1024, test_report_id=None, model_id=None,
                           min_zoom=2, max_zoom=300):
        """
        Get url to annotation file
        :param s3_image_path: Name of image file
        :param annotation_name: Name of annotation file, if any
        :param bbox: Selects zoom and center for the bbox
        :param zoom: Zoom level [2-300] related to screen pixel size (if None zoom will be calculated from bbox)
        :param screen_size: default screen size in pixels
        :param test_report_id:
        :param model_id:
        :param min_zoom:
        :param max_zoom:
        """

        uri_length = 36
        rm_keys = [self.backend.data_bucket, ".tiles/", "/dzi.json"]
        image_key = s3_image_path
        for rm_key in rm_keys:
            image_key = image_key.replace(rm_key, "")
        image_key = image_key.lstrip("/")
        dataset_id = image_key[:uri_length]
        image_rel_path = "/".join(image_key.split("/")[1:])

        url_info = dict(file=image_rel_path)

        if annotation_name:
            url_info["annotationFile"] = annotation_name

        if test_report_id:
            url_info["testReportId"] = test_report_id

        if model_id:
            url_info["modelId"] = model_id

        if bbox is not None:
            url_info["x"], url_info["y"] = np.array(bbox).reshape(2, 2).mean(0).astype(np.int)
            # NB: This will be overwritten if zoom is provided
            zoom = (100 * screen_size / np.array(bbox).reshape(2, 2).T.dot([-1, 1]))
            url_info["zoom"] = int(zoom.clip(min=min_zoom, max=max_zoom).min())

        if zoom:
            url_info["zoom"] = zoom

        return "https://platform.brevetti.ai/data/{}?".format(dataset_id) + urllib.parse.urlencode(url_info)

    def add_output_metric(self, key, metric):
        """
        Add an output metric for the job comparison module
        :param key:
        :param metric:
        :return:
        """
        self.check_started()
        self._job_output[key] = metric

    def add_output_metrics(self, metrics):
        """
        Add a number of metrics to the job
        :param metrics:
        :return:
        """
        self.check_started()
        self._job_output.update(metrics)

    def upload_job_output(self, path="output.json"):
        """
        Upload / update the output.json artifact containing parsed settings, etc.
        :param path:
        :return:
        """
        self.check_started()
        # Load relevant environment variables
        environment = {x: os.getenv(x) for x in ("BUILD_ID",)}

        # Add git info if available
        for name, object_type in (("git", type(self)), ("brevettiai git", Job)):
            try:
                environment[name] = GitRepositoryState.from_type(object_type)
            except Exception:
                pass

        # Verify python environment packages
        try:
            environment["modules"] = package_validation.get_module_status_from_poetry_lock(type(self))
        except (FileNotFoundError, TypeError):
            environment["modules"] = package_validation.get_installed_modules()

        payload = JobOutput(
            output=self._job_output,
            environment=environment,
            config=self
        ).json(indent=2, exclude={"job": {"api_key"}})
        if self.api_key:
            payload = payload.replace(self.api_key, "*" * len(self.api_key))
        return self.upload_artifact(path, payload)

    def get_output_segmentation_dir(self, path: str, bucket: str):
        """
        Build output segmentation path of object
        Used in conjunction with job.artifact_path
        `self.artifact_path(output_segmentation_dir, "segmentation.json")`

        Args:
            path: path to object
            bucket: dataset bucket, in which path resides

        Returns:

        """
        sep = self.io.path.get_sep(bucket)
        bucket_id = bucket.rsplit(sep, 1)[-1]
        return sep.join((
            self.backend.output_segmentation_dir,
            bucket_id,
            ".annotations",
            path[len(bucket)+1:],
        ))

    def get_remote_monitor(self):
        """Retrieve remote monitor object if available"""
        self.check_started()
        from brevettiai.interfaces.remote_monitor import RemoteMonitor
        return RemoteMonitor(root=self.host_name, path=self.remote_url) if self.remote_url else None

    def complete(self, tmp_package_path=None, package_path=None, output_args=''):
        """
        Complete job by uploading package to gcs and notifying api
        :param tmp_package_path: Path to tar archive with python package
        :param package_path: package path on gcs
        :param output_args
        :return:
        """
        self.check_started()
        self.upload_job_output()

        complete_url_args = ""
        if package_path is None:
            if tmp_package_path is not None:
                artifact_path = self.artifact_path("saved_model.tar.gz")
                self.io.copy(tmp_package_path, artifact_path)
                complete_url_args = quote(artifact_path)
        else:
            artifact_path = self.io.path.relpath(package_path, self.job_dir)
            assert ".." not in artifact_path, "Illegal package path. It should be an artifact of the model"
            complete_url_args = quote(artifact_path)

        # Clean temp dir if autogenerated
        if self._temp_dir_reference is not None:
            self._temp_dir_reference.cleanup()
            self._temp_dir_reference = None

        if self.complete_url:
            complete_url = self.host_name + self.complete_url + complete_url_args + output_args
            try:
                r = requests.post(complete_url)
                log.info(f'Job completed: {complete_url.split("&", 1)[-1]}')
                self._is_started = False
                return r
            except requests.exceptions.HTTPError as e:
                log.warning("HTTP error on complete job", exc_info=e)
            except requests.exceptions.RequestException as e:
                log.warning("No Response on complete job", exc_info=e)
        else:
            log.warning("No known completion url, backend not notified")

    @classmethod
    def init(cls, job_id: Optional[str] = None, api_key: Optional[str] = None,
             cache_path: Optional[str] = None, info_file: Optional[str] = None,
             type_selector: Union[Iterable[Type['Job']], Callable[[dict], Type['Job']]] = None,
             job_config: Optional[dict] = None,
             log_level=logging.INFO, io=io_tools, backend=default_backend, **kwargs) -> 'Job':
        """
        Initialize a job
        :param job_id: id of job to find on the backend
        :param api_key: Api key for access if job is containing remote resources
        :param info_file: filename of info file to use, overwrites job id
        :param cache_path: Path to use for caching remote resources and as temporary storage
        :param type_selector: list of different job types to match
        :param job_config: configuration of the job
        :param log_level: logging level
        :param io IoTools: object managing data access and reads / writes
        :param backend: PlatformBackend object containing info on the backend to use
        """
        # Setup logging
        logging.basicConfig()
        log.root.setLevel(log_level)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("charset_normalizer").setLevel(logging.WARNING)

        backend.prepare_runtime()

        # Parse args
        args, extra_args = parse_job_args()

        if args.raygun_api_key is not None:
            from brevettiai.interfaces import raygun
            raygun.setup_raygun(api_key=args.raygun_api_key)

        # Job API: from input or input args
        job_id = job_id or args.test_id if args.model_id == "unknown" else args.model_id
        api_key = api_key or args.api_key
        job_dir = args.job_dir or backend.resource_path(job_id)
        info_file = info_file or args.info_file or io.path.join(job_dir, "info.json")
        cache_path = cache_path or args.cache_path

        io.minio.credentials = io.minio.credentials or DefaultJobCredentialsChain()

        if job_config is None:
            try:
                job_config = io.read_file(info_file)
            except KeyError:
                io.minio.credentials.set_credentials(type="JobCredentials", user=job_id, secret=api_key)
                io.resolve_access_rights(job_dir, resource_id=job_id, resource_type="job", mode="w")
                job_config = io.read_file(info_file)

            job_config = json.loads(job_config)

        # Overload config with extras
        job_config.update(io=io, backend=backend, cache_path=cache_path, **kwargs)

        # overload settings from argv
        settings_args = argparse_utils.parse_args_from_dict(extra_args, target=job_config["settings"])
        for k, v in vars(settings_args).items():
            log.warning(f"Overloading setting {k}: {v}")
        argparse_utils.overload_dict_from_args(settings_args, target=job_config["settings"])

        if type_selector is not None:
            try:
                job = parse_obj_as(type_selector, job_config)
            except (TypeError, RuntimeError):
                try:
                    job = parse_obj_as(Union[tuple(type_selector)], job_config)
                except (TypeError, RuntimeError):
                    job = type_selector(job_config).parse_obj(job_config)
        else:
            job = cls.parse_obj({**job_config, "_job_dir": job_dir})
        log.info(f"{type(job)} initialized")
        return job

    @classmethod
    def from_model_spec(cls, model, schema=None, config=None, job_dir=None, **kwargs):
        """
        Build job object from model specification
        :param model:
        :param schema:
        :param config:
        :param kwargs:
        :param job_dir:
        :return:
        """
        cdict = {} if config is None else config.__dict__

        if schema is None:
            schema = vue.SchemaBuilder().schema

        if isinstance(model["settings"], str):
            model["settings"] = json.loads(model["settings"])

        config = cls(
            name=model["name"],
            id=model["id"],
            settings=model["settings"],
            tags=model.get("tags", []),
            platform_schema=schema,
            job_dir=job_dir,
            datasets=cdict.get("datasets", []),
            api_key=cdict.get("api_key"),
            charts_url=cdict.get("charts_url"),
            complete_url=cdict.get("complete_url"),
            remote_url=cdict.get("remote_url"),
            host_name=cdict.get("host_name"),
            **kwargs,
        )
        config.model_path = model.get("model_path", None)
        return config

    def check_started(self):
        if not self._is_started:
            raise PermissionError("Call start() to use the job via the run() function")


class JobOutput(BaseModel):
    output: dict
    environment: Dict[str, Any]
    job: Job = Field(alias="config")

    class Config:
        json_encoders = custom_json_encoders
