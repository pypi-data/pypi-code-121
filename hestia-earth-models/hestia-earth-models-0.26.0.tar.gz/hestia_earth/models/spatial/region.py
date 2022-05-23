"""
Region

The model calculates the finest scale GADM region possible,
moving from gadm level 5 (for example, a village) to GADM level 0 (Country).
"""
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import linked_node

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from .utils import MAX_AREA_SIZE, download, has_geospatial_data, should_download
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "or": [
            {"latitude": "", "longitude": ""},
            {"boundary": ""}
        ]
    }
}
RETURNS = {
    "Term": {"@type": "Term", "termType": "region"}
}
KEY = 'region'
EE_PARAMS = {
    'ee_type': 'vector'
}


def _download_by_level(site: dict, level: int):
    field = f"GID_{level}"
    gadm_id = download(
        KEY,
        site,
        {
            **EE_PARAMS,
            'collection': f"gadm36_{level}",
            'fields': field
        },
        by_region=False
    ).get(field)
    try:
        return None if gadm_id is None else linked_node(download_hestia(f"GADM-{gadm_id}"))
    except Exception:
        # the Term might not exist in our glossary if it was marked as duplicate
        return None


def _run(site: dict):
    for level in [5, 4, 3, 2, 1]:
        value = _download_by_level(site, level)
        if value is not None:
            debugValues(model=MODEL, key=KEY,
                        value=value.get('@id'))
            break

    return value


def _should_run(site: dict):
    geospatial_data = has_geospatial_data(site, by_region=False)
    below_max_area_size = should_download(site, by_region=False)

    logRequirements(model=MODEL, key=KEY,
                    geospatial_data=geospatial_data,
                    max_area_size=MAX_AREA_SIZE,
                    below_max_area_size=below_max_area_size)

    should_run = all([geospatial_data, below_max_area_size])
    logShouldRun(MODEL, None, should_run, key=KEY)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else None
