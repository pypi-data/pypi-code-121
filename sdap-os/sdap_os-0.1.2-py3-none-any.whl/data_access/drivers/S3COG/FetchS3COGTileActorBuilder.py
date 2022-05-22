import logging
import boto3


from sdap.utils import get_log

from sdap.data_access.index.temporal import *

logger = get_log(__name__)
logger.setLevel(logging.DEBUG)

logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('rasterio').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


class FetchS3COGTileActorBuilder:

    def set_s3_connection(self,
            aws_access_key_id: str = None,
            aws_secret_access_key: str = None,
            region_name: str = 'us-west-2',
            anonymous: bool = True,
            bucket: str = None):
        self.anonymous = anonymous
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.bucket = bucket

    def set_request_params(self,
            temporal_index: Daily = None,
            bbox: list = None,
            crs: str = None,
            operator = None,
            cache_ds_coordinates: bool = True
            ):
        self.temporal_index = temporal_index
        self.request_bbox = bbox
        self.request_crs = crs
        self.operator = operator
        self.cache_ds_coordinates = cache_ds_coordinates

