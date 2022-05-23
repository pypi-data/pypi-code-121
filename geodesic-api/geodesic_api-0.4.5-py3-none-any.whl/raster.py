from __future__ import annotations
from typing import Optional, Sequence, Union, TYPE_CHECKING

import uuid
from datetime import timedelta, datetime

import pytz
from dateutil.parser import parse as parse_date

# from geodesic.utils.memcache import cache

if TYPE_CHECKING:
    from geodesic import Item, Dataset
from geodesic.utils.downloader import gs_re, s3_re, s3_re_other
from geodesic.utils.backoff import backoff
try:
    from osgeo import gdal

    gdal.UseExceptions()
except ImportError:
    gdal = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, desc=None):
        return iterable

if gdal is not None:
    resample_lut = {
        "nearest": gdal.GRA_NearestNeighbour,
        "bilinear": gdal.GRA_Bilinear,
        "lanczos": gdal.GRA_Lanczos,
        "cubic": gdal.GRA_Cubic,
        "cubic_spline": gdal.GRA_CubicSpline,
    }
else:
    resample_lut = {}


def group_by_threshold(items, threshold):
    """
    Group rasters together that are within some threshold of each other.
    """
    timestamps_items_ids = sorted([(item.datetime, item, item.id) for item in items], key=lambda x: x[0])

    groups = []
    group = []
    last_timestamp = None

    for timestamp, item, item_id in timestamps_items_ids:

        if last_timestamp is None:
            last_timestamp = timestamp
        if timestamp > (last_timestamp + threshold):
            groups.append(group)
            group = [(timestamp, item, item_id)]

            last_timestamp = timestamp
            continue

        group.append((timestamp, item, item_id))
        last_timestamp = timestamp
    if len(group):
        groups.append(group)

    return groups


def group_static(items):
    """
    Group all together and mosaic.
    """
    groups = [
        [
            (None, item, item.id)
            for item in items
        ]
    ]

    return groups


def is_offset_aware(t):
    if t.tzinfo is not None and t.tzinfo.utcoffset(t) is not None:
        return True
    return False


def group_by_bins(items, bins):
    timestamps_items_ids = list(
        sorted([(item.datetime, item, item.id) for item in items], key=lambda x: x[0])
    )

    groups = [None for _ in bins]

    for i, (start, end) in enumerate(bins):
        if not isinstance(start, datetime):
            start = parse_date(start)
        if not isinstance(end, datetime):
            end = parse_date(end)
        if not is_offset_aware(start):
            start = pytz.UTC.localize(start)
        if not is_offset_aware(end):
            end = pytz.UTC.localize(end)
        group = []
        for t, item, iid in timestamps_items_ids:
            if (t >= start) and (t < end):
                group.append((start, item, iid))
        if group:
            groups[i] = group
        else:
            groups[i] = [(start, None, None)]

    return groups


def group_temporal(items):
    """
    Group each image only with itself, there will be a time bin for each iamge.
    """
    timestamps_items_ids = sorted([(item.datetime, item, item.id) for item in items], key=lambda x: x[0])

    groups = [
        [(timestamp, item, item_id)]
        for timestamp, item, item_id in timestamps_items_ids
    ]

    return groups


class Raster:
    """Handles raster data, typically MSI
    A class used as the main interface to raster data.
    Args:
        item: A Geodesic python api item object.
        dataset: A Geodesic Python API dataset object. Default: ``None``.
    """

    def __init__(self, item: Item, dataset: Dataset = None) -> None:

        self.item = item
        self.dataset = dataset

    def export_raster(
        self,
        bbox: Optional[Sequence] = None,
        bands: Sequence = ["red", "green", "blue"],
        image_size: Optional[Sequence] = None,
        pixel_size: Optional[Union[float, Sequence[float]]] = None,
        resample: str = "nearest",
        input_srs: str = "EPSG:4326",
        output_srs: str = "EPSG:3857",
    ):

        bands = lookup_bands(bands, self.dataset)
        mosaic = mosaic_bands(bands, self.item)

        width = height = None
        x_res = y_res = None

        if image_size is not None:
            height, width = image_size

        if pixel_size is not None:
            try:
                x_res, y_res = pixel_size
            except Exception:
                x_res = y_res = pixel_size

        if x_res is None:
            x_res = y_res = 30.0

        options = gdal.WarpOptions(
            format="GTiff",
            outputBounds=bbox,
            outputBoundsSRS=input_srs,
            resampleAlg=resample_lut.get(resample, gdal.GRA_NearestNeighbour),
            xRes=x_res,
            yRes=y_res,
            width=width,
            height=height,
            dstSRS=output_srs,
        )

        try:
            d = backoff(gdal.Warp("/vsimem/test.tiff", mosaic, options=options))
        except Exception:
            mosaic = None
            d = None
            return

        mosaic = None

        x = d.ReadAsArray()
        d = None

        return x


class RasterCollection:
    """
    For operations on a list of rasters (as Items)
    """

    def __init__(self, items: Sequence[Item], dataset=None, download_files=False, delete_when_complete=True) -> None:

        self.items = items
        self.download_files = download_files
        self.delete_when_complete = delete_when_complete

        try:
            first_item = next(iter(items))
        except StopIteration:
            raise ValueError("no items provided to RasterCollection")

        # Is a geodesic.features.Item?
        if first_item['type'] != "Feature":
            raise ValueError("unable to check datetime attribute. Is this a `geodesic.Item`?")

        dt = getattr(first_item, 'datetime', None)
        if dt is None:
            self.static = True
        else:
            self.static = False

        self.dataset = dataset

    def export_rasters(
        self,
        bbox: Optional[Sequence] = None,
        bands: Sequence = ["red", "green", "blue"],
        image_size: Optional[Sequence] = None,
        pixel_size: Optional[Union[float, Sequence[float]]] = None,
        input_srs: str = "EPSG:4326",
        output_srs: str = "EPSG:3857",
        resample: str = "nearest",
        input_nodata: Union[int, float] = 0,
        output_nodata: Union[int, float] = 0,
        output_dtype: Union[np.dtype, str] = np.float32,
        mosaic_threshold: timedelta = None,
        time_bins: Optional[Sequence] = None,
        verbose=False,
        progress_func=tqdm,
    ):

        width = height = None
        x_res = y_res = None

        if (pixel_size is not None) and (image_size is not None):
            raise ValueError("You must only specify one of pixel_size or image_size")

        if image_size is not None:
            height, width = image_size

        if pixel_size is not None:
            try:
                x_res, y_res = pixel_size
            except Exception:
                x_res = y_res = pixel_size

        if x_res is None and image_size is None:  # If nothing specified use pixel_size = 30
            x_res = y_res = 30.0

        bands = lookup_bands(bands, self.dataset)

        # Mosaic group images together according to some spatiotemporal rule.
        if self.static:
            groups = group_static(self.items)
        elif time_bins is not None:
            groups = group_by_bins(self.items, time_bins)
        elif mosaic_threshold is not None:
            groups = group_by_threshold(self.items, mosaic_threshold)
        else:
            groups = group_temporal(self.items)

        options = gdal.WarpOptions(
            format="GTiff",
            outputBounds=bbox,
            outputBoundsSRS=input_srs,
            resampleAlg=resample_lut.get(resample, gdal.GRA_NearestNeighbour),
            xRes=x_res,
            yRes=y_res,
            width=width,
            height=height,
            srcNodata=input_nodata,
            dstNodata=output_nodata,
            dstSRS=output_srs,
        )

        for i, group in enumerate(progress_func(groups, desc="warping")):
            items = []
            if group is not None:

                items = [g[1] for g in group if g is not None and g[1] is not None]

                if self.download_files:
                    for item in items:
                        for band in bands:
                            item.assets[band].download()

                if not self.static:
                    dt = group[0][0].isoformat()
                else:
                    dt = None

            stack = []
            # If there are items to process
            if items:

                warp = str(uuid.uuid4())
                vsimem_path = f"/vsimem/{warp}.tif"

                for band in bands:
                    uris = [
                        get_uri(item.assets[band], self.download_files)
                        for item in items
                    ]

                    try:
                        d = backoff(gdal.Warp)(vsimem_path, uris, options=options)
                        if self.delete_when_complete and self.download_files:
                            for item in items:
                                del item.assets[band].local

                    except Exception:
                        try:
                            gdal.Unlink(vsimem_path)
                        except Exception:
                            pass

                        d = None
                        continue

                    arr = d.ReadAsArray()

                    # Add to the stack
                    stack.append(arr)
                if stack:
                    x = np.stack(stack)
                    x = x.astype(output_dtype)
                else:
                    x = None

                try:
                    gdal.Unlink(vsimem_path)
                except Exception as e:
                    print(f"failed Unlink: {e}")
                d = None
            else:
                x = None

            yield i, len(groups), x, dt


def get_uri(asset, download=False):
    if download:
        return asset.local
    return format_uri(asset.href)


def lookup_bands(bands: Sequence[str], dataset: Dataset):
    if dataset is not None:
        extensions = dataset.stac_extensions
        assets = dataset.item_assets
    else:
        assets = {}
        extensions = []
    has_eo_ext = "eo" in extensions
    has_item_assets_ext = "item-assets" in extensions

    band_keys = []
    for band in bands:
        # Check in the item assets for a commonName for the band
        if has_eo_ext and has_item_assets_ext:
            for ia, a in assets.items():
                eo = a.get("eo", {})
                for b in eo.get("bands", []):
                    if b.get("commonName") == band:
                        band = ia
                        break

        band_keys.append(band)
    return band_keys


@backoff
def load_dataset(path):
    d = gdal.Open(path)
    if d is None:
        raise ValueError("unable to load raster!")
    return d


def format_uri(uri):
    m = gs_re.match(uri)

    if m:
        bucket = m.group(1)
        key = m.group(2)

        return f"/vsigs/{bucket}/{key}"

    m = s3_re.match(uri)

    if m:
        bucket = m.group(1)
        key = m.group(2)

        return f"/vsis3/{bucket}/{key}"

    for _re, (bucket_index, key_index) in s3_re_other:
        m = _re.match(uri)
        if m:
            bucket = m.group(bucket_index)
            key = m.group(key_index)

            return f"/vsis3/{bucket}/{key}"

    if (
        uri.startswith("http://")
        or uri.startswith("https://")
        or uri.startswith("ftp://")
    ):
        return "/vsicurl/" + uri

    return uri


def mosaic_bands(bands: Sequence[str], item: Item):

    band_files = []
    for band in bands:
        if band not in item.assets:
            assets = ",".join([k for k in item.assets])
            raise ValueError(
                "band '{0}' does not exist for this item. Available assets are: {1}".format(
                    band, assets
                )
            )

        asset = item.assets[band]
        if asset.local:
            uri = asset.local
        else:
            uri = asset.href

        band_files.append(format_uri(uri))

    vrt_uuid = str(uuid.uuid4())

    options = gdal.BuildVRTOptions(separate=True)

    datasets = [
       load_dataset(p)
       for p in band_files
    ]

    vrt = backoff(gdal.BuildVRT(f"/vsimem/{vrt_uuid}.vrt", datasets, options=options))

    return vrt
