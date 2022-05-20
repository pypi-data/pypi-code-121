import re
import datetime
from typing import List, Union
from dateutil.parser import isoparse
import numpy as np
from geodesic.account.projects import ProjectDescr
from geodesic.bases import APIObject
from geodesic.descriptors import BoolDescr, DTypeDescr, DatetimeIntervalDescr, DictDescr, IntDescr, ListDescr, \
                                 NumberDescr, RegexDescr, StringDescr, TupleDescr, TypeConstrainedDescr, BaseDescr, \
                                 URLDescr
from geodesic.entanglement.dataset import DatasetDescr
from geodesic.stac import Item, Feature
from geodesic.utils import datetime_to_utc

__all__ = [
    "GlobalProperties",
    "AssetSpec",
    "Container",
    "Step",
    "StepInput",
    "StepOutput",
    "Webhook",
    "Bucket",
    "Equal",
    "User",
    "TemporalBinning"
]


bin_size_re = re.compile(r'^\d+(ms|us|ns|[WDhms]){1}')


class Equal(APIObject):
    """Temporal binning with equal bin size (either by count or size)
    """
    bin_size = RegexDescr(bin_size_re, doc="the bin size, in time units for each bin")
    bin_count = IntDescr(doc="the count of bins to create")


class User(APIObject):
    """Temporal binning by user specified bins.
    """
    omit_empty = BoolDescr(doc="don't create a space for empty bins in resulting output")

    def __init__(self, **spec):
        self.omit_empty = False
        self._bins = None
        super().__init__(**spec)

    @property
    def bins(self):

        if self._bins is not None:
            return self._bins
        b = self.get('bins', [])
        if not isinstance(b, list):
            raise ValueError("bins must be a list of list of datetimes")
        out = []
        for d in b:
            if d is None:
                raise ValueError("bin cannot be None")
            dates = d
            try:
                out.append([d for d in map(isoparse, dates)])
            except Exception as e:
                raise e
        self._bins = out
        return out

    @bins.setter
    def bins(self, v: List[List[Union[datetime.datetime, str]]]):
        b = []
        for d in v:
            if len(d) != 2:
                raise ValueError("bins must be a list of pairs of start/end datetime bin edges")

            if isinstance(d[0], str):
                for dt in d:
                    try:
                        isoparse(dt)
                    except Exception as e:
                        raise ValueError("bin edges must be datetimes or parsable rfc3339 strings") from e
                b.append(list(d))

            elif isinstance(d[0], datetime.datetime):
                b.append([datetime_to_utc(dt).isoformat() for dt in d])
        self._set_item('bins', b)


class TemporalBinning(APIObject):
    """Temporal binning is a class to represent the temporal binning in a series request.

    Args:
        spec(dict): The dict to initialize the class with.
    """
    equal = TypeConstrainedDescr((Equal, dict), doc="specify Equal time binning")
    user = TypeConstrainedDescr((User, dict), doc="specify time bins defined by User time binning")
    reference = StringDescr(doc="reference the time bins to another asset in the Job")


class Webhook(APIObject):
    """A webhook triggered on completion of a step in a Tesseract Job

    NotImplemented

    A future version of Tesseract will allow webhooks when a job step has completed, which will POST
    information to a url with specified headers and credentials
    """

    url = URLDescr(doc="url")
    headers = DictDescr(doc="dictionary with string keys to string values headers to pass along: {'key': 'value'}")
    credentials = StringDescr(doc="name of the credential to use (geodesic.accounts.Credential)")


class Container(APIObject):
    """A container that runs arbitrary code to execute a model for aggregation, machine learning, etc

    NotImplemented

    """
    repository = StringDescr(doc="the docker repository to pull from", default="docker.io")
    image = StringDescr(doc="the name of the image to use")
    tag = StringDescr(doc="the tag of the image to use")
    pull_secret_credential = StringDescr(doc="name of the credential to use to pull the container")


class StepInput(APIObject):
    """An input for a processing step
    """
    asset_name = StringDescr(doc="name of the asset to use as input")
    slice = StringDescr(doc="a slice into the asset, if it's a tensor, to use. This is numpy array slicing extended by"
                            " a '|' following by the chunk size in each dimension. E.g.: [:|30, 3, 256, 256] would use"
                            " everything in the input array with chunks of shape (30, 3, 256, 256). These would"
                            " get used by your container and your container should process data of this shape.")


class StepOutput(APIObject):
    """An output for a processing step
    """
    asset_name = StringDescr(doc="name of an asset this step emits")
    type = RegexDescr(r"((?:tensor)|(?:features)|(?:records))", doc="the type of output")
    shape = TupleDescr(
        doc="the shape of the output from this asset from the container. Even if the container performs a reduction, "
            "please specify the full dimensions in the order (time, band/feature, rows, columns). (1, 1, 1, 1) for "
            " scaler output",
        min_len=4,
        max_len=4)


class Step(APIObject):
    """A step in a Tesseract Job

    NotImplemented

    """
    name = StringDescr(doc="the name of this step")
    type = StringDescr(doc="the type of this step (model, rechunk)")
    inputs = ListDescr(item_type=(StepInput, dict), doc="a list of inputs for this step")
    outputs = ListDescr(item_type=(StepOutput, dict), doc="a list of outputs for this step")
    container = TypeConstrainedDescr((Container, dict))
    gpu = BoolDescr(doc="make the step run on a machine with GPU resources", default=False)
    workers = IntDescr(doc="number of workers to run for this step")


class Bucket(APIObject):
    prefix = StringDescr(doc="all output will be written to this prefix")
    platform = StringDescr(doc="the platform for this bucket (aws, gcp, azure)")
    bucket = StringDescr(doc="name of the bucket or container")
    region = StringDescr(doc="storage region (AWS)")
    credentials = StringDescr(doc="credentials to access this bucket")
    requester_pays = BoolDescr(doc="requester pays to access bucket", default=False)


class GlobalProperties(APIObject):
    """GlobalProperties that will be applied to all assets if they have empty values

    Only contains a subset of the parameters for an asset.

    Args:
        **spec(dict): A dictionary that can be used to initialize the object. Optional.
    """

    shape = TupleDescr(doc="the shape of the output for this asset (rows, columns)", min_len=2, max_len=2)
    pixel_size = TupleDescr(doc="the size of each pixel in the output SRS (x, y)", min_len=2, max_len=2)
    pixel_dtype = DTypeDescr(doc="output pixel dtype")
    chip_size = IntDescr(doc="size of the chips to break work into (default=512, max=2000)")
    project = ProjectDescr(doc="the project the source dataset belongs to. You must have read access to this project")
    output_no_data = ListDescr(
        item_type=(int, float, complex),
        doc="set the value to be ignored and treated as nodata in the output")
    compression = RegexDescr(regex=r'((?:zlib)|(?:blosc)|(?:none))', doc="the compression algorithm for output data")
    datetime = DatetimeIntervalDescr(doc="the datetime interval to be used to query for matching data")
    temporal_binning = TypeConstrainedDescr((TemporalBinning, dict), doc="the temporal binning strategy")

    def __init__(self, **spec):

        self._compression = None
        self._project = None
        self._datetime = None
        self._output_no_data = None
        self._temporal_binning = None

        for k, v in spec.items():
            setattr(self, k, v)


resample_options = [
    'nearest',
    'bilinear',
    'cubic',
    'cubicspline',
    'lanczos',
    'average',
    'mode',
    'max',
    'min',
    'median',
    'q1',
    'q3',
    'sum'
]


class FeatureAggregation(APIObject):
    """FeatureAggregation specifies how features should be handled while rasterizing
    """
    value = TypeConstrainedDescr((str, float, int, complex))
    aggregation_rules = ListDescr(item_type=str)
    groups = ListDescr(item_type=dict)


class AssetSpec(APIObject):
    """AssetSpec is a class to represent the requested output assets in a tesseract job.

    Args:
        **spec(dict): A dictionary that can be used to initialize the object. Optional.

    """
    name = StringDescr(doc="name of this asset")
    dataset = DatasetDescr(doc="the dataset to derive this asset from")
    assets = ListDescr(item_type=str, doc="the assets within the dataset to use. "
                                          "Each will be separate band(s)/feature(s)")
    asset_band_counts = ListDescr(item_type=(int,), doc="list of band counts for each asset. If empty, Tesseract will"
                                                        " infer from the dataset spec or assume it's 1 and return"
                                                        " a warning")
    resample = StringDescr(
        one_of=resample_options,
        doc=f"resampling method to use, one of {', '.join(resample_options)}")
    project = ProjectDescr(doc="the project the source dataset belongs to. You must have read access to this project")
    shape = TupleDescr(doc="the shape of the output for this asset (rows, columns)", min_len=2, max_len=2)
    pixel_size = TupleDescr(doc="the size of each pixel in the output SRS (x, y)", min_len=2, max_len=2)
    pixel_dtype = DTypeDescr(doc="output pixel dtype")
    chip_size = IntDescr(doc="size of the chips to break work into (default=512, max=2000)")
    compression = StringDescr(one_of=['zlib', 'blosc', 'none'], doc="the compression algorithm for output data")
    input_no_data = ListDescr(
        item_type=(int, float, complex),
        doc="set the value to be ignored and treated as nodata in the input")
    output_no_data = ListDescr(
        item_type=(int, float, complex),
        doc="set the value to be ignored and treated as nodata in the output")
    ids = ListDescr(item_type=(int, str), doc="list of item IDs to be used to query from the specified dataset")
    datetime = DatetimeIntervalDescr(doc="the datetime interval to be used to query for matching data")
    query = DictDescr(doc="a dictionary formatted like"
                          "https://github.com/radiantearth/stac-api-spec/"
                          "blob/master/item-search/README.md#query-extension"
                          "to be used to filter input data")
    filter = DictDescr(doc="a dictionary representing a JSON CQL2 filter as defined by the OGC spec: "
                           "https://github.com/opengeospatial/ogcapi-features/tree/master/cql2")
    feature_aggregation = TypeConstrainedDescr(
        (FeatureAggregation, dict), doc="how features should be aggregated into a resulting raster see REST API docs"
                                        " for further info: https://docs.seerai.space/tesseract/v1/index.html")
    stac_items = ListDescr(item_type=(dict, Feature, Item), doc="a list of Tesseract features/items to use in lieu"
                                                                " of a query", dict_name='items')
    as_feature = BoolDescr(doc="treat items as features (e.g. for Rasterize) instead of STAC items (usually Warp)")
    fill_value = NumberDescr(doc="anywhere there is no calculated data, will be replaced with this")
    temporal_binning = TypeConstrainedDescr((TemporalBinning, dict), doc="the temporal binning strategy")
    hooks = ListDescr(item_type=(Webhook, dict), doc="webhooks to be called when asset is completed")

    def __init__(self, **spec):
        # Set defaults
        self.resample = 'nearest'
        self.fill_value = 0
        self.pixel_dtype = np.float32
        self.compression = 'blosc'
        self.project = 'global'

        for k, v in spec.items():
            if k == 'items':
                k = 'stac_items'
            setattr(self, k, v)


class AssetSpecListDescr(BaseDescr):
    """a list of validated AssetSpecs

    AssetSpecListDescr is a list of AssetSpec items, this sets/returns a list no matter what,
    it doesn't raise an attribute error.

    __get__ returns the list, creating it on the base object if necessary
    __set__ sets the list after validating that it is a list
    """
    def _get(self, obj: object, objtype=None) -> list:
        # Try to get the private attribute by name (e.g. '_assets')
        assets = getattr(obj, self.private_name, None)
        if assets is not None:
            # Return it if it exists
            return assets

        try:
            assets = self._get_object(obj)

            isAssetSpec = True
            for asset in assets:
                if not isinstance(asset, AssetSpec):
                    isAssetSpec = False
                    break
            if not isAssetSpec:
                self._set(obj, assets)
                return self._get(obj)

        except KeyError:
            assets = []
            self._set_object(obj, assets)
        setattr(obj, self.private_name, assets)
        return assets

    def _set(self, obj: object, value: object) -> None:
        assets = [
            AssetSpec(**asset) for asset in value
        ]
        setattr(obj, self.private_name, assets)
        self._set_object(obj, assets)

    def _validate(self, obj: object, value: object) -> None:
        if not isinstance(value, (list, tuple)):
            raise ValueError(f"'{self.public_name}' must be a tuple or list")
        if len(value) > 0:
            for asset in value:
                if not isinstance(asset, (dict, AssetSpec)):
                    raise ValueError(f"each value must be a dict/AssetSpec, not '{type(asset)}'")
