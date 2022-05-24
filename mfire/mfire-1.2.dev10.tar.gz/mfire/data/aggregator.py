"""
@package core.aggregator

Aggregation module
"""
from __future__ import annotations

import operator
import xarray as xr
from typing import Optional, List, Union
from enum import Enum

from mfire.settings import get_logger
from mfire.utils.xr_utils import mask_set_up, rounding


"""
Dictionnaire d'aggregation.
Le dictionnaire donne les arguments obligatoire pour chaque methode.
Une valeur par defaut est présente pour chaque méthode.
Cette valeur sera utilisé si cette derniere venait a ne pas etre renseignée.

AGGREGATION_CATALOG : L'ensemble des méthodes d'aggrégation.
"""

AGGREGATION_CATALOG = {
    "density": {},
    "requiredDensity": {"dr": 0.5},
    "requiredDensityWeighted": {
        "dr": 0.5,  # Le threshold par defaut
        "central_weight": 10,  # la ponderation dans la zone
        "outer_weight": 1,  # La ponderation en dehors de la zone
    },
    "requiredDensityConditional": {"dr": 0.5},
    "all": {},
    "any": {},
    "max": {},
    "mean": {},
    "median": {},
    "min": {},
    "sum": {},
    "std": {},
    "var": {},
    "quantile": {"q": 0.5},
}


class AggregationMethod(str, Enum):
    """Création d'une classe d'énumération contenant les différentes
    méthodes d'aggregation
    """

    MEAN = ("mean", False)
    DENSITY = ("density", True)
    RDENSITY = ("requiredDensity", True)
    RDENSITY_WEIGHTED = ("requiredDensityWeighted", True)
    RDENSITY_CONDITIONAL = ("requiredDensityConditional", True)
    ALL = ("all", True)
    ANY = ("any", True)
    MAX = ("max", False)
    MIN = ("min", False)
    MEDIAN = ("median", False)
    SUM = ("sum", False)
    STD = ("std", False)
    VAR = ("VAR", False)
    QUANTILE = ("quantile", False)

    def __new__(cls, value: str, is_after_threshold: bool) -> AggregationMethod:
        """Initialize a new Method object

        Args:
            value (str): String value of the Aggregation Method
            is_after_threshold (bool): Whether the given method is to use
                only after aggregation. For instance, given a field of floating values:
                * 'density' method is is_after_threshold because the expression
                    "density(field) > threshold" has no sense.
                * 'mean' method is not is_after_threshold because the expression
                    "mean(field) > threshold" has a sense.

        Returns:
            Method: New Method object
        """
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.is_after_threshold = is_after_threshold
        return obj


# Logging
LOGGER = get_logger(name="aggregator", bind="aggregation")


class InputError(ValueError):
    """
    Class for InputError
    """

    pass


class Aggregator:
    """
    Class for aggregating fields (xr.DataArray)
    """

    def __init__(
        self,
        da: xr.DataArray,
        mask: xr.DataArray = None,
        aggregate_dim: Optional[Union[List[str], str]] = None,
    ):
        """
        Initialize an aggregator object
        @param da (xarray.DataArray) - Fields to be aggregated
        @param mask (xarray.DataArray, optional) - Mask to apply
        @param aggregate_dim (str or sequence of str, optional)
            - Dimension(s) over which to apply aggregation.
        """
        self.aggregate_dim = aggregate_dim
        if aggregate_dim is None:
            self.aggregate_dim = ["latitude", "longitude"]
        self.da = da.copy(deep=True)
        self.mask_da = None
        if isinstance(mask, xr.DataArray):
            self.mask_da = mask.copy(deep=True)

    def masking(self):
        """
        Apply self.mask_da to the self.da DataArray
        Could be use if masking has not already been perform
        """
        if self.mask_da is not None:
            LOGGER.debug("Masking array", func="masking")
            self.da = self.da * self.mask_da

    def compute(self, method, **kwargs):
        """
        Aggregates self.da DataArray using the specific 'method' over
        the self.aggregate_dim dimension(s)
        @param method (str) - Name of the aggregation method
            (to choose among the AGGREGATION_CATALOG)
        @param **kwargs (dict) - Keyword arguments specific to the chosen
            aggregation method
        @return reduced (xarray.DataArray) - New DataArray object with the
            method applied to its data and the the self.aggregate_dim removed.
        """
        self.masking()
        if method not in AGGREGATION_CATALOG:
            raise ValueError("Aggregation method '{}' does not exist".format(method))

        # On met a jour les arguments pour avoir au minimum les arguments
        # obligatoires
        temp_kwargs = AGGREGATION_CATALOG[method].copy()
        temp_kwargs.update(kwargs)
        if isinstance(method, AggregationMethod):
            tmp_krgs = {k: v for k, v in temp_kwargs.items() if v is not None}
        else:
            tmp_krgs = temp_kwargs
        # A updater : passer par self.__get_attribute__(method) pour les
        # fonctions internes
        try:
            if method == "density":
                LOGGER.debug("AggregationMethod", density=1, func="compute")
                output = self.density(**tmp_krgs).compute()
            elif method == AggregationMethod.RDENSITY:
                LOGGER.debug("AggregationMethod", requiredDensity=1, func="compute")
                output = self.requiredDensity(**tmp_krgs).compute()
            elif method == AggregationMethod.RDENSITY_WEIGHTED:
                LOGGER.debug(
                    "AggregationMethod", requiredDensityWeighted=1, func="compute"
                )
                output = self.drr_weighted(**tmp_krgs).compute()
            elif method == AggregationMethod.RDENSITY_CONDITIONAL:
                LOGGER.debug(
                    "AggregationMethod", requiredDensityConditional=1, func="compute"
                )
                output = self.drr_conditional(**tmp_krgs).compute()
            elif hasattr(self.da, method):
                LOGGER.debug("AggregationMethod", xr_method=method, func="compute")
                output = self.da.__getattribute__(method)(
                    dim=self.aggregate_dim, **tmp_krgs
                ).compute()
            else:
                raise ValueError(
                    f"AggregationMethod '{method}' in catalog but not implemented"
                )
        except Exception as excpt:
            LOGGER.error(
                "Getting an error in aggregation",
                shape=self.da.shape,
                method=method,
                count=int(self.da.count().compute().values),
                func="compute",
            )
            raise ValueError from excpt
        return output

    def density(self, **kwargs):
        """
        Returns the density risk (Densité De Risque) of the self.da DataArray
        over the self.aggregate_dim dimension(s)
        @param **kwargs (dict) - Keyword arguments specific to xarray's sum method.
        @return reduced (xarray.DataArray) - New DataArray object with the ddr
            applied to its data and the self.aggregate_dim removed.
        """
        if self.mask_da is not None:
            return (
                self.da.sum(dim=self.aggregate_dim, **kwargs)
                * 1.0
                / self.mask_da.sum(self.aggregate_dim, **kwargs)
            )
        else:
            return (
                self.da.sum(dim=self.aggregate_dim, **kwargs)
                * 1.0
                / self.da.count(dim=self.aggregate_dim, **kwargs)
            )

    def requiredDensity(self, dr, **kwargs):
        """
        Threshold thresh applied to the density risk of the self.da DataArray
            over the self.aggregate_dim dimension(s)
        @param dr (float in range [0, 1]) - Threshold to apply
        @param **kwargs (dict) - Keyword arguments specific to the previous
            ddr method.
        @return reduced (xarray.DataArray) - New DataArray object with
            'thresholded ddr' applied to its data and the self.aggregate_dim
            removed.
        """
        if dr > 1 or dr < 0:
            raise InputError(f"Threshold given = {dr}, while expected to be in [0,1].")
        return self.density(**kwargs) > dr

    def setting_mask_for_aggregation(self, central_mask_id):
        """
        setting_mask_for_aggregation
          On charge le masque, on le crop et on le met sur la bonne grille pour
          que les calculs soit rapide

        Args:
            central_mask_id ([dictionnaire]): Contient file et mask_id
        """
        grid = self.da.attrs["PROMETHEE_z_ref"]

        if not isinstance(central_mask_id, dict):
            central_mask_id = dict(central_mask_id)

        central_file = central_mask_id["file"]
        central_id = central_mask_id["mask_id"]

        mask = xr.open_dataset(central_file)[grid]
        dict_dims = {}
        # On renomme les dimension pour avoir latitude et longitude (au lieu de
        # latitude_globe05)
        for x in mask.dims:
            dict_dims[x] = x.split("_")[0]
        mask = mask.rename(dict_dims)
        central_mask = rounding(mask.sel(id=central_id))
        central_mask = mask_set_up(central_mask, self.da)
        # Ensuite on en extrait un masque central et un masque périphérique.
        self.define_central_periph_mask(central_mask)

    def define_central_periph_mask(self, central_mask):
        # On commence par construire le dictionnaire pour le cropping
        input_dim = set(self.da.dims)
        # On regarde quelles sont les dimensions qui ne sont ni dependante des
        # dimensions id, ni du temps
        sel_dim = input_dim.difference(set(self.aggregate_dim).union(set(["id"])))
        # On suppose qu'on cree un masque par dimension id
        dout = {}
        for x in sel_dim:
            dout[x] = 0
        mask = self.da.isel(dout) * 0 + 1
        # On crop le central_mask
        if set(central_mask.dims) != set(self.aggregate_dim):
            LOGGER.error(
                f"Error : the central_mask dimensions {central_mask.dims} are "
                f"different from the aggregation dimension {self.aggregate_dim}",
                func="define_central_periph_mask",
            )
        # On met a jour le mask central.
        # S'il y a differentes zones (masques) on etend donc la dimension du
        # masque central (et on sait pour chacune des regions si le masque
        # central en fait partie)
        self.central_mask = central_mask * mask
        mout = mask - self.central_mask.where(self.central_mask > 0, 0)
        self.periph_mask = mout.where(mout > 0)

    def weighted_density(self, central_weight, outside_weight):
        """Calcul une densite ponderee

        Args:
            central_weight (int): Poids a l'interieur de la zone centrale
            outside_weight (int): Poids a l'exterieur de la zone centrale
        Returns:
            [data_array]: La densité pondérée
        """
        # On va combiner les deux densités
        if not hasattr(self, "central_mask"):
            raise (
                InputError(
                    "You should define the central area before calling this function"
                )
            )
        #       self.setting_mask_for_aggregation(fmask,central_mask_id)
        central_pix = self.central_mask.sum(dim=self.aggregate_dim).values
        out_pix = self.periph_mask.sum(dim=self.aggregate_dim).values
        total_pix = central_weight * central_pix + outside_weight * out_pix
        density = (
            (self.da * self.periph_mask).sum(dim=self.aggregate_dim)
            * outside_weight
            / total_pix
            + (self.da * self.central_mask).sum(dim=self.aggregate_dim)
            * central_weight
            / total_pix
        )
        return density

    def drr_conditional(self, dr, central_mask_id, **kwargs):
        """Calcul de l'occurrence du risque en prenant en compte que si un pixel
        de la zone centrale est touché alors le risque est levé.

        Args:
            thresh (float): Un entier compris entre 0 et 1 nous disant quelle est
                la densité a atteindre
            central_mask_id (dict):  Dictionnaire contenant le path et l'id du mask

        Returns:
            [data_array]: L'occurrence du risque
        """
        self.setting_mask_for_aggregation(central_mask_id)
        if dr > 1 or dr < 0:
            raise InputError(f"Threshold given = {dr}, while expected to be in [0,1].")
        # Calcul du risque en fonction de la densite
        risk_1 = self.density(**kwargs) > dr
        # Calcul du risque sur la zone a risque
        risk_2 = (self.da * self.central_mask).sum(dim=self.aggregate_dim) > 0
        # Si le risk dépendant de la densité est activé ou si le risque parlant
        # de la zone centrale est activé.
        return operator.or_(risk_1, risk_2)

    def drr_weighted(self, dr, central_mask_id, central_weight, outer_weight):
        """ Calcul l'occurrence du risque en prendant en compte une densité pondérée
        (entre zone centrale et zone extérieure)

        Args:
            thresh (float): Un entier compris entre 0 et 1 nous disant quelle est
                la densité a atteindre
            central_mask_id (dict):  Dictionnaire contenant le path et l'id du mask
            central_weight (int): Poids a l'interieur de la zone centrale
            outer_weight (int): Poids a l'exterieur de la zone centrale
        Returns:
            [data_array]: L'occurrence du risque
        """
        self.setting_mask_for_aggregation(central_mask_id)
        if dr > 1 or dr < 0:
            raise InputError(f"Threshold given = {dr}, while expected to be in [0,1].")
        return self.weighted_density(central_weight, outer_weight) > dr
