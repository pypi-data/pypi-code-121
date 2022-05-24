# -*- coding: utf-8 -*-
import os
from collections import namedtuple
from io import BytesIO
from math import ceil

import requests
from PIL import Image
from shapely.affinity import rotate, scale, translate
from shapely.geometry import LinearRing
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from arkindex_worker import logger

# See http://docs.python-requests.org/en/master/user/advanced/#timeouts
DOWNLOAD_TIMEOUT = (30, 60)

BoundingBox = namedtuple("BoundingBox", ["x", "y", "width", "height"])


def open_image(path, mode="RGB", rotation_angle=0, mirrored=False):
    """
    Open an image from a path or a URL
    """
    if (
        path.startswith("http://")
        or path.startswith("https://")
        or not os.path.exists(path)
    ):
        image = download_image(path)
    else:
        try:
            image = Image.open(path)
        except (IOError, ValueError):
            image = download_image(path)

    if image.mode != mode:
        image = image.convert(mode)

    if mirrored:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)

    if rotation_angle:
        image = image.rotate(-rotation_angle, expand=True)

    return image


def download_image(url):
    """
    Download an image and open it with Pillow
    """
    assert url.startswith("http"), "Image URL must be HTTP(S)"

    # Download the image
    # Cannot use stream=True as urllib's responses do not support the seek(int) method,
    # which is explicitly required by Image.open on file-like objects
    try:
        resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
    except requests.exceptions.SSLError:
        logger.warning(
            "An SSLError occurred during image download, retrying with a weaker and unsafe SSL configuration"
        )

        # Saving current ciphers
        previous_ciphers = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS

        # Downgrading ciphers to download the image
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"
        resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT)

        # Restoring previous ciphers
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = previous_ciphers

    resp.raise_for_status()

    # Preprocess the image and prepare it for classification
    image = Image.open(BytesIO(resp.content))
    logger.info(
        "Downloaded image {} - size={}x{}".format(url, image.size[0], image.size[1])
    )

    return image


def polygon_bounding_box(polygon):
    x_coords, y_coords = zip(*polygon)
    x, y = min(x_coords), min(y_coords)
    width, height = max(x_coords) - x, max(y_coords) - y
    return BoundingBox(x, y, width, height)


def _retry_log(retry_state, *args, **kwargs):
    logger.warning(
        f"Request to {retry_state.args[0]} failed ({repr(retry_state.outcome.exception())}), "
        f"retrying in {retry_state.idle_for} seconds"
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2),
    retry=retry_if_exception_type(requests.RequestException),
    before_sleep=_retry_log,
    reraise=True,
)
def _retried_request(url):
    resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
    resp.raise_for_status()
    return resp


def download_tiles(url):
    """
    Reconstruct a full IIIF image on servers that cannot serve the full-sized image using tiles.
    """
    if not url.endswith("/"):
        url += "/"
    logger.debug("Downloading image information")
    info = _retried_request(url + "info.json").json()

    image_width, image_height = info.get("width"), info.get("height")
    assert image_width and image_height, "Missing image dimensions in info.json"
    assert info.get(
        "tiles"
    ), "Image cannot be retrieved at full size and tiles are not supported"

    # Take the biggest available tile size
    tile = sorted(info["tiles"], key=lambda tile: tile.get("width", 0), reverse=True)[0]
    tile_width = tile["width"]
    # Tile height is optional and defaults to the width
    tile_height = tile.get("height", tile_width)

    full_image = Image.new("RGB", (image_width, image_height))

    for tile_x in range(ceil(image_width / tile_width)):
        for tile_y in range(ceil(image_height / tile_height)):
            region_x = tile_x * tile_width
            region_y = tile_y * tile_height

            # Prevent trying to crop outside the bounds of an image
            region_width = min(tile_width, image_width - region_x)
            region_height = min(tile_height, image_height - region_y)

            logger.debug(f"Downloading tile {tile_x},{tile_y}")
            resp = _retried_request(
                f"{url}{region_x},{region_y},{region_width},{region_height}/full/0/default.jpg"
            )

            tile_img = Image.open(BytesIO(resp.content))

            # Some bad IIIF image server implementations may sometimes return tiles with a few pixels of difference
            # with the expected sizes, causing Pillow to raise ValueError('images do not match').
            actual_width, actual_height = tile_img.size
            if actual_width < region_width or actual_height < region_height:
                # Fail when tiles are too small
                raise ValueError(
                    f"Expected size {region_width}×{region_height} for tile {tile_x},{tile_y}, "
                    f"but got {actual_width}×{actual_height}"
                )

            if actual_width > region_width or actual_height > region_height:
                # Warn and crop when tiles are too large
                logger.warning(
                    f"Cropping tile {tile_x},{tile_y} from {actual_width}×{actual_height} "
                    f"to {region_width}×{region_height}"
                )
                tile_img = tile_img.crop((0, 0, region_width, region_height))

            full_image.paste(
                tile_img,
                box=(
                    region_x,
                    region_y,
                    region_x + region_width,
                    region_y + region_height,
                ),
            )

    return full_image


def trim_polygon(polygon, image_width: int, image_height: int):
    """
    This method takes as input:
    - a polygon: a list or tuple of points
    - image_width, image_height: an image's dimensions
    and outputs a new polygon, whose points are all located within the image.
    If some of the polygon's points are not inside the image, the polygon gets trimmed,
    which means that some points can disappear or their coordinates be modified.
    """

    assert isinstance(
        polygon, (list, tuple)
    ), "Input polygon must be a valid list or tuple of points."
    assert all(
        isinstance(point, (list, tuple)) for point in polygon
    ), "Polygon points must be tuples or lists."
    assert all(
        len(point) == 2 for point in polygon
    ), "Polygon points must be tuples or lists of 2 elements."
    assert all(
        isinstance(point[0], int) and isinstance(point[1], int) for point in polygon
    ), "Polygon point coordinates must be integers."
    assert any(
        point[0] <= image_width and point[1] <= image_height for point in polygon
    ), "This polygon is entirely outside the image's bounds."

    trimmed_polygon = [
        [
            min(image_width, max(0, x)),
            min(image_height, max(0, y)),
        ]
        for x, y in polygon
    ]

    updated_polygon = []
    for point in trimmed_polygon:
        if point not in updated_polygon:
            updated_polygon.append(point)

    # Add back the matching last point, if it was present in the original polygon
    if polygon[-1] == polygon[0]:
        updated_polygon.append(updated_polygon[0])

    return updated_polygon


def revert_orientation(element, polygon):
    """Update the coordinates of the polygon of a child element based on the orientation of
    its parent.

    :param element: Parent element
    :type element: Element|CachedElement
    :param polygon: Polygon corresponding to the child element.
    :type polygon: list
    :return: A polygon with updated coordinates
    :rtype: list
    """
    from arkindex_worker.models import Element
    from arkindex_worker.cache import CachedElement

    assert element and isinstance(
        element, (Element, CachedElement)
    ), "element shouldn't be null and should be an Element or CachedElement"
    assert polygon and isinstance(
        polygon, list
    ), "polygon shouldn't be null and should be a list"
    # Rotating with Pillow can cause it to move the image around, as the image cannot have negative coordinates
    # and must be a rectangle.  This means the origin point of any coordinates from an image is invalid, and the
    # center of the bounding box of the rotated image is different from the center of the element's bounding box.
    # To properly undo the mirroring and rotation implicitly applied by open_image, we first need to find the center
    # of the rotated bounding box.
    if isinstance(element, Element):
        assert (
            element.zone and element.zone.polygon
        ), "element should have a zone and a polygon"
        parent_ring = LinearRing(element.zone.polygon)
    elif isinstance(element, CachedElement):
        assert element.polygon, "cached element should have a polygon"
        parent_ring = LinearRing(element.polygon)

    rotated_ring = rotate(parent_ring, element.rotation_angle, origin="center")

    # This rotated ring might have negative coordinates, so we get the vector that Pillow applies to offset the
    # image to non-negative coordinates using the rotated bounding box.
    offset_x, offset_y, _, _ = rotated_ring.bounds

    # This uses the same calculation as what Shapely does for rotate/scale(origin='center').
    # We will use this below to rotate around the center of the parent bounding box and not of each child polygon.
    # https://github.com/Toblerity/Shapely/blob/462de3aa7a8bbd80408762a2d5aaf84b04476e4d/shapely/affinity.py#L98-L101
    minx, miny, maxx, maxy = parent_ring.bounds
    origin = ((maxx + minx) / 2.0, (maxy + miny) / 2.0)

    ring = LinearRing(polygon)

    # First undo the negative coordinates offset, since this is the last step of the original rotation
    ring = translate(ring, xoff=offset_x, yoff=offset_y)

    if element.rotation_angle:
        ring = rotate(ring, -element.rotation_angle, origin=origin)

    if element.mirrored:
        ring = scale(ring, xfact=-1, origin=origin)

    return [[int(x), int(y)] for x, y in ring.coords]
