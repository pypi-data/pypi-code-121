import logging
import numpy as np
import ray
import rioxarray
import rasterio as rio
from rasterio.session import AWSSession
from rasterio.errors import RasterioIOError
import boto3


from pyproj import Transformer, CRS

from sdap.utils import get_log
from sdap.operators import OperatorProcessingException
from sdap.data_access.index.temporal import *
from .FetchS3COGTileActorBuilder import FetchS3COGTileActorBuilder

logger = get_log(__name__)
logger.setLevel(logging.DEBUG)

logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('rasterio').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)







@ray.remote(max_task_retries=0)
class FetchS3COGTileActor:
    # TODO have abstract objects for spatial_index and temporal_index , instead of Daily used here
    # TODO same for operator
    def __init__(self, actor_builder: FetchS3COGTileActorBuilder):
        self.anonymous = actor_builder.anonymous
        self.session = boto3.Session(
            aws_access_key_id=actor_builder.aws_access_key_id,
            aws_secret_access_key=actor_builder.aws_secret_access_key,
            region_name=actor_builder.region_name
        )
        self.bucket = actor_builder.bucket
        self.temporal_index = actor_builder.temporal_index
        self.bbox = actor_builder.request_bbox
        self.crs = actor_builder.request_crs
        self.operator = actor_builder.operator
        self.cache_ds_coordinates = actor_builder.cache_ds_coordinates
        self.ds_bbox = None
        self.mask = None
        self.request_x = None
        self.request_y = None

    @staticmethod
    def convert_bbox(bbox, source_crs, target_crs=CRS.from_string("epsg:4326")):

        if source_crs.equals(target_crs):
            return bbox
        else:
            transformer = Transformer.from_crs(source_crs,
                                               target_crs,
                                               skip_equivalent=True,
                                               always_xy=True
                                               )

            target_bbox = transformer.transform_bounds(left=bbox[0],
                                                       bottom=bbox[1],
                                                       right=bbox[2],
                                                       top=bbox[3]
                                                       )
            return list(target_bbox)

    def add_request_coordinates(self, xas):

        #if not self.cache_ds_coordinates or self.request_y is None:
        xv, yv = np.meshgrid(xas.x, xas.y, indexing='ij')

        source_crs = CRS(xas.spatial_ref.crs_wkt)
        if source_crs.equals(self.crs):
            self.request_x, self.request_y = xv, yv
        else:
            transformer = Transformer.from_crs(source_crs,
                                               self.crs,
                                               skip_equivalent=True,
                                               always_xy=True
                                               )

            self.request_x, self.request_y = transformer.transform(xv, yv)
        logger.debug("cached x,y dimensions are x %i, y %i", len(self.request_x), len(self.request_x[0]))

        logger.debug("add request coordinates to grid with dimension x %i, y %i", len(xas.x), len(xas.y))

        xas.coords['request_x'] = (('x', 'y'), self.request_x)
        xas.coords['request_y'] = (('x', 'y'), self.request_y)

        return xas

    def get_from_key(self, key):
        path = f's3://{self.bucket}/{key.get_str()}'

        try:
            result = None
            aws_session_kwargs = {'aws_unsigned': self.anonymous}
            # CPL_CURL_VERBOSE=True
            with rio.Env(session=AWSSession(self.session, **aws_session_kwargs)):
                logger.debug("fetching %s", path)
                with rio.open(path) as f:
                    rds = rioxarray.open_rasterio(f)
                    #if not self.cache_ds_coordinates or self.ds_bbox is None:
                    ds_crs = CRS(rds.spatial_ref.crs_wkt)
                    self.ds_bbox = FetchS3COGTileActor.convert_bbox(self.bbox, CRS.from_string(self.crs), ds_crs)

                    rds = rds.rio.clip_box(
                                    minx=self.ds_bbox[0],
                                    maxx=self.ds_bbox[2],
                                    miny=self.ds_bbox[1],
                                    maxy=self.ds_bbox[3]
                    )
                    rds = self.add_request_coordinates(rds)

                    #if not self.cache_ds_coordinates or self.mask is None:
                    mask_x = (rds.request_x >= self.bbox[0]) & (rds.request_x <= self.bbox[2])
                    mask_y = (rds.request_y >= self.bbox[1]) & (rds.request_y <= self.bbox[3])
                    self.mask = mask_x & mask_y
                    rds = rds.where(self.mask, drop=True)

                    rds.data[rds.data == rds._FillValue] = np.nan
                    if not np.isnan(rds.data).all():
                        rds = rds.expand_dims(
                            {'time': [self.temporal_index.get_datetime(key.get_temporal_key())]},
                            axis=0
                        )
                        rds.name = 'var'
                        result = self.operator.tile_calc(rds)
                        del rds
                    else:
                        logger.debug("no valid data in subset for key %s, ignore", key)
            return result

        except RasterioIOError:
            logger.debug("object not found from key %s, ignore", key)
            return None
        except OperatorProcessingException:
            logger.debug("operator fail on key %s, ignore", key)
            return None
