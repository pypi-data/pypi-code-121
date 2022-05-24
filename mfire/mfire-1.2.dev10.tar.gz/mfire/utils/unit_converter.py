"""
@package utils.unit_converter

Module de conversion d'unités

Fortement inspiré des modules du projet Métronome
    (pour les conversions non symétriques)
- mpylib.syncom.unit_converter, par Joël Barthez
- mpylib.syncom.constants, par Thomas Bouton

Une grande partie des conversion se fait via la librairie pint

To do list :
   - Handle correctly Beaufort (with problem of comparison operator) (issue 16)
   - Handle the "1" unit converter (with multiple contexts) (issue 17)
   - Convert percent in octa (and conversely) (issue 1)

"""
import re
from typing import Union, List
from collections.abc import Iterable
import ast
import pandas as pd
import numpy
import pint
import xarray as xr
from mfire.settings import get_logger, UNITS_TABLES

# Logging
LOGGER = get_logger(name="unit_converter", bind="unit_converter")

# A faire :
# Proportion (pourcentage, octat)
# Les cumuls de precip peuvent theroriquement etre fait depuis pint mais necessitent
# l'utilisation d'un contexte.
# Cumul de precip (kg/m2, mm, cm)

"""
Defining pint handler
"""
pint_handler = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
# Loading specific unit for us (and specific conversion rules).
pint_handler.load_definitions(UNITS_TABLES["pint_extension"])

"""
Fonction de conversion d'unités
"""

# Conversion d'unités d'angles


def fromDegreDecimalToDegreSexagesimal(val):
    """
    Retourne une valeur d'angle exprimé en décimal sous la forme degré
    sexagesimal (signe, degré, minute, seconde)
    @param val valeur de l'angle en décimal
    @return Cette valeur sous la forme sexagesimale signé
    """
    degre_absolu = numpy.fabs(val)
    if degre_absolu == val:
        signe = "+"
    else:
        signe = "-"
    degre = int(degre_absolu)
    decimale = degre_absolu - degre
    minute = int(decimale * 60)
    seconde = int((decimale * 60 - minute) * 60)
    return signe, degre, minute, seconde


def fromLatitudeDecimalToLatitudeSexagesimal(val):
    """
    Retourne une chaine caratéristique de la latitude exprimée sous forme sexagesimale
    @param val valeur de la latitude en décimal
    @return chaine caratéristique de la latitude exprimée sous forme sexagesimale
    """
    signe, degre, minute, seconde = fromDegreDecimalToDegreSexagesimal(val)
    if signe == "-":
        sens = "Sud"
    else:
        sens = "Nord"
    latitude = "%02d°%02d'%02d\" %s" % (degre, minute, seconde, sens)
    return latitude


def fromLongitudeDecimalToLongitudeSexagesimal(val):
    """
    Retourne une chaine caratéristique de la longitude exprimée sous forme sexagesimale
    @param val valeur de la longitude en décimal
    @return chaine caratéristique de la longitude exprimée sous forme sexagesimale
    """
    signe, degre, minute, seconde = fromDegreDecimalToDegreSexagesimal(val)
    if signe == "-":
        sens = "Ouest"
    else:
        sens = "Est"
    longitude = "%02d°%02d'%02d\" %s" % (degre, minute, seconde, sens)
    return longitude


def fromDegreToDirection(val):
    """
    A partir de la direction du vent exprime en degre affiche une chaine de caractère
    caractéristique de ce vent.
    Direction du vent sous la forme numérique et sous la forme cardinale
    @param val: Direction du vent en degrés
    @return: chaine de caractère représentant cette direction
    """

    direction = int((((val + 11.25) // 22.5) * 225) % 3600)  # en dixième de degrés
    if direction == 0:
        cardinalite = "Nord"
    elif direction == 225:
        cardinalite = "NNE"
    elif direction == 450:
        cardinalite = "NE"
    elif direction == 675:
        cardinalite = "ENE"
    elif direction == 900:
        cardinalite = "Est"
    elif direction == 1125:
        cardinalite = "ESE"
    elif direction == 1350:
        cardinalite = "SE"
    elif direction == 1575:
        cardinalite = "SSE"
    elif direction == 1800:
        cardinalite = "Sud"
    elif direction == 2025:
        cardinalite = "SSO"
    elif direction == 2250:
        cardinalite = "SO"
    elif direction == 2475:
        cardinalite = "OSO"
    elif direction == 2700:
        cardinalite = "Ouest"
    elif direction == 2925:
        cardinalite = "ONO"
    elif direction == 3150:
        cardinalite = "NO"
    elif direction == 3375:
        cardinalite = "NNO"
    else:
        cardinalite = f"Inconnu ({direction})"
    return cardinalite


ANGLES_DICT = {
    "degreDecimal": {
        "direction": fromDegreToDirection,
        "degreSexagesimal": fromDegreDecimalToDegreSexagesimal,
    },
}

LAT_LON_DICT = {
    "latDecimal": {"latSexagesimal": fromLatitudeDecimalToLatitudeSexagesimal},
    "lonDecimal": {"lonSexagesimal": fromLongitudeDecimalToLongitudeSexagesimal},
}


# Conversion d'unités de vitesse
def fromNoeudToBeaufort(val):
    """
    Convertit une vitesse exprimée en noeud en force beaufort
    @param val valeur de la vitesse exprimée en noeuds
    @return La valeur de cette vitesse exprimée en échelle beaufort
    """
    seuils = [-1e21, 1, 4, 7, 11, 17, 22, 28, 34, 41, 48, 56, 64, 1e21]
    if isinstance(val, numpy.ndarray):
        res = numpy.empty_like(val)
        for i in range(len(seuils) - 1):
            res[numpy.logical_and(val >= seuils[i], val < seuils[i + 1])] = i
        res[numpy.logical_or(val < seuils[0], val >= seuils[-1])] = -1
        return res
    else:
        for i in range(len(seuils) - 1):
            if val >= seuils[i] and val < seuils[i + 1]:
                return i
        return -1


def fromBeaufortToDescription(val):
    """
    Retourne un terme représentatif de la force beaufort passé en paramètre
    @param val valeur de la vitesse exprimée en sous la forme d'une force beaufort
    @return Chaine de caractère caractérisant cette force
    """
    if val == 0:
        return "Calme"
    elif val == 1:
        return "Très légère brise"
    elif val == 2:
        return "Légère brise"
    elif val == 3:
        return "Petite brise"
    elif val == 4:
        return "Jolie brise"
    elif val == 5:
        return "Bonne brise"
    elif val == 6:
        return "Vent frais"
    elif val == 7:
        return "Grand vent frais"
    elif val == 8:
        return "Coup de vent"
    elif val == 9:
        return "Fort coup de vent"
    elif val == 10:
        return "Tempête"
    elif val == 11:
        return "Violente tempête"
    elif val == 12:
        return "Ouragan"

    return "Inconnu"


def fromNoeudToDescription(val):
    """
    Permet la description de tout vent exprime en Noeud.
    Par extension (via pint) permet de faire toutes les unités du système métrique

    Arguments:
    """

    return fromBeaufortToDescription(fromNoeudToBeaufort(val))


# Points définissant la fonction de conversion noeuds <-> Beauforts
beauforts = [0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5]
# Points définissant la fonction de conversion noeuds <-> Beauforts
kts = [0, 0.5, 3.5, 6.5, 10.5, 16.5, 21.5, 27.5, 33.5, 40.5, 47.5, 55.5, 63.5]


def fromKtToBeaufort(x):
    """
    Conversion d'une vitesse exprimée en Noeuds vers une vitesse exprimée en
    Beaufort. Fonction de conversion continue, affine par morceau, telle
    qu'après arrondi du résultat, on obtient la valeur attendue en Beauforts.
    @param x Vitesse exprimée en noeuds
    @return Vitesse exprimée en Beaufort.
    """
    for i in range(1, len(kts)):
        if x <= kts[i]:
            break
    return beauforts[i - 1] + (x - kts[i - 1]) * (beauforts[i] - beauforts[i - 1]) / (
        kts[i] - kts[i - 1]
    )


def fromBeaufortToKt(x):
    """
    Conversion d'une vitesse exprimée en Beauforts vers une vitesse exprimée en
    noeuds. Fonction réciproque de `from KtToBeaufort`.
    @param x Vitesse exprimée en Beaufort.
    @return Vitesse exprimée en noeud.
    """
    for i in range(1, len(beauforts)):
        if x <= beauforts[i]:
            break
    return kts[i - 1] + (x - beauforts[i - 1]) * (kts[i] - kts[i - 1]) / (
        beauforts[i] - beauforts[i - 1]
    )


SPEED_DICT = {
    "kt": {"B": fromNoeudToBeaufort, "description": fromNoeudToDescription},
    "B": {"kt": fromBeaufortToKt, "description": fromBeaufortToDescription},
}

# Conversion Taux de Precipitations/Reflectivité Radar


def fromKgPerM2PerSecondTodBZ(x, a=200, b=1.6):
    """
    Conversion d'un taux de précipitations en réflectivité radar par la relation
    de Marshall-Palmer
    @param x taux de precipitation exprimé en kg m-2 s-1
    @param a coefficient a de la relation de Marshall-Palmer (defaut a=200)
    @param b coefficient b de la relation de Marshall-Palmer (defaut b=1.6)
    @return Réflectivité exprimée dBZ:
    """
    save_settings = numpy.seterr(divide="ignore")
    try:
        if not isinstance(x, numpy.ndarray):
            if x < 0:
                return 0
        else:
            if (x < 0).any():
                cp = x.copy()
                cp[x < 0] = 0
                x = cp
        z = 10 * numpy.log10(a * (x * 3600000.0) ** b)
        if z.ndim > 0:
            z[z == -numpy.inf] = 0
        elif z == -numpy.inf:
            z = 0
        return z
    finally:
        numpy.seterr(**save_settings)


def fromdBZToKgPerM2PerSecond(x, a=200, b=1.6):
    """
    Conversion d'une réflectivité radar en taux de précipitations par la relation
    de Marshall-Palmer
    @param x réflectivité exprimée en dBZ
    @param a coefficient a de la relation de Marshall-Palmer (defaut a=200)
    @param b coefficient b de la relation de Marshall-Palmer (defaut b=1.6)
    @return Taux de precipitation exprimé en kg m-2 s-1
    """
    return ((10 ** (x / 10.0)) / a) ** (1 / b) / 3600000.0


RADAR_DICT = {
    "dBZ": {"kg/m2s": fromdBZToKgPerM2PerSecond},
    "kg/m2s": {"dBZ": fromKgPerM2PerSecondTodBZ},
}

# Conversion de codes temps sensible
# Dataframe contenant les code WWMF et les code W1
DF_WWMF_TO_W1 = pd.read_csv(UNITS_TABLES["wwmf_w1"], converters={2: ast.literal_eval})

W1_TO_WWMF = [
    (-1, "Inconnu", -1, "Inconnu"),
    (0, "RAS", 0, "Clair"),
    (1, "Brume ou brouillard peu dense", 31, "Brume/brouillard"),
    (2, "Brouillard dense par place", 32, "Brouillard"),
    (3, "Brouillard dense généralisé", 33, "Brouillard dense"),
    (4, "Brume ou brouillard givrant peu dense", 38, "Brouillard givrant"),
    (5, "Brouillard givrant dense par place", 38, "Brouillard givrant"),
    (6, "Brouillard givrant dense généralisé", 39, "Brouillard dense givrant"),
    (7, "Bruine", 40, "Bruine"),
    (8, "Bruine ou pluie verglaçante", 59, "Pluie verglaçante"),
    (9, "Pluie faible par place", 51, "Pluie faible"),
    (10, "Pluie faible ou modérée généralisée", 52, "Pluie modérée"),
    (11, "Pluie forte généralisée", 53, "Pluie forte"),
    (12, "Pluie localement orageuse", 53, "Pluie forte"),
    (13, "Neige faible par place", 61, "Neige faible"),
    (14, "Pluie et neige mêlées", 58, "Pluie et neige mêlées"),
    (15, "Neige collante", -1, "Inconnu"),
    (16, "Neige faible ou mdoérée généralisée", 62, "Neige modérée"),
    (17, "Neige forte généralisée", 63, "Neige forte"),
    (18, "Rares averses de pluie", 71, "Rares averses"),
    (19, "Averses de pluie", 70, "Averses"),
    (20, "Averses de pluie et neige mêlées", 77, "Averses de pluie et neige mêlées"),
    (21, "Rares averses de neige", 81, "Rares averses de neige"),
    (22, "Averses de neige", 80, "Averses de neige"),
    (23, "Averses de grêles", 85, "Averses de grêles"),
    (24, "Orages possibles", 90, "Orages"),
    (25, "Orages probables", 90, "Orages"),
    (26, "Violents orages possibles", 99, "Orages violents"),
    (27, "Violents orages probables", 99, "Orages violents"),
    (28, "Orages de grêle possibles", 98, "Orages avec grêle"),
    (29, "Orages de grêle probables", 98, "Orages avec grêle"),
    (30, "Averses sur le relief", -1, "Inconnu"),
    (31, "Orages sur le relief", -1, "Inconnu"),
    (32, "Averses localement orageuses", 70, "Averses"),
    (33, "Bancs de brouillard en plaine", -1, "Inconnu"),
]


def convert_wwmf(code: int, conversion_list: list, input_name: str = "") -> int:
    try:
        return next(
            output_code
            for input_code, _, output_code, _ in conversion_list
            if input_code == code
        )
    except StopIteration:
        LOGGER.error(f"Invalid  Code {input_name} given : {code}")
    except Exception:
        LOGGER.error(f"Invalid Code {input_name} given : {code}", exc_info=True)
    return -1


def fromW1ToWWMF(codeW1, w1_to_wwmf=W1_TO_WWMF):
    if isinstance(codeW1, Iterable):
        return list({convert_wwmf(code, w1_to_wwmf, "W1") for code in codeW1})
    return convert_wwmf(codeW1, w1_to_wwmf, "W1")


def fromWWMFToW1(code_list: Union[Iterable, int]) -> list:
    """
    Enable to convert a list of WwMF code to a list of W1 code

    Args:
        code_list (Union[Iterable, int]): The input WwMF codes
    Returns:
        [list]:  W1 codes
    """
    if not isinstance(code_list, Iterable):
        code_list = [code_list]
    W1_code = []
    for x in code_list:
        if x not in DF_WWMF_TO_W1["Code WWMF"].values:
            LOGGER.error(f"We did not found the translation for this code {x}")
        W1_code = (
            W1_code
            + DF_WWMF_TO_W1.loc[DF_WWMF_TO_W1["Code WWMF"] == x, "Code W1"].to_list()[0]
        )
    W1_code = list(set(W1_code))
    return W1_code


WWMF_DICT = {
    "w1": {"wwmf": fromW1ToWWMF},  # Theoriquement on a pas ce sens la
    "wwmf": {"w1": fromWWMFToW1},
}

"""
Dictionnaire créé pour verifier les fonctions de pint
Utilise maintenant pour savoir quelles conversions sont possibles
"""
CONVERT_DICT = {**RADAR_DICT, **SPEED_DICT, **ANGLES_DICT, **LAT_LON_DICT, **WWMF_DICT}
# Both are needed to go out of pint if needed (or to specify the context)
not_pint_unit = [
    "B",
    "description",
    "dBZ",
    "direction",
    "degreSexagesimal",
    "latSexagesimal",
    "lonSexagesimal",
    "wwmf",
    "w1",
]
contextual_unit = [
    "kg/m^2",
    "kg/m2",
    "kg m**-2",
    "kg/m^2/s",
    "kg/m2/s",
    "kg/m2s",
    "kg m**-2 s**-1",
]


def pint_converter(threshold, unit, output_unit, *context):
    """
    Use pint to convert unity of a given number or dataArray
    Arguments:
        threshold {number, dataArray} -- [description]
        unit {str} -- [description]
        output_unit {str} -- [description]
        *context --  Context to use for conversion.
            Context is usefull to go from [mass]/[area] -> [length]
            for precipitation, snow and ice
    Returns:
        {number,dataArray} -- Thresold (in the given output_unit)
    """
    # Very specific case to handle '%' symbol
    # Unsolved issue #429 in the pint library :
    # it triggers a AttributeError: 'NoneType' object has no attribute 'evaluate'
    if unit == "%":
        unit = "percent"
    if output_unit == "%":
        output_unit = "percent"

    th = pint_handler(unit) * threshold
    if isinstance(th, xr.core.dataarray.DataArray):
        th.values = th.data.to(output_unit, *context).m
        th.attrs["units"] = output_unit
        return th
    else:
        return th.to(output_unit, *context).m


def simplify_old_convert(threshold, units, output_unit):
    """
    Usefull for test of adequation between pint and this module
    """
    return CONVERT_DICT[units][output_unit](threshold)


def change_input_unit(th, unit, output_unit):
    """
    This function enable to change input unit.
    This input_unit will match one unit of CONVERT_DICT

    Arguments:
        th {number} -- Input number to convert
        unit {str} -- Unit of the input_unit
        output_unit {str} -- Output_unit we need to attains through CONVERT_DICT.

    Returns:
        tuple -- (new_threshold, new_unit)
        if a conversion is not found, return (none,none)
    """
    for pos in CONVERT_DICT.keys():
        if output_unit in CONVERT_DICT[pos].keys():
            try:
                new_th = pint_converter(th, unit, pos)
                new_unit = pos
                return new_th, new_unit
            except Exception:
                LOGGER.error(f"Impossible to convert {unit} to {pos}")
    return None, None


def change_output_unit(possible_list, unit):
    """
    This function enable to change input unit to use local function
    Arguments:
        possible_list {list of possibility} -- Possible list of units
        unit {str} -- unit to transform

    Returns:
        str --  new_unit
        if a conversion is not found, return None
    """
    for pos in possible_list:
        try:
            _ = pint_converter(1, unit, pos)
            new_unit = pos
            return new_unit
        except Exception:
            LOGGER.error(f"Impossible to convert {unit} to {pos}")
    return None


CONTEXTS = {
    "precipitation": (
        r"^tp$",
        r"[P|p]recipitation",
        r"rprate",
        r"PRECIP\d*__SOL",
        r"EAU\d*__SOL",
    ),
    "snow": (r"[S|s]no[w|m]", r"p3099", r"NEIPOT\d*__SOL",),
}


def get_context(names: List[str]) -> str:
    """Returns the context associated to a list of parameter's names.

    Args:
        names (List[str]): List of possible parameter's name.

    Returns:
        str: Context name associated to the given names. None
            if no context found.
    """
    for context, patterns in CONTEXTS.items():
        for pattern in patterns:
            reg = re.compile(pattern=pattern)
            for name in names:
                if reg.search(name):
                    return context
    return None


def convert_threshold_operation(threshold, units, output_units, name=None):
    """
    Main function for converstion
    Arguments:
        threshold {number} -- A given number to convert
        units {str} -- Input units
        output_units {str} -- Ouput units
        name {str or list of str} : variable name or names.
            It is  usefull for context if pint is used. It is usefull
    Returns:
        number -- The threshold converted
    """
    try:
        if units in not_pint_unit or output_units in not_pint_unit:
            if units not in CONVERT_DICT.keys():
                # Converting input units (in order to be present
                # in convert dictionnary)
                threshold, units = change_input_unit(threshold, units, output_units)
                if threshold is None:
                    raise ValueError("Not possible to find input unit correspondance")
            if output_units not in CONVERT_DICT[units]:
                # looking for ouptut_units (in order to be present
                # in convert dictionnary)
                transitory_output = change_output_unit(
                    CONVERT_DICT[units], output_units
                )
                transitory_thr = CONVERT_DICT[units][transitory_output](threshold)
                return pint_converter(transitory_thr, transitory_output, output_units)
            else:
                return CONVERT_DICT[units][output_units](threshold)
        else:
            if units in contextual_unit or output_units in contextual_unit:
                LOGGER.debug(f"Trying contextual, here are the name {name}")
                context = get_context(names=name)
                if context is None:
                    raise ValueError("Impossible to find parameter's context.")
                return pint_converter(threshold, units, output_units, context)
            else:
                return pint_converter(threshold, units, output_units)

    except Exception as excpt:
        raise ValueError(
            "Error when trying to convert units in "
            f"convert_threshold_operation(threshold={threshold}, "
            f"units={units}, output_units={output_units}, name={name})."
        ) from excpt


def convert_dataarray(da, units):
    """
    convert_dataarray : Conversion du dataArray tout entier

    Arguments:
        da {dataArray} -- The dataArray to convert. Should have an units attribute
        units {str} -- Unité vers laquelle on converti

    Returns:
        dataArray -- Le dataArray de sortie
    """
    if str(units) == str(da.units):
        return da
    else:
        names = [da.name]
        if hasattr(da, "long_name"):
            names.append(da.long_name)
        if hasattr(da, "GRIB_shortName"):
            names.append(da.GRIB_shortName)
        return convert_threshold_operation(da, da.units, units, names)


def convert_threshold(da, threshold, units):
    """
    This function convert a threshold
    It base the convesion on unit of the dataarray and on output unit.

    Arguments:
        da {data_array} -- The data array we will compare with threshold
        threshold {number} -- The number to convert to data_array units
        units {str} -- Input unit of the threshold

    Returns:
        float -- The threshold convert
    """
    if not isinstance(da, xr.core.dataarray.DataArray):
        raise (
            ValueError(f"In convert_threshold we expected a data_array. Get{type(da)} ")
        )
    if units == da.units:
        return threshold
    else:
        names = [da.name]
        if hasattr(da, "long_name"):
            names.append(da.long_name)
        if hasattr(da, "GRIB_shortName"):
            names.append(da.GRIB_shortName)
        return convert_threshold_operation(threshold, units, da.units, names)
