from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data_closest_date
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugMissingLookup
from hestia_earth.models.utils.impact_assessment import get_site, get_region_id
from . import MODEL


def get_emission_factor(impact_assessment: dict, average_years: str, from_site_type: SiteSiteType):
    end_date = impact_assessment.get('endDate')
    site = get_site(impact_assessment)
    region_id = get_region_id(impact_assessment)
    to_site_type = site.get('siteType')

    if not to_site_type:
        # site type needed to get factors
        return None

    lookup_name = f"region-{to_site_type.replace(' ', '_')}-landTransformation{average_years}years.csv"
    lookup = download_lookup(lookup_name)
    value = get_table_value(lookup, 'termid', region_id, column_name(from_site_type.value))
    debugMissingLookup(lookup_name, 'termid', region_id, from_site_type.value, value, model=MODEL)

    return safe_parse_float(extract_grouped_data_closest_date(value, int(end_date)), None)
