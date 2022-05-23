from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.product import has_flooded_rice
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "products": [
            {
                "@type": "Product",
                "primary": "True",
                "term.@id": ["riceGrainPaddy", "ricePlantsPaddy"]
            }
        ],
        "practices": {"@type": "Practice", "term.@id": "croppingDuration"},
        "site": {
            "@type": "Site",
            "country": ""
        },
        "optional": {
            "inputs": {"@type": "Input", "term.termType": "organicFertilizer"},
            "products": {"@type": "Product", "term.@id": "aboveGroundCropResidueIncorporated"},
            "practices": [
                {"@type": "Practice", "term.termType": "cropResidueManagement"},
                {"@type": "Practice", "term.termType": "waterRegime"}
            ]
        }
    }
}
LOOKUPS = {
    "waterRegime": [
        "IPCC_2019_CH4_rice_SFw", "IPCC_2019_CH4_rice_SFw_min", "IPCC_2019_CH4_rice_SFw_max",
        "IPCC_2019_CH4_rice_SFw_sd",
        "IPCC_2019_CH4_rice_SFp", "IPCC_2019_CH4_rice_SFp_min", "IPCC_2019_CH4_rice_SFp_max",
        "IPCC_2019_CH4_rice_SFp_sd"
    ],
    "organicFertilizer": ["IPCC_2019_CH4_rice_CFOA_kg_fresh_weight", "IPCC_2019_CH4_rice_CFOA_kg_dry_weight"],
    "region-ch4ef-IPCC2019": ["CH4_ef", "CH4_ef_min", "CH4_ef_max", "CH4_ef_sd"]
}
RETURNS = {
    "Emission": [{
        "value": "",
        "min": "",
        "max": "",
        "sd": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'ch4ToAirFloodedRice'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float, min: float, max: float, sd: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['min'] = [min]
    emission['max'] = [max]
    emission['sd'] = [sd]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _get_CH4_ef(country: str, suffix: str = ''):
    lookup = download_lookup('region-ch4ef-IPCC2019.csv')
    return safe_parse_float(get_table_value(lookup, 'termid', country, column_name('CH4_ef' + suffix)))


def _get_waterRegime_lookup(term: dict, col: str):
    return safe_parse_float(get_lookup_value(term, col, model=MODEL, term=TERM_ID))


def _get_cropResidue_value(cycle: dict, suffix: str = ''):
    abgIncorporated = list_sum(
        find_term_match(cycle.get('products', []), 'aboveGroundCropResidueIncorporated').get('value', [])
    )
    abgManagement = filter_list_term_type(cycle.get('practices', []), TermTermType.CROPRESIDUEMANAGEMENT)
    term = abgManagement[0].get('term', {}) if len(abgManagement) > 0 else None
    factor = safe_parse_float(
        get_lookup_value(term, LOOKUPS['organicFertilizer'][1] + suffix, model=MODEL, term=TERM_ID)
    ) if term else 0
    return abgIncorporated * factor


def _get_fertilizer_value(input: dict, suffix: str = ''):
    term = input.get('term', {})
    factor = safe_parse_float(
        get_lookup_value(term, LOOKUPS['organicFertilizer'][0] + suffix, model=MODEL, term=TERM_ID)
    )
    return list_sum(input.get('value', [])) * factor


def _calculate_SFo(cycle: dict, suffix: str = ''):
    cropResidue = _get_cropResidue_value(cycle, suffix)
    fertilizers = filter_list_term_type(cycle.get('inputs', []), TermTermType.ORGANICFERTILIZER)
    fert_value = list_sum([_get_fertilizer_value(i, suffix) for i in fertilizers])
    return (1 + (fert_value/1000) + (cropResidue/1000)) ** 0.59


def _calculate_factor(cycle: dict, country: str, practices: list, suffix: str = ''):
    CH4_ef = _get_CH4_ef(country, suffix)
    SFw = list_sum([
        _get_waterRegime_lookup(p.get('term', {}), 'IPCC_2019_CH4_rice_SFw' + suffix) for p in practices
    ])
    SFp = list_sum([
        _get_waterRegime_lookup(p.get('term', {}), 'IPCC_2019_CH4_rice_SFp' + suffix) for p in practices
    ])
    SFo = _calculate_SFo(cycle, suffix)
    debugValues(model=MODEL, term=TERM_ID,
                CH4_ef=CH4_ef,
                SFw=SFw,
                SFp=SFp,
                SFo=SFo)
    return CH4_ef * (SFw if SFw > 0 else 1) * (SFp if SFp > 0 else 1) * SFo


def _get_croppingDuration(croppingDuration: dict, key: str = 'value'):
    return list_sum(croppingDuration.get(key, croppingDuration.get('value', [])))


def _run(cycle: dict, croppingDuration: dict, country: str):
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.WATERREGIME)

    value = _calculate_factor(cycle, country, practices) * _get_croppingDuration(croppingDuration)
    min = _calculate_factor(cycle, country, practices, '_min') * _get_croppingDuration(croppingDuration, 'min')
    max = _calculate_factor(cycle, country, practices, '_max') * _get_croppingDuration(croppingDuration, 'max')
    sd = (max-min)/4

    return [_emission(value, min, max, sd)]


def _should_run(cycle: dict):
    country = cycle.get('site', {}).get('country', {}).get('@id')

    flooded_rice = has_flooded_rice(cycle.get('products', []))

    croppingDuration = find_term_match(cycle.get('practices', []), 'croppingDuration', None)
    has_croppingDuration = croppingDuration is not None

    logRequirements(model=MODEL, term=TERM_ID,
                    has_flooded_rice=flooded_rice,
                    has_croppingDuration=has_croppingDuration,
                    country=country)

    should_run = all([flooded_rice, has_croppingDuration, country])
    logShouldRun(MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, croppingDuration, country


def run(cycle: dict):
    should_run, croppingDuration, country = _should_run(cycle)
    return _run(cycle, croppingDuration, country) if should_run else []
