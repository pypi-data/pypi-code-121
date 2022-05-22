import logging
import time
import itertools
import boto3
import botocore
import xarray
import ray

from sdap.utils import get_log
from sdap.data_access.drivers.Key import Key

from sdap.data_access.index.temporal import *
from sdap.data_access.index.spatial import *

from .FetchS3COGTileActor import FetchS3COGTileActor
from .FetchS3COGTileActorBuilder import FetchS3COGTileActorBuilder

logger = get_log(__name__)
logger.setLevel(logging.DEBUG)

logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('rasterio').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


class S3COG:

    def __init__(self,
                 region_name='us-west-2',
                 bucket='aqacf-nexus-stage',
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 key_pattern=[],
                 spatial_index=None,
                 temporal_index=None,
                 ):

        self.session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        self.anonymous = aws_access_key_id is None
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.bucket = bucket
        self.key_pattern = key_pattern
        self.spatial_index = spatial_index
        self.temporal_index = temporal_index

    def get_keys(self, bbox, crs, t_range):

        key_space = {'pattern': self.key_pattern}

        if self.spatial_index:
            spatial_sub_keys = self.spatial_index.get_codes(bbox, crs)
            logger.info('spatial sub keys: %s', ', '.join(spatial_sub_keys))
            key_space['spatial_key'] = spatial_sub_keys

        if self.temporal_index:
            temporal_sub_keys = self.temporal_index.get_codes(t_range)
            logger.info('temporal sub keys: %s', ', '.join(temporal_sub_keys))
            key_space['temporal_key'] = temporal_sub_keys

        s3_session = self.session.resource('s3')

        if self.anonymous:
            s3_session.meta.client.meta.events.register('choose-signer.s3.*', botocore.handlers.disable_signing)

        tested = 0
        found = 0
        key_components, key_values = zip(*key_space.items())
        for key_component_values in itertools.product(*key_values):
            tested += 1
            key_args = dict(zip(key_components, key_component_values))
            pattern = key_args.pop('pattern')
            key = Key(pattern,
                      **key_args)
            logger.debug("Test if key %s exists", key.get_str())
            if self.key_exists(key, s3_session):
                found += 1
                yield key
        logger.info("%i keys tested, %i keys found", tested, found)

    def key_exists(self, key: Key, s3_session):
        try:
            s3_session.Object(
                self.bucket,
                key.get_str()
            ).load()
            return True
        except botocore.exceptions.ClientError as e:
            logger.debug("s3 key %s not found", key.get_str())
            logger.debug(e)
            return False

    def get_all(self, request_bbox, t_range, operator, crs="epsg:4326"):
        xas = xarray.DataArray()
        xas.name = 'var'
        for xa in self.get(request_bbox, t_range, operator, request_crs=crs):
            xas = operator.consolidate([xas, xa])
            del xa

        return xas

    def get(self, request_bbox, t_range, operator, request_crs="epsg:4326"):

        # ray.init(_node_ip_address='128.149.255.29', ignore_reinit_error=True)
        ray.init(include_dashboard=True,
                 ignore_reinit_error=True,
                 #local_mode=True
                 )
        # TODO should be a function of available CPU and available RAM
        # but it is difficult to compute to amount of RAM needed for each actor
        # since it depends on the size of the data.
        num_workers = int(ray.available_resources()['CPU'])
        actor_builder = FetchS3COGTileActorBuilder()
        actor_builder.set_s3_connection(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
            anonymous=self.anonymous,
            bucket=self.bucket,
        )
        actor_builder.set_request_params(
            temporal_index=self.temporal_index,
            bbox=request_bbox,
            crs=request_crs,
            operator=operator,
            cache_ds_coordinates=True
        )
        tile_fetchers = [FetchS3COGTileActor.remote(actor_builder) for _ in range(num_workers)]

        futures = {}
        i = 0
        for key in self.get_keys(request_bbox, request_crs, t_range):
            futures[key.get_str()] = tile_fetchers[i%num_workers].get_from_key.remote(key)
            i += 1

        while futures:
            done_keys = set()
            for key_str, future in futures.items():
                if future.future().done():
                    result = future.future().result()
                    if result is not None:
                        yield result
                    done_keys.add(key_str)
            [futures.pop(key_str) for key_str in done_keys]
            time.sleep(2)

        ray.shutdown()




