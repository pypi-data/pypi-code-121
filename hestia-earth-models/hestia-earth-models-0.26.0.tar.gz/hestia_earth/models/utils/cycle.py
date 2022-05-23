from hestia_earth.schema import CycleFunctionalUnit, SiteSiteType, TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match, find_primary_product
from hestia_earth.utils.tools import list_sum, safe_parse_float, safe_parse_date

from ..log import logRequirements
from .lookup import _factor_value
from .term import get_lookup_value
from .property import get_node_property
from .dataCompleteness import _is_term_type_complete
from .input import get_total_nitrogen
from .measurement import most_relevant_measurement_value
from .site import valid_site_type as site_valid_site_type
from .crop import is_orchard
from .currency import DEFAULT_CURRENCY


def unique_currencies(cycle: dict) -> list:
    """
    Get the list of different currencies used in the Cycle.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    list
        The list of currencies as string.
    """
    products = cycle.get('products', [])
    return list(set([p.get('currency') for p in products if p.get('currency') is not None]))


def default_currency(cycle: dict) -> str:
    """
    Get the default currency for the Cycle.
    If multiple curriencies are used, will default to `USD`.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    str
        The default currency.
    """
    currencies = unique_currencies(cycle)
    return currencies[0] if len(currencies) == 1 else DEFAULT_CURRENCY


def get_excreta_N_total(cycle: dict) -> float:
    """
    Get the total nitrogen content of excreta used in the Cycle.

    The result is the sum of every excreta specified in `kg N` as an `Input` or a `Product`.

    Note: in the event where `dataCompleteness.products` is set to `True` and there are no excreta inputs or products,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.EXCRETA)
    products = filter_list_term_type(cycle.get('products', []), TermTermType.EXCRETA)
    values = get_total_nitrogen(inputs) + get_total_nitrogen(products)
    return 0 if len(values) == 0 and _is_term_type_complete(cycle, {'termType': 'products'}) else list_sum(values)


def get_max_rooting_depth(cycle: dict) -> float:
    properties = list(map(lambda p: get_node_property(p, 'rootingDepth'), cycle.get('products', [])))
    values = [safe_parse_float(p.get('value')) for p in properties if p.get('value') is not None]
    return max(values) if len(values) > 0 else None


def _land_occupation_per_ha(model: str, term_id: str, cycle: dict):
    cycleDuration = cycle.get('cycleDuration', 365)
    fallowCorrection = most_relevant_measurement_value(
        cycle.get('site', {}).get('measurements', []), 'fallowCorrection', cycle.get('endDate')
    )
    value = cycleDuration / 365 * fallowCorrection if fallowCorrection is not None else None

    logRequirements(model=model, term=term_id,
                    cycleDuration=cycleDuration,
                    fallowCorrection=fallowCorrection,
                    value_per_ha=value)

    return value


def _orchard_crop_land_occupation_per_ha(model: str, term_id: str, cycle: dict):
    practices = cycle.get('practices', [])
    nurseryDuration = list_sum(find_term_match(practices, 'nurseryDuration').get('value', []), None)
    orchardBearingDuration = list_sum(find_term_match(practices, 'orchardBearingDuration').get('value', []), None)
    orchardDensity = list_sum(find_term_match(practices, 'orchardDensity').get('value', []), None)
    orchardDuration = list_sum(find_term_match(practices, 'orchardDuration').get('value', []), None)
    rotationDuration = list_sum(find_term_match(practices, 'rotationDuration').get('value', []), None)
    saplings = list_sum(find_term_match(cycle.get('inputs', []), 'saplings').get('value', []), None)

    logRequirements(model=model, term=term_id,
                    nurseryDuration=nurseryDuration,
                    saplings=saplings,
                    orchardDensity=orchardDensity,
                    orchardDuration=orchardDuration,
                    orchardBearingDuration=orchardBearingDuration,
                    rotationDuration=rotationDuration)

    should_run = all([
        nurseryDuration, saplings, orchardDensity, orchardDuration, orchardBearingDuration, rotationDuration
    ])
    return (orchardDuration/orchardBearingDuration) * (
        1 + (nurseryDuration/365)/saplings * orchardDensity/(orchardDuration/365)  # nursery
    ) * rotationDuration/orchardDuration if should_run else None


def land_occupation_per_ha(model: str, term_id: str, cycle: dict):
    """
    Get the land occupation of the cycle per hectare in hectare.

    Parameters
    ----------
    model : str
        The name of the model running this function. For debugging purpose only.
    term_id : str
        The name of the term running this function. For debugging purpose only.
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.

    Returns
    -------
    float
        The land occupation in hectare.
    """
    product = find_primary_product(cycle) or {}
    orchard_crop = is_orchard(model, product.get('term', {}).get('@id'))
    return _orchard_crop_land_occupation_per_ha(model, term_id, cycle) if orchard_crop \
        else _land_occupation_per_ha(model, term_id, cycle)


def _land_occupation_per_kg(model: str, term_id: str, cycle: dict, product: dict, land_occupation_per_ha: float):
    functionalUnit = cycle.get('functionalUnit')
    product_value = list_sum(product.get('value', [0]))
    economicValueShare = product.get('economicValueShare', 0)

    value = land_occupation_per_ha * 10000 * (economicValueShare / 100)
    value = value / product_value if product_value > 0 else None
    value = value if functionalUnit == CycleFunctionalUnit._1_HA.value else None

    logRequirements(model=model, term=term_id,
                    functionalUnit=functionalUnit,
                    product_yield=product_value,
                    economicValueShare=economicValueShare,
                    value_per_kg_per_m2=value)

    return value


def land_occupation_per_kg(model: str, term_id: str, cycle: dict, primary_product: dict):
    """
    Get the land occupation of the cycle per kg in meter square.

    Parameters
    ----------
    model : str
        The name of the model running this function. For debugging purpose only.
    term_id : str
        The name of the term running this function. For debugging purpose only.
    cycle : dict
        The `Cycle` as defined in the Hestia Schema.
    primary_product : dict
        The primary `Product` of the `Cycle`.

    Returns
    -------
    float
        The land occupation in m2.
    """
    value = land_occupation_per_ha(model, term_id, cycle)
    return _land_occupation_per_kg(model, term_id, cycle, primary_product, value) if value is not None else None


def valid_site_type(cycle: dict, include_permanent_pasture=False):
    """
    Check if the `site.siteType` of the cycle is `cropland`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.
    include_permanent_pasture : bool
        If set to `True`, `permanent pasture` is also allowed. Defaults to `False`.

    Returns
    -------
    bool
        `True` if `siteType` matches the allowed values, `False` otherwise.
    """
    site_types = [SiteSiteType.CROPLAND.value] + (
        [SiteSiteType.PERMANENT_PASTURE.value] if include_permanent_pasture else []
    )
    return site_valid_site_type(cycle.get('site', {}), site_types)


def is_organic(cycle: dict):
    """
    Check if the `Cycle` is organic, i.e. if it contains an organic standard label `Practice`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.

    Returns
    -------
    bool
        `True` if the `Cycle` is organic, `False` otherwise.
    """
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.STANDARDSLABELS)
    return any([get_lookup_value(p.get('term', {}), 'isOrganic') == 'organic' for p in practices])


def is_irrigated(cycle: dict):
    """
    Check if the `Cycle` is irrigated, i.e. if it contains an irrigated `Practice`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.

    Returns
    -------
    bool
        `True` if the `Cycle` is irrigated, `False` otherwise.
    """
    practices = cycle.get('practices', [])
    return next((p for p in practices if p.get('term', {}).get('@id') == 'irrigated'), None) is not None


def cycle_end_year(cycle: dict):
    """
    End year of the `Cycle`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.

    Returns
    -------
    number
        The year in which the `Cycle` ends.
    """
    date = safe_parse_date(cycle.get('endDate'))
    return date.year if date else None


def impact_lookup_value(term_id: str, blank_nodes: list, term_type: TermTermType, lookup_col: str) -> float:
    """
    Calculate the value of the impact based on lookup factors and cycle values.

    Parameters
    ----------
    term_id : str
        The term to display in the logs only.
    blank_nodes : list
        The list of blank nodes from the Cycle.
    term_type: TermTermType
        The termType to restrict blank nodes and fetch lookup.
    lookup_col : str
        The lookup column to fetch the factors from.

    Returns
    -------
    int
        The impact total value.
    """
    nodes = filter_list_term_type(blank_nodes, term_type)
    factors = list(map(_factor_value(f"{term_type.value}.csv", lookup_col, term_id), nodes))
    values = [value for value in factors if value is not None]
    return list_sum(values) if len(values) > 0 else None
