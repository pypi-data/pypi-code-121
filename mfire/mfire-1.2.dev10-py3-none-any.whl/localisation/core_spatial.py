import copy

import numpy as np
import xarray as xr

from mfire.settings import get_logger
from mfire.localisation.area_algebre import RiskArea

# Logging
LOGGER = get_logger(name="localisation", bind="localisation")

np.warnings.filterwarnings("ignore")


class LocalisationError(ValueError):
    pass


def get_variance(risk, area, comp_area):
    """
    Permet d'obtenir la variance.
    Ces fonctions sont ici pour vérifier que c'est bien elles qui pénalisent les choses
    """
    var_area = (area * risk).var(["latitude", "longitude"])
    var_comp = (comp_area * risk).var(["latitude", "longitude"])
    return var_area, var_comp


def remove_from_list(l_out, area):
    """
    Enleve une possibilité de la liste.
    A du être mise car problème quand on faisait le remove ...
    """
    LOGGER.debug(
        "entering remove from list %s %s", area.areaName.values, area.id.values
    )
    LOGGER.debug("List len %s", len(l_out))
    for i, elt in enumerate(l_out):
        if elt.id == area.id:
            del l_out[i]
            LOGGER.debug("removing element")


def choose_area(l_pos):
    """
    Permet le choix de la zone a partir d'une liste de choix.
    Prend le Gain maximum.
    """
    gain_max = 0
    l_gain = []
    for pos in l_pos.keys():
        gain = l_pos[pos]["Gain"]
        l_gain.append(gain)
        if gain > gain_max:
            winner = pos
            gain_max = gain
    LOGGER.debug("Gain max obtenu à ce niveau de séparation %s", gain_max)
    return winner


def best_separation(risk, area_handler, domain):
    """
    risk : le champ de risk
    domain : le domaine initial
    area: une lsite d'aire
    """

    # Variance initiale (avant subdivision)
    area, comp_area = area_handler.get_possibilities(domain)

    if area is None:
        LOGGER.debug("We did not found any 'valid subdivision'")
        return None, None, -1000
    var_init = (domain * risk).var(["latitude", "longitude"]).sum(
        "valid_time"
    ) * domain.sum(["latitude", "longitude"])
    # Calcul des variance intra pour chacune des zones
    var_area, var_comp = get_variance(risk, area, comp_area)
    # On fait la somme des carrés (histoire d'avoir des choses homogènes)
    v1_intra = var_area.sum("valid_time") * area.sum(["latitude", "longitude"])
    v2_intra = var_comp.sum("valid_time") * comp_area.sum(["latitude", "longitude"])
    var_intra = v1_intra + v2_intra
    # On recherche le mini de la somme des carrés
    mini = var_intra.load().argmin()
    # Selection de la zone et de son complementaire
    b_area = area.isel(id=mini)
    # Selection du complémentaire
    b_comp_area = comp_area.isel(id=mini)
    # On change d'ID car pour l'instant il a celui du complémentaire
    b_comp_area["id"] = f"comp_{str(b_comp_area.id.values)}"
    # On calcul le gain obtenu par cette subdivision
    gain = (var_init - var_intra.isel(id=mini)).values
    LOGGER.debug(
        f"Gain subdivision {gain} pour de ce domaine {domain['areaName'].values} "
        f"en zone {area.isel(id=mini)['areaName'].values} et ce complementaire "
        f"{comp_area.isel(id=mini)['areaName'].values}."
    )
    return b_area, b_comp_area, gain


def get_n_area(risk, full_domain, l_area, n=5, cdt=0.001, between_authorized=False):
    """
    Permet de
    - risk (dataArray):  Décrit le risque (ou le champ quantitatif) qui va servir
        à la localisation (time, lat,lon)
    - full_domain : Donne le domaine de départ. Théoriquement c'est la même que
        le risque (mais on ne sait jamais)
    - l_area(dataArray) : Un dataArray avec les "zones" descriptives
    - n : Nombre de découpage successif
    - cdt : Condition d'arret. Si on "améliore" la variance de moins de cdt %
        on ne propose pas le découpage comme une solution
    - between_authorized : Autorise-t-on les zones de type "Entre X et Y" à être
        prise comme zones complémentaires ?
    """
    if between_authorized:
        area_handler = RiskArea(
            full_domain, l_area, between_authorized=between_authorized
        )
    else:
        area_handler = RiskArea(full_domain, l_area)

    var_init = (full_domain * risk).var(["latitude", "longitude"]).sum(
        "valid_time"
    ) * full_domain.sum(["latitude", "longitude"])
    # On cherche la premiere separation de full_domain
    #
    domain = copy.deepcopy(full_domain)
    if "id" in domain.dims:
        domain = domain.squeeze("id")
    A, a_comp, _ = best_separation(risk, area_handler, domain)

    if A is None:
        raise LocalisationError(
            f"Ce domaine ({domain.areaName.values}) ne peut être découpé via "
            "ses zones descriptives. Aucun couple ne peut y etre trouvé."
        )

    # On cree un dictionnaire d'area transitoire

    dict_area = {}
    dict_area[str(A.areaName.values)] = A
    dict_area[str(a_comp.areaName.values)] = a_comp
    l_pos = {}
    # On cree une liste des "areas" en sortie
    l_out_area = []
    l_out_area.append(prepare_area(A))
    l_out_area.append(prepare_area(a_comp))
    # On ajoute en possibilité la décomposition de A et a_comp
    for i in range(1, n):
        # i n'est pas utile. C'est juste pour faire une boucle.
        # Peut etre passer par un while ?
        B, b_comp, gain_b = best_separation(risk, area_handler, A)
        if gain_b / var_init > cdt:
            l_pos[str(B.areaName.values)] = {
                "area": B,
                "areab": b_comp,
                "Gain": gain_b,
                "Parent": A,
            }
        elif gain_b < 0:
            LOGGER.debug("Pas de subdivision valide pour %s", A.areaName.values)
        else:
            LOGGER.debug("Gain trop faible %s %s", gain_b / var_init.values, B.areaName)
        C, c_comp, gain_c = best_separation(risk, area_handler, a_comp)
        if gain_c / var_init > cdt:
            l_pos[str(C.areaName.values)] = {
                "area": C,
                "areab": c_comp,
                "Gain": gain_c,
                "Parent": a_comp,
            }
        elif gain_c < 0:
            LOGGER.debug("Pas de subdivision valide pour %s", a_comp.areaName.values)
        else:
            LOGGER.debug("Gain trop faible %s %s", gain_c / var_init.values, C.areaName)

        if len(l_pos) > 0:
            idi = choose_area(l_pos)
            LOGGER.debug("Zone choisie pour le redecoupage %s", idi)
            dict_to_add = l_pos.pop(idi)
            remove_from_list(l_out_area, dict_to_add["Parent"])
            # On redefinie la zone et son complémentaire.
            A = dict_to_add["area"]
            a_comp = dict_to_add["areab"]
            l_out_area.append(prepare_area(A))
            l_out_area.append(prepare_area(a_comp))
        else:
            # On s'arrete prematurement : les decoupages ne permettent pas de continuer
            break
    name = l_out_area[0].name
    ds_out = xr.merge(l_out_area)
    return ds_out[name]


def prepare_area(A):
    """Permet de renvoyer un dataArray avec des dimensions prêtes pour le merge.
    Args:
        A (DataArray): Le dataArry à modifier

    Raises:
        ValueError: Si on est pas du type dataArray

    Returns:
        [DataArray]: DataArray modifié (areaName et areaType sont des dimensions
            indexées par id)
    """
    # On va rajouter 'areaName et areaType'.
    if not isinstance(A, xr.core.dataarray.DataArray):
        raise ValueError("Input is expected to be a dataArray")
    name = A.name
    A = A.reset_coords(["areaName", "areaType"])
    if "id" not in A.dims:
        A = A.expand_dims("id")
    else:
        A["areaName"] = A["areaName"].expand_dims("id")
        A["areaType"] = A["areaType"].expand_dims("id")
    A = (
        A.swap_dims({"id": "areaName"})
        .swap_dims({"areaName": "areaType"})
        .swap_dims({"areaType": "id"})
    )

    return A[name]


if __name__ == "__main__":
    # Pour l'instant le test fonctionne uniquement chez moi ....
    # A voir s'il faut faire quelque chose de plus générique.
    import matplotlib.pyplot as plt
    from mfire.utils.xr_utils import MaskLoader

    RISK = xr.open_dataset("../../localisation/ex_riskt2m.nc")[
        "__xarray_dataarray_variable__"
    ]
    RISK = RISK.drop("areaName")
    AREA = MaskLoader(
        filename="../../localisation/GeoOut/Geo_Isère.nc", grid_name="eurw1s100",
    ).load()

    FULL_DOMAIN = AREA.max("id")
    FULL_DOMAIN["areaName"] = "domain"
    FULL_DOMAIN["areaType"] = "test"

    ds_loca = get_n_area(RISK, FULL_DOMAIN, AREA, cdt=0.02)
    ds_loca.swap_dims({"id": "areaName"}).plot(col="areaName")
    plt.savefig("test_localisation.png")
