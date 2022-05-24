""" Configuration des noms des algorithmes et des variables
"""

# Lien entre les noms d'algorithmes et les champs à traiter pour le texte
TEXT_ALGO = {
    "wind": {
        "generic": {
            "params": {
                "wind": "FF__HAUTEUR10",
                "gust": "RAF__HAUTEUR10",
                "direction": "DD__HAUTEUR10",
            }
        }
    },
    "tempe": {"generic": {"params": {"tempe": "T__HAUTEUR2"}}},
    "weather": {
        "generic": {
            "params": {
                "wwmf": "WWMF__SOL",
                "precip": "PRECIP__SOL",
                "rain": "EAU__SOL",
                "snow": "NEIPOT__SOL",
                "lpn": "LPN__SOL",
            }
        }
    },
    "wwmf": {
        "generic": {
            "params": {
                "wwmf": "WWMF__SOL",
                "precip": "PRECIP__SOL",
                "rain": "EAU__SOL",
                "snow": "NEIPOT__SOL",
                "lpn": "LPN__SOL",
            }
        }
    },
    "thunder": {
        "generic": {"params": {"orage": "RISQUE_ORAGE__SOL", "gust": "RAF__HAUTEUR10"}}
    },
    "visibility": {
        "generic": {"params": {"visi": "VISI__SOL", "type_fg": "TYPE_FG__SOL"}}
    },
    "nebulosity": {"generic": {"params": {"nebul": "NEBUL__SOL"}}},
    "rainfall": {
        "generic": {
            "params": {
                "precip": "PRECIP__SOL",
                "rain": "EAU__SOL",
                "snow": "NEIPOT__SOL",
                "lpn": "LPN__SOL",
            }
        }
    },
    "snow": {"generic": {"params": {"snow": "NEIPOT__SOL", "lpn": "LPN__SOL"}}},
}


# Liste des variables potentielles
PREFIX_TO_VAR = {
    "FF": "wind",
    "RAF": "gust",
    "NEIGE": "snow",
    "NEIPOT": "snow",
    "PRECIP": "precip",
    "EAU": "rain",
    "NEBUL": "nebul",
    "T": "temperature",
    "TMAX": "temperature",
    "TMIN": "temperature",
}
