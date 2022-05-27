import os
import logging
import numpy as np
import urllib
import requests
from brevettiai.io import path as path_utils
from .tag import Tag
from pydantic import Field, BaseModel
from typing import Union, List
from uuid import UUID

log = logging.getLogger(__name__)


class PlatformBackend(BaseModel):
    host: str = Field(default_factory=lambda: os.getenv("BREVETTIAI_HOST_NAME", "https://platform.brevetti.ai"))
    output_segmentation_dir: str = Field(default="output_segmentations")
    bucket_region: str = Field(default_factory=lambda: os.getenv("AWS_REGION", "eu-west-1"))
    data_bucket: str = Field(default_factory=lambda: os.getenv("BREVETTIAI_DATA_BUCKET", "s3://data.criterion.ai"))
    custom_job_id: str = Field(default="a0aaad69-c032-41c1-a68c-e9a15a5fb18c",
                               description="uuid of model type to use for custom jobs")
    custom_report_id: str = Field(default="bdc5b6fa-f96b-4afa-b0dd-e6ed256e956a",
                                  description="uuid of model type to use for custom test reports linked to custom jobs")

    @property
    def s3_endpoint(self):
        return f"s3.{self.bucket_region}.amazonaws.com"

    def resource_path(self, uuid: Union[str, UUID]) -> str:
        """
        Get location of a resource
        """
        return path_utils.join(self.data_bucket, str(uuid))

    def prepare_runtime(self):
        # Determine runtime
        on_sagemaker = os.environ.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI") is not None

        # Initialize services
        if on_sagemaker:
            from brevettiai.interfaces import sagemaker
            sagemaker.load_hyperparameters_cmd_args()

    def get_download_link(self, path):
        if path.startswith("s3://"):
            target = path[5:].split("/", 1)[1]
            return f"{self.host}/download?path={urllib.parse.quote(target, safe='')}"
        else:
            raise ValueError("Can only provide download links on s3")

    def get_root_tags(self, id, api_key) -> List[Tag]:
        r = requests.get(f"{self.host}/api/resources/roottags?key={api_key}&id={id}")
        if r.ok:
            return [Tag.parse_obj(x) for x in r.json()]
        else:
            log.warning("Could not get root tags")
            return []

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
        rm_keys = [self.data_bucket, ".tiles/", "/dzi.json"]
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

        if zoom is not None:
            url_info["zoom"] = zoom

        return "https://platform.brevetti.ai/data/{}?".format(dataset_id) + urllib.parse.urlencode(url_info)

    @property
    def custom_model_type(self):
        from .web_api_types import ModelType
        return ModelType(id=self.custom_job_id, name="custom job")

    @property
    def custom_report_type(self):
        from .web_api_types import ReportType
        return ReportType(id=self.custom_report_id, name="custom report", created="",status=1,
                          can_run_on_projects=False, can_run_on_applications=False, can_run_on_models=True,
                          max_runtime_in_seconds=1, instance_count=1, volume_size_in_gb=100, model_type_ids=[])

backend = PlatformBackend()
