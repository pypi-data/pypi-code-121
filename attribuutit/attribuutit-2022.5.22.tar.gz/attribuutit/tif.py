import pathlib
from typing import no_type_check

from geotiff import GeoTiff  # type: ignore


@no_type_check
def load(path: pathlib.Path):
    """Load the GeoTIFF file at path."""
    geo_tiff = GeoTiff(str(path))  # Consider contributing upstream as neither pathlib nor context manager support there
    crs_code = geo_tiff.crs_code.value
    crs_name = geo_tiff.crs_code.name
    bounding_box = geo_tiff.tif_bBox
    print(f'crs_name: {crs_name} (code {crs_code})')
    print(f'bbox: {bounding_box}')
