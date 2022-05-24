"""constants.py

Module for configuring all the application's global constants
"""

import os


# Paths
CUR_DIR = os.curdir
SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))

# Rules
RULES_DIR = os.path.join(SETTINGS_DIR, "rules")
RULES_NAMES = tuple(
    d
    for d in os.listdir(RULES_DIR)
    if os.path.isdir(os.path.join(RULES_DIR, d)) and not d.startswith("__")
)

# Text
_text_dir = os.path.join(SETTINGS_DIR, "text")
TEMPLATES_FILENAMES = {
    "fr": {
        "date": os.path.join(_text_dir, "fr", "date.json"),
        "synonyms": os.path.join(_text_dir, "fr", "synonyms.json"),
        "period": {
            "short": os.path.join(_text_dir, "period", "short_term.csv"),
            "long": os.path.join(_text_dir, "period", "alertes_vh_time.ini"),
        },
        "multizone": {
            "generic": os.path.join(_text_dir, "comment", "multizone.json"),
            "snow": os.path.join(_text_dir, "comment", "multizone_snow.json"),
            "precip": os.path.join(_text_dir, "comment", "multizone_precip.json"),
            "rep_val_FFRaf": os.path.join(
                _text_dir, "comment", "multizone_rep_value_FFRaf.json"
            ),
            "rep_val": os.path.join(_text_dir, "comment", "multizone_rep_value.json"),
        },
        "monozone": os.path.join(_text_dir, "comment", "multizone.json"),
    },
    "en": {"date": os.path.join(_text_dir, "en", "date.json")},
}

# Data conf
LOCAL = {
    "gridpoint": "[date:stdvortex]/[model]/[geometry:area]/[term:fmth].[format]",
    "promethee_gridpoint": (
        "[date:stdvortex]/[model]/[geometry:area]/"
        "[param].[begintime:fmth]_[endtime:fmth]_[step:fmth].[format]"
    ),
}

# Units
_units_dir = os.path.join(SETTINGS_DIR, "units")
UNITS_TABLES = {
    "pint_extension": os.path.join(_units_dir, "pint_extension.txt"),
    "wwmf_w1": os.path.join(_units_dir, "wwmf_w1_correspondence.csv"),
}
