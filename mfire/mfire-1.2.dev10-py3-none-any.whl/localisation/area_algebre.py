"""
Module permettant de "jongler" avec les noms de zones.
History 24/02/2021 : Removing the possibility to name complementary
area with "Between ".
"""
import re
import operator
import copy
from typing import List

import numpy as np
import xarray as xr

from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="areaAlgebre", bind="areaAlgebre")

DefaultIOU = 0.5
IoUAlt = 0.7  # Pour nommer une zone "spatiale" par une zone d'altitude


def compute_IoU(area1, l_area):
    """
        Permet le calcul de l'IoU en se basant sur des dataArrays
    """
    lda = area1.astype("int8")
    rda = l_area.astype("int8")
    dims = ("latitude", "longitude")
    return (lda * rda).sum(dims) / rda.where(rda > 0, lda).sum(dims)


def alt_change(input_str):
    """permet de convertir un string conteant l'unité d'altitude m
    en entier

    Args:
        input_str ([string])

    Returns:
        [int]
    """
    return int(input_str.replace("m", ""))


def generic_merge(area1, area2):
    """ Permet de merger des zones

    Args:
        area1 (dataArray ou None): [description]
        area2 ([dataArray ou None]): [description]

    Returns:
        [dataArray ou None]: None si les deux entrées sont None.
    """
    if area1 is None:
        return area2
    if area2 is None:
        return area1
    name = area1.name
    return xr.merge([area1, area2])[name]


def get_representative_area_properties(area_list, area_possibilities, domain=None):
    """
    On va essayer de trouver la zone qui represente le mieux l'union
    de area_list afin de nommer la liste.
    S'il n'y a pas de candidats idéal, on va s'occuper de renommer
    (brutalement) certaines propriétés.
    Fonction utilisée dans le résumé.

    Args:
        area_list (dataArray): La liste d'entrée des zones à fusionner
        area_possibilities (dataArray): Les possibilités de fusion
        domain (dataArray) : Le domaine utilisé dans les calculs.
            Pour s'appeler avec le nom du domaine la condition est plus stricte.

    Returns:
        [Tuple]: [Le nom de la zone, le type de la zone]
    """
    area_sum = area_list.sum("id", min_count=1)
    IoU = compute_IoU(area_sum, area_possibilities)
    IoUMax = IoU.max("id")
    a_max = IoU.argmax("id")
    LOGGER.debug(f"Maximum of IoU for area merge {IoUMax.values}")
    if IoUMax > 0.6:
        area_name = area_possibilities.isel(id=a_max).areaName.values
        area_type = area_possibilities.isel(id=a_max).areaType.values
    else:
        area_name = " et ".join(area_list["areaName"].values.astype(str))
        if len(np.unique(area_list.areaType)) == 1:
            area_type = area_list.areaType[0]
        else:
            area_type = "No"
    # On test aussi avec l'ensemble du domaine s'il existe
    if domain is not None:
        IoU = compute_IoU(area_sum, domain)
        LOGGER.debug(f"IoU for domain is {IoU.values}")
        if IoU > 0.98:
            area_name = domain["areaName"].values
            area_type = "domain"

    LOGGER.debug(f"Name : {str(area_name)}, Type: {str(area_type)}")
    return (str(area_name), str(area_type))


class AltitudeName:
    """Classe permettant de caractériser un nom contenant des informations
    d'altitudes.
    """

    altitude_pattern: re.Pattern = re.compile(r"(\d+ m)\b")  # exemple : 1600 m
    entre_start: tuple = ("entre")
    dessus_start: tuple = ("au-dessus", "en dessus")
    dessous_start: tuple = ("au-dessous", "en dessous")

    def __init__(self, name: str):
        self.name = name

    @property
    def altitude(self) -> list:
        """Property that returns the altitude information contains in the self.name.
        Returns an empty list if not valid.

        Returns:
            list: Altitude informations.
        """
        return self.altitude_pattern.findall(self.name)

    @property
    def kind(self) -> str:
        """Property that describe the kind of altitude name, among :
            - "entre"
            - "dessus"
            - "dessous"
            - "invalide"

        Returns:
            str: type de nom d'altitude.
        """
        nb_altitudes = len(self.altitude)
        name_startswith = self.name.lower().startswith
        if nb_altitudes == 1:
            if name_startswith(self.dessus_start):
                return "dessus"
            if name_startswith(self.dessous_start):
                return "dessous"
            return "invalide"
        if nb_altitudes == 2 and name_startswith(self.entre_start):
            return "entre"
        return "invalide"

    def is_valid(self) -> bool:
        """checks if the given name contains altitudes informations

        Returns:
            bool: True if it contains altitude, else False
        """
        return self.kind != "invalide"

    def is_entre(self) -> bool:
        """checks whether the given name is of "entre" kind

        Returns:
            bool: True if is of kind "entre"
        """
        return self.kind == "entre"

    def is_dessus(self) -> bool:
        """checks whether the given name is of "dessus" kind

        Returns:
            bool: True if is of kind "dessus"
        """
        return self.kind == "dessus"

    def is_dessous(self) -> bool:
        """checks whether the given name is of "dessous" kind

        Returns:
            bool: True if is of kind "dessous"
        """
        return self.kind == "dessous"

    def get_low(self) -> str:
        """returns lower altitude information.
        Returns None if not valid.

        Returns:
            str: Lower altitude information.
        """
        if self.is_valid():
            return self.altitude[0]
        return None

    def get_high(self) -> str:
        """Returns higher altitude information.
        Returns None if not valid.

        Returns:
            str: Higher altitude information.
        """
        if self.is_valid():
            return self.altitude[-1]
        return None

    def rename_sub_inter(self, sub_name: str) -> str:
        """rename the intersection between the area named by self.name and
        another area named sub_name.
        Warning : the sub area must be contained in the self area !

        Args:
            sub_name (str): sub area's name

        Returns:
            str: name of the intersection between self and the sub areas.

        TO DO : reprendre la logique probablement foireuse !
        """
        if not self.is_valid():
            return sub_name

        sub_alt_name = AltitudeName(sub_name)

        if sub_alt_name.is_entre():  # cas simple avec la sub area deja entre
            return sub_name

        if self.is_entre():
            if sub_alt_name.is_dessus():
                return f"entre {sub_alt_name.get_low()} et {self.get_high()}"
            if sub_alt_name.is_dessous():
                return f"entre {self.get_low()} et {sub_alt_name.get_high()}"
            return f"{self.name} pour {sub_name}"

        if self.is_dessus():
            if sub_alt_name.is_dessus():
                return sub_name
            if sub_alt_name.is_dessous():
                return f"entre {self.get_low()} et {sub_alt_name.get_high()}"
            return f"{self.name} pour {sub_name}"

        if self.is_dessous():
            if sub_alt_name.is_dessus():
                return f"entre {sub_alt_name.get_low()} et {self.get_high()}"
            if sub_alt_name.is_dessous():
                return sub_name
            return f"{self.name} pour {sub_name}"

        return sub_name

    def rename_sub_diff(self, sub_name: str) -> str:
        """rename the difference between the area named self.name and
        another area, contained in self, named sub_name.
        Warning : the sub area must be contained in the self area !

        Args:
            sub_name (str): sub area's name

        Returns:
            str: name of the difference between self and the sub areas.

        TO DO : reprendre la logique probablement foireuse !
        """
        new_name = f"comp_{sub_name}"

        if not self.is_valid():
            return new_name

        sub_alt_name = AltitudeName(sub_name)
        if not sub_alt_name.is_valid() or sub_alt_name.is_entre():
            return new_name

        if self.is_entre():
            if sub_alt_name.is_dessus():
                return f"entre {self.get_low()} et {sub_alt_name.get_low()}"
            if sub_alt_name.is_dessous():
                return f"entre {sub_alt_name.get_high()} et {self.get_high()}"
        if sub_alt_name.is_dessus():
            if self.is_dessous():
                return f"entre {sub_alt_name.get_high()} et {self.get_low()}"
            if self.is_dessus():
                return f"entre {self.get_high()} et {sub_alt_name.get_low()}"
            return f"au dessus de {sub_alt_name.get_high()}"
        if sub_alt_name.is_dessous():
            if self.is_dessus():
                return f"entre {self.get_high()} et {sub_alt_name.get_low()}"
            if self.is_dessous():
                return f"entre {sub_alt_name.get_high()} et {self.get_low()}"
            return f"au-dessus de {sub_alt_name.get_high()}"
        return new_name


class GenericArea:
    """objet GenericArea contenant le domaine, le masque, l'ensemble
    des zones l'IoUT
    """

    def __init__(self, domain, mask=None, full_list=None, IoUT=DefaultIOU):
        """
        Args:
            domain (dataArray ou None): Le domaine
            mask ([dataArray or None ]): Zones générique (pas par altitude)
            full_list (dataArray) : la liste de l'ensemble des zones
                (incluant celles par altitude)
        """
        self.mask = mask
        self.domain = domain
        self.full_list = full_list
        self.IoUT = IoUT

    def intersect(self, area, IoUT=None):
        """[summary]

        Args:
            area ([type]): [description]
            IoUT (Integer): Threshold. Utilisé seulement si appelé a partir
                de la classe AltArea. Defaults to None.

        Returns:
            [type]: [description]
        """
        if IoUT is None:
            IoUT = self.IoUT
        result = None
        if self.mask is None:
            LOGGER.debug("mask is absent")
            return result
        id_mask = self.filter_areas(area, self.mask)
        temp_area = self.mask.sel(id=id_mask) * area.copy()
        ratio = temp_area.sum(["latitude", "longitude"]) / self.mask.sum(
            ["latitude", "longitude"]
        )
        # La aussi il faut rajouter quelque chose pour que l'IoU soit different
        # pour une zone d'altitude
        result = temp_area.sel(id=(ratio > IoUT).values)
        result["areaName"] = self.mask.sel(id=result.id)["areaName"]
        return result

    def append_in_full_list(self, d_area):
        """ Permet d'ajouter d'autres zones à la liste complète

        Args:
            d_area (xr.DataArray):
        """
        name = self.full_list.name
        self.full_list = xr.merge([self.full_list, d_area])[name]

    @staticmethod
    def filter_areas(area, l_area, equal_ok=False):
        """
        On va filtrer toutes les zones qui incluent complétement la zone
        qu'on cherche à diviser ou qui sont complétement disjointes.
        Ces zones là ne sont pas intéressantes.

        Args:
            area (dataArray): La zone qu'on cherche à découper
        returns:
            [] : liste des id des zones "inclues" dans la zone
        """
        if equal_ok:
            idx = (l_area * area.squeeze()).sum(
                ["longitude", "latitude"]
            ) <= area.squeeze().sum(["longitude", "latitude"])
        else:
            idx = (l_area * area.squeeze()).sum(
                ["longitude", "latitude"]
            ) < area.squeeze().sum(["longitude", "latitude"])
        idb = (l_area * area.squeeze()).sum(["longitude", "latitude"]) >= 1
        result = l_area.sel(id=operator.and_(idx, idb)).id.values
        return result

    def get_other_altitude_area(self, d_area):
        """ Le but de la fonction est de définir de nouvelles
        "zones d'altitudes" (du type entre 200 et 400m).
        Ces zones ne pourront être utilisée que pour le nommage.


        Args:
            d_area ([type]): Un dataArray des zones d'altitudes
        ToDo : Mettre un test
        Return :
            xr.DataArray : Un DataArray contenant les nouvelles zones créées.
        """
        d_area2 = copy.deepcopy(d_area)
        d_area2 = d_area2.rename({"id": "id1"})
        dinter = d_area2 * d_area
        nb_inter = dinter.sum(["latitude", "longitude"])
        res = (
            (nb_inter > 0)
            * (nb_inter < d_area.sum(["latitude", "longitude"]))
            * (nb_inter < d_area2.sum(["latitude", "longitude"]))
        )
        l_set = []
        l_out = []
        name_out = []
        # On commence par l'intersection entre zones (par ex <300 et >200)
        for idi in res.id.values:
            domain = d_area.sel(id=idi)
            l_area = d_area2.sel(id1=res.sel(id=idi))
            if len(l_area) > 0:
                for area in l_area:
                    id1 = area.id1.values
                    ref = (idi, id1)
                    ref_bis = (id1, idi)
                    # On regarde que la combinaison est bien absente
                    if not (ref in l_set) and not (ref_bis in l_set):
                        name_inter = self.rename_inter(
                            str(domain.areaName.values), [str(area.areaName.values),]
                        )
                        l_set.append(ref)
                        intersection = (
                            dinter.sel(id=idi)
                            .sel(id1=id1)
                            .drop(["id", "id1", "areaType"])
                        )
                        intersection = intersection.expand_dims("id").assign_coords(
                            id=[f"inter_{str(idi)}_{str(id1)}",]
                        )
                        intersection["areaName"] = (("id"), name_inter)
                        intersection["areaType"] = (("id"), ["Altitude",])
                        l_out.append(intersection)
                        name_out.append(name_inter)

        # On regarde ensuite les complémentaires "au sein de la zone"
        # Par ex > 1000 dans la zone >700 => Entre 700 et 1000
        comp_area = d_area.copy() - (d_area2 > 0)
        d_comp = comp_area.where(comp_area > 0)
        nb_comp = d_comp.sum(["latitude", "longitude"])
        res = (
            (nb_comp > 0)
            * (nb_comp < d_area.sum(["latitude", "longitude"]))
            * (nb_comp < d_area2.sum(["latitude", "longitude"]))
        )
        for idi in res.id.values:
            domain = d_area.sel(id=idi)
            l_area = d_area2.sel(id1=res.sel(id=idi))
            if len(l_area) > 0:
                for area in l_area:
                    id1 = area.id1.values
                    ref = (idi, id1)
                    ref_bis = (id1, idi)
                    if not (ref in l_set) and not (ref_bis in l_set):
                        name_comp = self.rename_difference(
                            str(domain.areaName.values), [str(area.areaName.values),]
                        )
                        if name_comp not in name_out:
                            l_set.append(ref)
                            difference = (
                                d_comp.sel(id=idi)
                                .sel(id1=id1)
                                .drop(["id", "id1", "areaType"])
                            )
                            difference = difference.expand_dims("id").assign_coords(
                                id=[f"diff_{str(idi)}_{str(id1)}",]
                            )
                            difference["areaName"] = (("id"), name_comp)
                            difference["areaType"] = (("id"), ["Altitude",])
                            l_out.append(difference)
                            name_out.append(name_comp)
        name = d_area.name
        dout = xr.merge(l_out)[name]
        return dout

    @staticmethod
    def rename_inter(domain_name: str, area_names: List[str]) -> List[str]:
        """
        Renomme les objets de area_names pour qu'ils correspondent à
        l'intersection avec le domaine.
        Traite seulement les zones d'altitudes.

        Args:
            domain_name (str): Nom du domaine
            area_names (List[str]): Liste de noms de zones

        Returns:
            List[str]: Liste comportant les nouveaux noms de zones.
        """
        domain_alt_name = AltitudeName(domain_name)
        return list(map(domain_alt_name.rename_sub_inter, area_names))

    @staticmethod
    def rename_difference(domain_name: str, area_names: List[str]) -> List[str]:
        """
        Renomme les objets de area_names pour qu'ils correspondent à
        la différence avec le domaine (domain - area).
        Traite seulement les zones d'altitudes.

        Args:
            domain_name (str): Nom du domaine
            area_names (List[str]): Liste de noms de zones

        Returns:
            List[str]: Liste comportant les nouveaux noms de zones.
        """
        domain_alt_name = AltitudeName(domain_name)
        return list(map(domain_alt_name.rename_sub_diff, area_names))

    def get_best_comp(self, comp_area, full_list):
        """ Cette fonction va permettre de trier les complémentaires.
        On fait une distinction sur les zones d'altitudes et les autres

        Args:
            comp_area (xr.Dataarray): La zone complémentaire dont on doit trouver le nom
            full_list (xr.Dataarray): La liste des zones dans lequel on a le droit de
                piocher

        Returns:
            (xr.Dataarray, xr.Dataarray, xr.Dataarray):
               1. Est-on supérieur au ratio imposé pour la similarité ?
               2. La liste des ids des maximums ?
               3. Est-ce une zone d'altitude ou non ?
        """
        # On va trier les zones : on va mettre les zones d'altitude d'un côté et
        # les autres zones de l'autre.

        if (
            hasattr(full_list, "areaType")
            and (full_list["areaType"] == "Altitude").sum().values > 0
        ):
            idx = full_list["areaType"] == "Altitude"
            alt_area = full_list.sel(id=idx)
            idx_other = set(full_list.id.values).difference(set(alt_area.id.values))
            other_area = full_list.sel(id=list(idx_other))
            iou_alt = compute_IoU(comp_area, alt_area)
            # Max, est-on superieur au seuil et nom.
            m_alt = iou_alt.max("id")
            r_alt = m_alt > IoUAlt
            a_alt = iou_alt.argmax("id")
            if len(list(idx_other)) > 0:
                iou_other = compute_IoU(comp_area, other_area)
                # Donne le max de l'IoU
                m_other = iou_other.max("id")
                # Ratio et argmax (donne le ratio et le nom )
                r_other = m_other > self.IoUT
                a_other = iou_other.argmax("id")
                # Si on a un seul ratio on prend celui là et la zone correspondante.
                # si on a plusieurs ratio_ok il faut prendre le meilleur des deux et
                # recupérer l'id correspondant
                ratio = r_alt + r_other
                ids = (
                    r_alt
                    * ((1 - r_other) + r_other * (m_alt > m_other))
                    * alt_area.isel(id=a_alt).id.values
                    + r_other
                    * ((1 - r_alt) + r_alt * (m_other >= m_alt))
                    * other_area.isel(id=a_other).id.values
                )
                alti_field = r_alt * ((1 - r_other) + r_other * (m_alt > m_other))
            else:
                ratio = r_alt
                ids = r_alt * alt_area.isel(id=a_alt).id.values
                alti_field = r_alt
        else:
            IoU = compute_IoU(comp_area, full_list)
            IoUMax = IoU.max("id")
            # Permet de savoir à quelle zone on l'associe.
            a_max = IoU.argmax("id")
            ids = full_list.isel(id=a_max).id
            ratio = IoUMax > self.IoUT
            alti_field = ratio * False
        return ratio, ids, alti_field

    def difference(self, area):
        """
            Compute the difference between the list of area and the input area.
            If the corresponding area IoU between complementary and original area
            (in the list) is greater than a threshold
            we keep it. Otherwise we discard it.

            We also rename this area according to the "closest" area in the full list.

        Args:
            area ([type]): [description]

        Returns:
            [type]: [description]
        """
        result = None
        if self.mask is None:
            LOGGER.debug("mask is absent")
            return result
        # id_full0 = self.filter_areas(area, self.full_list, equal_ok=True)
        id_full = self.filter_areas(area, self.full_list, equal_ok=False)  #
        # diff = set(id_full0).difference(set(id_full))
        # LOGGER.error(f"Liste des ids avec et sans contrainte {diff}")
        # Option pour ne pas avoir un complementaire qui porte le meme nom que le
        # 'domaine'.
        if len(id_full) == 0:
            LOGGER.warning(
                f"Apres contrôle, pas de zone disponible pour {area.areaName.values}"
            )
            return None
        id_mask = self.filter_areas(area, self.mask)
        full_list = self.full_list.copy()
        full_list = full_list.sel(id=id_full)
        comp_area = (area.squeeze().copy() - (self.mask.sel(id=id_mask) > 0)) * area
        comp_area = comp_area.where(comp_area > 0)

        # On change l'identifiant de nom
        comp_area = comp_area.rename({"id": "id1"})
        try:
            ratio, ids, alti_field = self.get_best_comp(comp_area, full_list)
        except ValueError as e:
            LOGGER.error(f"Ful list of possibility is {full_list}")
            LOGGER.error(f"The input area is {area}")
            LOGGER.error(
                f"An error has happend in area_algebre. Comp_area is {comp_area}"
            )
            raise (e)
        # On regarde quels sont les ids des zones complémentaire qu'on va conserver
        # result = comp_area.sel(id1=ratio)
        result = comp_area.sel(id1=ratio)
        if ratio.sum() >= 1:
            # On va maintenant essayer de renommer.
            # areaNames = []
            areaBis = []
            areaType = []
            for idi in ids.sel(id1=ratio):
                areaBis.append(str(full_list.sel(id=idi.values)["areaName"].values))
                areaType.append(str(full_list.sel(id=idi.values)["areaType"].values))
            result["areaName"] = (("id1"), areaBis)
            # result["areaType"] = (("id1"),areaType)
            result = result.rename({"id1": "id"})
        else:
            # On a ici aucun résultat
            result = None
        return result


class AltArea(GenericArea):
    """Permet de générer un objet GenericArea à partir de données
    d'altitude

    Args:
        GenericArea

    Returns:
        GenericArea: objet AltArea
    """

    @staticmethod
    def restrict_to(area, pos_area):
        domain_alt_name = AltitudeName(str(area.areaName.values))
        drop_id = []
        for otherAreaName in pos_area.areaName:
            # TO DO : change the messy logic
            area_alt_name = AltitudeName(str(otherAreaName.values))

            if domain_alt_name.is_dessus():
                if area_alt_name.is_dessus() and alt_change(
                    area_alt_name.get_low()
                ) < alt_change(domain_alt_name.get_low()):
                    drop_id.append(str(otherAreaName.id.values))
            elif domain_alt_name.is_dessous():
                if area_alt_name.is_dessous() and alt_change(
                    area_alt_name.get_low()
                ) > alt_change(domain_alt_name.get_low()):
                    drop_id.append(str(otherAreaName.id.values))
        if drop_id != []:
            idx = list(set(pos_area.id.values).difference(set(drop_id)))
        else:
            idx = pos_area.id.values
        return pos_area.sel(id=idx)

    def intersect(self, area):
        """ Calcul de l'intersection entre une zone et la liste de zone d'altitude.
            Seul les zones "correctes" sont retournées

        Args:
            area (dataArray): Une zone spécifique

        Returns:
            [none or dataArray]:
                Une liste des zones qui ont une intersection "correcte"
                avec la zone en question.
                Ces zones ont été restreints à la zone en question.
                Elles ont potentiellement été renommés
        """
        result = None
        if self.mask is None:
            return result
        if area["areaType"] == "Altitude":
            id_mask = self.filter_areas(area, self.mask)
            temp_area = self.mask.sel(id=id_mask) * area.copy()
            # On ne considere que les zones qui couvrent au moins 5% de l'aire
            idx = temp_area.sum(["latitude", "longitude"]) > 0.05 * area.sum(
                ["latitude", "longitude"]
            )
            result = temp_area.isel(id=idx.values)
            l_name = self.mask.sel(id=result.id)["areaName"].values
            result["areaName"] = (
                "id",
                self.rename_inter(str(area.areaName.values), l_name.astype(str)),
            )
            # On va encore restreindre aux cas logiques. On ne veut pas avoir >250 si
            # le domaine est >300.
            result = self.restrict_to(area, result)
        else:
            result = super().intersect(area, IoUT=IoUAlt)
        return result

    def difference(self, area):
        """
        On souhaite avoir le complémentaire de chaque zone à l'intérieur
        du domaine D (i-e D - area).

        Si la zone d'entrée est une zone d'altitude, on sait la nommer.
        Si ça n'en est pas une, on passe par la méthode générique.
        On vérifiera (dans un second temps) si on peut nommer cette zone.

        Args:
            area (dataArray): Une zone spécifique

        Returns:
            [none or dataArray]:
                Une liste des zones qui ont une intersection "correcte"
                avec la zone en question.
                Ces zones ont été restreints à la zone en question.
                Elles ont potentiellement été renommés
        """
        result = None
        if self.mask is None:
            return result
        if area["areaType"] == "Altitude":
            id_mask = self.filter_areas(area, self.mask)
            comp_area = area.copy() - (self.mask.sel(id=id_mask) > 0)
            comp_area = comp_area.where(comp_area > 0)
            # On ne considere que les zones qui couvrent au moins 5% de l'aire
            idx = comp_area.sum(["latitude", "longitude"]) > 0.05 * area.sum(
                ["latitude", "longitude"]
            )
            result = comp_area.isel(id=idx.values)
            l_name = self.mask.sel(id=result.id)["areaName"].values
            result["areaName"] = (
                "id",
                self.rename_difference(str(area.areaName.values), l_name.astype(str)),
            )
        else:
            result = super().difference(area)
        return result


class RiskArea:
    """ Initialise les zones pour les risques """

    def __init__(self, domain, areaList, IoUT=DefaultIOU, between_authorized=False):
        """
        Args:
            domain (dataArray): [description]
            areaList
            IoUT
            Between_authorized : Autorise-t-on les zones "entre deux altitudes" a être
        """
        self.IoUT = IoUT
        self.domain = domain
        self.full_list = areaList
        self.min_percent = 0.7
        self.between_authorized = between_authorized
        self.alt_area, self.other_area = self.separate_alt_other()

    def separate_alt_other(self):
        """
        Permet de séparer les zones de type altitudes des autres.
        Les zones d'altitudes vont avoir des
        """
        if hasattr(self.full_list, "areaType"):

            # On va récupérer les zones qui sont des zones d'altitudes
            idx = self.full_list["areaType"] == "Altitude"

            da_alt = self.full_list.sel(id=idx)
            idx_other = set(self.full_list.id.values).difference(set(da_alt.id.values))
            da_other = self.full_list.sel(id=list(idx_other))
            alt = AltArea(self.domain, da_alt, self.full_list, IoUT=self.IoUT)
            other = GenericArea(self.domain, da_other, self.full_list, IoUT=self.IoUT)

            # On calcul les noms d'autres zones d'altitude
            if self.between_authorized:
                if idx.sum() > 0:
                    new_area = other.get_other_altitude_area(da_alt)
                    # On les rajoute à la full_list
                    if len(new_area.id) > 0:
                        LOGGER.debug("Adding area between altitudes")
                        other.append_in_full_list(new_area)
                        alt.append_in_full_list(new_area)
        else:
            alt = AltArea(self.domain, full_list=self.full_list, IoUT=self.IoUT)
            other = GenericArea(
                self.domain, self.full_list, self.full_list, IoUT=self.IoUT
            )
        return alt, other

    def get_possibilities(self, area):
        """
        Retourne toute les zones qui sont possibles pour cette zone.
        La réponse peu dépendre du type de zone en entrée.

        1. Si la zone est une zone d'altitude, on retourne
            - Toutes les zones d'altitudes qui ont une intersection non nulle
            - Toutes les autres zones qui sont au moins à 'min_percent' dans la zone
                et dont on peut nommer le complémentaire.
        2. Sinon
            - Toutes les zones qui sont au moins à 'min_percent" dans la zone
                et dont on peut nommer le complémentaire.

        Cette fonction peut évoluer en fonction
        Args:
            area (da): Une dataArray contenant une unique zone
        """
        pos_inter = self.intersect(area)
        pos_comp = self.difference(area)
        if pos_inter is not None and pos_comp is not None:
            common_id = set(pos_inter.id.values).intersection(set(pos_comp.id.values))
            if common_id != set():
                return (
                    pos_inter.sel(id=list(common_id)),
                    pos_comp.sel(id=list(common_id)),
                )
            else:
                LOGGER.debug("Pas d'id en commum")
                return None, None
        else:
            LOGGER.debug("Aucune zone dans l'intersection ou le complementaire")
            return None, None

    def intersect(self, area):
        """
            Retourne l'intersection avec l'aire.
        """
        alt_intersect = self.alt_area.intersect(area)
        other_intersect = self.other_area.intersect(area)
        return generic_merge(alt_intersect, other_intersect)

    def difference(self, area):
        alt_diff = self.alt_area.difference(area)
        other_diff = self.other_area.difference(area)
        return generic_merge(alt_diff, other_diff)


if __name__ == "__main__":
    from mfire.utils.xr_utils import MaskLoader

    da = MaskLoader(
        filename="/scratch/labia/chabotv/tmp/wd_20201208T164500/mask/HauteGaronne.nc",
        grid_name="eurw1s100",
    ).load()
    geo_id = "Haute-Garonne"
    id_list = [idi for idi in da.id.values if idi.startswith(geo_id) and idi != geo_id]
    id_list.extend(
        [
            "ASPET",
            "AUTERIVE",
            "BAGNERES-DE-LUCHON",
            "BOULOC",
            "BOULOGNE-SUR-GESSE",
            "BOUSSENS",
            "CADOURS",
            "CARAMAN",
            "CARBONNE",
            "CASTELGINEST",
            "CIER-DE-LUCHON",
            "CIERP-GAUD",
            "Coteaux du Lauragais et du Volvestre",
            "FLOURENS",
            "FOS",
            "LARRA",
            "LAYRAC-SUR-TARN",
            "LE_FOUSSERET",
            "LISLE-EN-DODON",
            "LOUDET",
            "LUCHON",
            "MONTESQUIEU-VOLVESTRE",
            "MURET",
            "NAILLOUX",
            "PIBRAC",
            "Plaine",
            "REVEL",
            "ROQUEFORT-SUR-GARONNE",
            "SAINT-BEAT",
            "SAINT-BERTRAND-DE-COMMINGES",
            "SAINT-GAUDENS",
            "SAINT-LYS",
            "SAINT-PAUL-DOUEIL",
            "SAINT-SULPICE-SUR-LEZE",
            "SAINTE-FOY-DE-PEYROLIERES",
            "SAUBENS",
            "TOULOUSE",
            "TOULOUSE-BLAGNAC",
            "VERFEIL",
            "VILLEFRANCHE",
            "VILLEFRANCHE-DE-LAURAGAIS",
            "VILLENEUVE-DE-RIVIERE",
            "coteaux de Cadours et du Boulonnais",
            "montagne",
            "piémont",
        ]
    )
    domain = da.sel(id=geo_id).expand_dims("id")
    areaHandler = RiskArea(domain, da.sel(id=id_list), IoUT=0.4)
    descriptiveTest = da.sel(id="Haute-Garonne_compass__Sud")
    dcomp = areaHandler.difference(descriptiveTest)
    print(dcomp.areaName.values)
    # inter, comp = areaHandler.get_possibilities(descriptiveTest)
    areaHandler = RiskArea(
        domain, da.sel(id=id_list), IoUT=0.4, between_authorized=True
    )
    descriptiveTest = da.sel(id="Haute-Garonne_compass__Sud")
    # dout = areaHandler.intersect(descriptiveTest)
    dcomp = areaHandler.difference(descriptiveTest)
    print(dcomp.areaName.values)
