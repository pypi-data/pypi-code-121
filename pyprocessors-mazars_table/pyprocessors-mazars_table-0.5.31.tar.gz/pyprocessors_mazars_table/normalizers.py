import re
from functools import partial

import pendulum
from duckling import (
    load_time_zones,
    parse_ref_time,
    parse_lang,
    default_locale_lang,
    parse_locale,
    parse_dimensions,
    parse,
    Context,
)
from textacy import preprocessing
from thefuzz import process

time_zones = load_time_zones("/usr/share/zoneinfo")


def get_context(time_zone, lang, locale):
    bog_now = pendulum.now(time_zone).replace(microsecond=0)
    ref_time = parse_ref_time(time_zones, time_zone, bog_now.int_timestamp)
    # Load language/locale information
    lang = parse_lang(lang)
    default_locale = default_locale_lang(lang)
    locale = default_locale if locale is None else parse_locale(locale, default_locale)
    return Context(ref_time, locale)


context = get_context("Europe/Paris", "fr", None)


def NoNormalizer(text: str) -> str:
    return text


LINEBREAK2EMPTY = str.maketrans({"\n": ""})
LINEBREAK2SPACE = str.maketrans({"\n": " "})


def CleanText(text: str) -> str:
    preproc = preprocessing.make_pipeline(
        partial(preprocessing.remove.punctuation, only=".,)("),
        preprocessing.normalize.whitespace,
        lambda x: x.translate(LINEBREAK2SPACE),
        partial(preprocessing.normalize.repeating_chars, chars=" \n"),
    )
    return preproc(text)


def CleanDate(text: str) -> str:
    if (
            "/" in text
    ):  # If date in the form dd/mm/yyyy remove all characters that are not digits and /
        text = re.sub("[^0-9/]", "", text)
        return text
    else:  # maybe a date like 1er janvier 2020, do some basic cleaning
        preproc = preprocessing.make_pipeline(
            partial(preprocessing.remove.punctuation, only=".,)("),
            preprocessing.normalize.whitespace,
            partial(preprocessing.normalize.repeating_chars, chars=" \n"),
            lambda x: x.translate(LINEBREAK2EMPTY),
        )
        return preproc(text)


def CleanDuration(text: str) -> str:
    if "/" in text:  # If combined duration like 4/6/9/12 ans, just keep 12 ans
        text = re.sub("([0-9]+/?)+", r"\1", text)
        return text
    else:  # maybe a date like 1er janvier 2020, do some basic cleaning
        preproc = preprocessing.make_pipeline(
            partial(preprocessing.remove.punctuation, only=".,)("),
            preprocessing.normalize.whitespace,
            partial(preprocessing.normalize.repeating_chars, chars=" \n"),
            lambda x: x.translate(LINEBREAK2EMPTY),
        )
        return preproc(text)


def CleanAmount(text: str) -> str:
    # basic cleanup
    preproc = preprocessing.make_pipeline(
        preprocessing.normalize.whitespace,
        partial(preprocessing.normalize.repeating_chars, chars=" \n"),
        lambda x: x.translate(LINEBREAK2EMPTY),
    )
    text = preproc(text)
    return text


def CleanIndex(text: str) -> str:
    text2 = re.sub("[^A-Z. ]", "", text)
    if text == text2:  # acronym
        text = re.sub("[. ]", "", text)
        return text
    else:
        return CleanText(text)


def NormalizeDate(text: str) -> str:
    # Use duckling time dimension
    output_dims = parse_dimensions(dims=["time"])
    dims = parse(text, context, output_dims, False)
    if dims:
        # just consider first date
        dim = dims[0]
        val = dim["value"]
        if "value" in val:
            strdate = val["value"]
            dt = pendulum.parse(strdate)
            # format french way
            return dt.format("DD/MM/YYYY")
    return text


def NormalizeIndex(text: str) -> str:
    indexes = {
        "indice du coût de la construction": "ICC",
        "indice national du coût de la construction": "ICC",
        "indice des loyers commerciaux": "ILC",
        "indice de référence des loyers commerciaux": "ILC",
        "indice de référence des loyers des activités tertiaires": "ILAT",
        "indice des loyers des activités tertiaires": "ILAT",
        "indice de révision des loyers": "IRL",
        "indice de référence des loyers": "IRL",
    }
    text2 = re.sub("[^A-Z]", "", text)
    if text == text2:  # acronym
        return text
    else:
        # use levensthein distance to find closer candidate
        best = process.extractOne(text.lower(), indexes.keys())
        if best and best[1] > 90:
            text = indexes[best[0]]
    return text


DURATION_UNITS = {
    "year": ["an", "ans"],
    "month": ["mois", "mois"],
    "week": ["semaine", "semaine"],
    "day": ["jour", "jours"],
}
BASE_UNIT2UNIT = {
    "year": {"month": 12, "week": 52, "day": 365},
    "month": {"week": 4.5, "day": 30},
    "week": {"day": 7},
}


def NormalizeDuration(text: str) -> str:
    # un quart du loyer annuel
    if "quart" in text.lower() and "loyer" in text.lower():
        text = "3 mois"
    else:
        # Use duckling duration dimension
        output_dims = parse_dimensions(dims=["duration"])
        dims = parse(text, context, output_dims, False)
        if dims:
            durations = {}
            texts = []
            for dim in dims:
                val = dim["value"]
                if "value" in val and "unit" in val:
                    value = val["value"]
                    unit = val["unit"]
                    durations[unit] = value
            if durations:
                units = list(durations.keys())
                base_unit = units[0]
                fr_units = DURATION_UNITS.get(base_unit, [base_unit, base_unit + "s"])
                fr_unit = fr_units[0] if value == 1 else fr_units[1]
                for unit, val in durations.items():
                    if unit == base_unit:
                        texts.append(f"{val}")
                    else:
                        ratio = BASE_UNIT2UNIT[base_unit][unit]
                        texts.append(f"{val}/{ratio}")
                text = ("+".join(texts)) + " " + fr_unit
    return text


def NormalizeAmount(text: str) -> str:
    text2 = re.sub("[^0-9,. €)(+-]", "", text)
    if text == text2:
        text = re.sub("[^0-9,. ]", "", text)
        if "." in text:
            idx = text.rindex(".")
            if idx == len(text) - 3:
                text = text[:idx] + "," + text[idx + 1:]
            else:
                text = re.sub(" ", "", text)
        output_dims = parse_dimensions(dims=["number"])
        dims = parse(text, context, output_dims, False)
        if dims:
            dim = dims[0]
            val = dim["value"]
            if "value" in val:
                value = str(val["value"])
                return value
    return text
