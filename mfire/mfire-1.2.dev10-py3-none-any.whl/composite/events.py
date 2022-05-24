"""
    Module d'interprétation de la configuration des geos
"""
from enum import Enum
from pydantic import BaseModel, root_validator, validator
from pydantic import Field as PydanticField
from typing import List, Union, Optional, Any, Tuple

import xarray as xr
import copy
import operator

from mfire.settings import get_logger
from mfire.utils.unit_converter import (
    convert_threshold,
    convert_dataarray,
)
from mfire.utils.xr_utils import Loader, ArrayLoader, mask_set_up
from mfire.data.aggregator import Aggregator

from mfire.composite.base import BaseComposite
from mfire.composite.fields import FieldComposite
from mfire.composite.geos import GeoComposite, AltitudeComposite
from mfire.composite.operators import ComparisonOperator
from mfire.composite.aggregations import Aggregation


# Logging
LOGGER = get_logger(name="composite.events.mod", bind="composite.events")


class Category(str, Enum):
    """Création d'une classe d'énumération contenant les categories possibles
    des unités
    """

    BOOLEAN = "boolean"
    QUANTITATIVE = "quantitative"
    CATEGORICAL = "categorical"
    RESTRICTED_QUANTITATIVE = "restrictedQuantitative"


def validate_threshold(value: Any) -> Any:
    """valide la valeur de threshold

    Args:
        value : threshold

    Returns:
        value : threshold
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and int(value) == value:
        return int(value)
    return value


class Threshold(BaseModel):
    """Création d'un objet Threshold contenant la configuration des objects plain
    et mountain de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Threshold
    """

    threshold: Union[float, int, List[Union[float, str]], bool, str]
    # deprecated
    comparison_op: ComparisonOperator
    units: str

    @root_validator(pre=True)
    def check_comparison_op_threshold(cls, values: dict) -> dict:
        if isinstance(values["threshold"], (list, tuple)):
            if values["comparison_op"] == ComparisonOperator.EGAL:
                if len(values["threshold"]) > 1:
                    values["comparison_op"] = ComparisonOperator.ISIN
                else:
                    values["threshold"] = values["threshold"][0]
        return values

    @validator("threshold")
    def validate_threshold(cls, value: Any) -> Any:
        if isinstance(value, list):
            return [validate_threshold(v) for v in value]
        return validate_threshold(value)


class EventComposite(BaseComposite):
    """Création d'un objet Element contenant la configuration des elements_event
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Element
    """

    field: FieldComposite
    category: Category
    plain: Threshold
    mountain: Optional[Threshold]
    mountain_altitude: Optional[int]
    altitude: Optional[AltitudeComposite] = AltitudeComposite()
    process: Optional[str]
    geos: Optional[GeoComposite]
    time_dimension: Optional[str]
    aggregation: Optional[Aggregation]
    aggregation_aval: Optional[Aggregation]
    compute_list: Optional[List[str]] = []
    _values_ds: xr.Dataset = None
    _mask_da: xr.DataArray = None
    _representative_field_da: xr.DataArray = None

    @validator("compute_list")
    def check_compute_list(cls, v: Optional[List[str]] = None) -> List[str]:
        if v is None:
            return []
        return v

    @property
    def values_ds(self) -> xr.DataArray:
        return self._values_ds

    @property
    def _cached_attrs(self) -> dict:
        return {
            "data": ArrayLoader,
            "values_ds": Loader,
        }

    def init_fields(self) -> Tuple[xr.DataArray, xr.DataArray]:
        """Method for initializing self's fields like :
            * field_da: field's DataArray
            * alt_field_da: Altitude field's DataArray
            * _mask_da: Mask DataArray combining geo and altitude restrictions
            * _representative_field_da: Representative values in a DataArray
            * _values_ds: All values computed (representative, min, max, etc.) in
                a single Dataset.

        Returns:
            Tuple[xr.DataArray, xr.DataArray]: field_da and alt_field_da
        """
        # 1. on init le field
        field_da = self.field.compute()
        # ! temporairement on assigne le grid_name comme ça
        self.altitude.grid_name = self.field.grid_name
        if isinstance(self.geos, GeoComposite):  # ! temporairement #GeoGate
            self.geos.grid_name = self.field.grid_name
            # 2. creation du masque
            #   A. on init notre masque de geos
            geos_mask_da = mask_set_up(self.geos.compute(), field_da)
        elif isinstance(self.geos, xr.DataArray):  # ! temporairement #GeoGate
            geos_mask_da = mask_set_up(self.geos, field_da)

        #   B. on masque notre field avec l'altitude
        #       a. on recupère le champs d'altitude
        alt_field_da = self.altitude.compute()
        alt_mask_da = alt_field_da >= self.altitude.alt_min
        #       b. on le transforme en masque
        alt_mask_da = mask_set_up(alt_mask_da.where(alt_mask_da), field_da)
        #   C. finalement notre masque en combinant geo et masque
        self._mask_da = geos_mask_da * alt_mask_da

        # ! temporairement on init self._representative_field_da
        self._representative_field_da = field_da * self._mask_da
        self._representative_field_da.name = field_da.name
        # ! temporairement on init le self._values_ds ici
        self._values_ds = xr.Dataset()
        return field_da, alt_field_da

    def _compute(self) -> xr.DataArray:
        # on init les fiels
        field_da, alt_field_da = self.init_fields()
        # on compute sur plain and mountain
        risk_da = self.compute_plain_and_mountain(
            field_da=field_da, alt_field_da=alt_field_da
        )
        # on aggrege si besoin
        return self.compute_downstream_aggregation(
            field_name=self.field.name, risk_da=risk_da
        )

    def get_comparison(self) -> dict:
        """
        Enable to get comparison operator for an event

        Returns:
            dict: Dictionnary of comparison operator (on plain or mountain)
        """
        dict_out = {}
        if self.plain is not None:
            dict_out["plain"] = dict(self.plain)
        if self.mountain is not None:
            dict_out["mountain"] = dict(self.mountain)
        dict_out["category"] = self.category

        # On recupere la fonction d'aggregation. Permettra les controles plus tard.
        if self.aggregation is not None:
            agg = self.aggregation
        else:
            agg = self.aggregation_aval
        dict_out["aggregation"] = dict(agg)
        return dict_out

    def get_cover_period(self) -> xr.DataArray:
        """Return the period cover by the event.
        To do so, we will need to open the DataArray

        Returns:
            xr.DataArray: Period covering the Event.
        """
        return copy.deepcopy(self.field.get_coord(self.time_dimension))

    def update_selection(
        self,
        sel: dict = dict(),
        slice: dict = dict(),
        isel: dict = dict(),
        islice: dict = dict(),
    ):
        self.field.selection.update(sel=sel, slice=slice, isel=isel, islice=islice)
        if hasattr(self, "field_1"):
            self.field_1.selection.update(
                sel=sel, slice=slice, isel=isel, islice=islice
            )

    def changing_threshold(
        self, threshold: Threshold, field_da: xr.DataArray
    ) -> Threshold:
        """This function change the threshold to match units of the field

        Args:
            threshold (Threshold): Objet contenant le threshold et
                les unités du threshold

        Returns:
            Threshold : Le threshold modifié.

        TODO : rajouter une information (sup ou inf) pour les variables quantitatives
        discretes (type Beaufort)
        """
        new_threshold = copy.deepcopy(threshold)
        if new_threshold.units is not None:
            if new_threshold.units != 1:
                new_threshold.threshold = convert_threshold(
                    field_da, new_threshold.threshold, new_threshold.units
                )
        return new_threshold

    def get_risk(
        self,
        comp_op: ComparisonOperator,
        field_da: xr.DataArray,
        threshold: Any,
        mask_da: xr.DataArray,
    ) -> xr.DataArray:
        """" Function created to be able for other children class to implement
        the risk another way

        Args:
            comp_op ([type]): Function which describe the comparison to perform
            field ([data_array]):  The field
            threshold ([float]): The threshold applied

        Returns:
            [data_array]: The risk. It returns a boolean for every pixel.
        Be carreful : there is no nan inside.  nan with a logical produce a False.
        So you may need to restrict this results to area where the mask is valid.

        """

        return comp_op(field_da, threshold)

    def compute_density(self, risk_field_da: xr.DataArray) -> xr.DataArray:
        """Calcul la densité d'un evenement.
        Ceci dans le but de renvoyer la densité quelque soit le cas
        (qu'on passe par une aggréagation par la moyenne/par la drr ...)

        Args:
            risk_field_da (xr.DataArray): Champ du risque

        Returns:
            xr.DataArray: Densité du risque
        """
        agg_handler = Aggregator(risk_field_da)
        density = agg_handler.compute("density")
        return density

    def compute_summarized_density(
        self, risk_field_da: xr.DataArray, mask_da: xr.DataArray
    ) -> xr.DataArray:
        """Permet de calculer la densité résumée dans le temps

        Args:
            risk_field_da (xr.DataArray): Champ du risque
            mask_da (xr.DataArray): mask

        Returns:
            xr.DataArray: Densité résumée dans le temps
        """
        agg_handler_time = Aggregator(risk_field_da, aggregate_dim=self.time_dimension)
        max_risk = agg_handler_time.compute("max") * mask_da

        agg_handler_space = Aggregator(max_risk)
        density = agg_handler_space.compute("density")
        return density

    def get_extremevalues(
        self, masked_field_da: xr.DataArray, original_unit: str
    ) -> Tuple[xr.DataArray, xr.DataArray]:
        """
        get_extremevalues : Retourne les valeurs extremes

        Arguments:
            masked_field {data_array} -- Le data_array pour lequel on recherche
                le min et le max

        Returns:
            [(data_array,data_array)] -- Les deux data_array representant les extremes
        """
        if self.category in (Category.QUANTITATIVE, Category.RESTRICTED_QUANTITATIVE):
            agg_handler = Aggregator(masked_field_da)
            mini_da = convert_dataarray(agg_handler.compute("min"), original_unit)
            maxi_da = convert_dataarray(agg_handler.compute("max"), original_unit)
            return (mini_da, maxi_da)
        else:
            return (None, None)

    def get_representative_values(
        self,
        masked_field: xr.DataArray,
        comparison_op: ComparisonOperator = None,
        original_unit: str = None,
    ) -> xr.DataArray:
        """
        Permet de retourner la valeur representative du champ.
        Gere le cas d'aggrégation par la moyenne et par les drr
        (si l'operateur de comparaison est dans [<,<=,>,>=]).

        Args:
            masked_field ([type]): [description]
            comparison_op : L'opérateur de comparaison (si besoin dans les drr)
            original_unit : L'unité dans laquelle on doit reconvertir les sorties
        Return:
            data_array : La valeur representative. Return None si la variable est
                qualitative/booleénne ou qu'une erreur s'est produite
        Log :
            erreur : Si l'operateur de comparaison n'est pas dans
                [<,<=,>,>=, inf, infegal, sup ,supegal] et la methode d'aggregation
                est drr.

        """
        rep_value = None
        if self.category in (Category.QUANTITATIVE, Category.RESTRICTED_QUANTITATIVE):
            agg_handler = Aggregator(masked_field)
            # On va mainteant recuperer la methode d'aggregation.
            # Soit on la connait deja, soit elle est dans la cle
            # aggregation_aval.
            if self.aggregation is None:
                aggregation_aval = self.aggregation_aval
                if aggregation_aval is not None:
                    LOGGER.debug(
                        "On a une info sur la methode bien qu'on soit "
                        f"en aval {aggregation_aval}",
                        func="get_representative_values",
                    )
                    # Cette methode d'agregation va devoir etre changee si on
                    # est dans le cas d'une methode qui fait intervenir les
                    # zones centrales.
                    aggregation = aggregation_aval
                else:
                    aggregation = Aggregation(method="mean")

                    LOGGER.warning(
                        "No aggregation method supply for rep value. Taking mean.",
                        func="get_representative_values",
                    )
            else:
                aggregation = self.aggregation
            LOGGER.debug(
                "Aggregation method",
                aggregation=aggregation,
                place="event",
                func="get_representative_values",
            )

            if not aggregation.method.is_after_threshold:
                aggregation_kwargs = dict(aggregation.kwargs or {})
                rep_value = agg_handler.compute(
                    aggregation.method, **aggregation_kwargs
                )
            elif aggregation.method.startswith("requiredDensity"):
                thresh = aggregation.kwargs.dr
                my_operator = comparison_op
                try:
                    if my_operator in (
                        ComparisonOperator.SUP,
                        ComparisonOperator.SUPEGAL,
                    ):
                        quantile = 1 - thresh
                        rep_value = agg_handler.compute(
                            "quantile", q=quantile
                        ).drop_vars("quantile")
                    elif my_operator in (
                        ComparisonOperator.INF,
                        ComparisonOperator.INFEGAL,
                    ):
                        quantile = thresh
                        rep_value = agg_handler.compute(
                            "quantile", q=quantile
                        ).drop_vars("quantile")
                    else:
                        LOGGER.error(
                            f"get_representative_value:cas non connu {my_operator}",
                            func="get_representative_values",
                        )
                        return None
                except Exception as excpt:
                    LOGGER.error(
                        f"Echec de l'aggregation sur le field : {masked_field}",
                        operateur=my_operator,
                        quantile=quantile,
                        field=masked_field,
                        func="get_representative_values",
                    )
                    raise ValueError from excpt
            else:
                LOGGER.error(
                    f"Aggregation method {aggregation.method} unknown",
                    func="get_representative_values",
                )
                raise ValueError("Case need to be included")
            if original_unit is not None:
                rep_value = convert_dataarray(rep_value, original_unit)
        return rep_value

    def compute_plain_and_mountain(
        self, field_da: xr.DataArray, alt_field_da: xr.DataArray
    ) -> xr.DataArray:
        """Calcul le risk et les differentes valeurs representatives/extreme que
        l'on soit en plaine ou en plaine + montagne.

        Args:
            field_da (xr.DataArray): Champ du risque
            alt_field_da (xr.DataArray): Champ d'altitude

        Returns:
            xr.DataArray: Risque sur plaine et montagne
        """
        mountain = self.mountain

        if mountain is not None:
            mountain = self.changing_threshold(threshold=mountain, field_da=field_da)
            altitude_masked = alt_field_da * self._mask_da
            plain_mask = (altitude_masked <= self.mountain_altitude) * self._mask_da
            plain_mask = plain_mask.where(plain_mask > 0)
            mountain_mask = (altitude_masked > self.mountain_altitude) * self._mask_da
            mountain_mask = mountain_mask.where(mountain_mask > 0)
        else:
            plain_mask = self._mask_da
        # On va maintenant changer les thresholds
        plain = self.changing_threshold(threshold=self.plain, field_da=field_da)
        # On charge le field (comme ça on le fera qu'une seule fois)
        # Calcul du champ de risque
        plain_field = field_da * plain_mask
        plain_risk = self.get_risk(
            plain.comparison_op, plain_field, plain.threshold, mask_da=plain_mask,
        )

        risk_field = plain_risk
        if mountain is not None:
            mountain_field = field_da * mountain_mask
            mountain_risk = self.get_risk(
                mountain.comparison_op,
                mountain_field,
                mountain.threshold,
                mask_da=mountain_mask,
            )
            risk_field = plain_risk + mountain_risk

        # ===================
        # Calculs des valeurs non obligatoires #
        # ====================
        # Calcul de la densité

        if "density" in self.compute_list:
            density = self.compute_density(risk_field * self._mask_da)
            # On rajoute la densité dans le dataset
            self._values_ds["density"] = density

        # Calcul de la densité résumée
        if "summary" in self.compute_list:
            density = self.compute_summarized_density(
                risk_field * self._mask_da, self._mask_da
            )
            self._values_ds["summarized_density"] = density
        # Calcul des extremes
        original_unit = self.plain.units

        if "extrema" in self.compute_list:
            field = self._representative_field_da * plain_mask
            field.name = self._representative_field_da.name
            (mini, maxi) = self.get_extremevalues(field, original_unit)
            if mini is not None:
                self._values_ds["min_plain"] = mini
                self._values_ds["max_plain"] = maxi
            if mountain is not None:
                field = self._representative_field_da * mountain_mask
                field.name = self._representative_field_da.name
                (mini, maxi) = self.get_extremevalues(field, original_unit)
                if mini is not None:
                    self._values_ds["min_mountain"] = mini
                    self._values_ds["max_mountain"] = maxi
        # Calcul des valeurs representatives.
        if "representative" in self.compute_list:
            field = self._representative_field_da * plain_mask
            field.name = self._representative_field_da.name
            rep_value = self.get_representative_values(
                field, comparison_op=plain.comparison_op, original_unit=original_unit,
            )
            if rep_value is not None:
                self._values_ds["rep_value_plain"] = rep_value
            if mountain is not None:
                field = self._representative_field_da * mountain_mask
                field.name = self._representative_field_da.name
                rep_value = self.get_representative_values(
                    field,
                    comparison_op=plain.comparison_op,
                    original_unit=original_unit,
                )
                if rep_value is not None:
                    self._values_ds["rep_value_mountain"] = rep_value

        # =========================
        # Maintenant on passe au calcul du risk en lui-meme
        # Ce calcul est obligatoire
        # =========================
        aggregation = self.aggregation

        if aggregation is not None and not aggregation.method.is_after_threshold:
            # Cas ou le risque est calcule a partir de valeur aggregee (moyenne)
            aggregation_kwargs = dict(aggregation.kwargs or {})
            aggregation_algo = aggregation.method
            # Aggregation sur la plaine
            agg_plain = Aggregator(plain_field)
            plain_field_t = agg_plain.compute(aggregation_algo, **aggregation_kwargs)
            # On definit le risque sur la plaine
            risk = self.get_risk(
                plain.comparison_op, plain_field_t, plain.threshold, mask_da=plain_mask,
            )
            # Si on a une condition sur l'altitude
            if mountain is not None:
                agg_mountain = Aggregator(mountain_field)
                mountain_field_t = agg_mountain.compute(
                    aggregation_algo, **aggregation_kwargs
                )
                mountain_risk = self.get_risk(
                    mountain.comparison_op,
                    mountain_field_t,
                    mountain.threshold,
                    mask_da=mountain_mask,
                )
                risk = risk + mountain_risk
        else:
            # Cas où le risque est calcule a partir de valeur non aggregee (drr)
            # Si on aggrege au niveau de l'evenement (i-e chaque evenement de
            # maniere independante)
            if self.aggregation is not None:
                risk = risk_field * self._mask_da
            else:
                # Si on aggrege au niveau du risque
                risk = risk_field
        return risk

    def compute_downstream_aggregation(
        self, field_name: str, risk_da: xr.DataArray
    ) -> xr.DataArray:
        """
        Permet de calculer le risque.
        Si aggrégation il y a, elle peut être faite avant (moyenne/quantile/...)
        ou après la comparaison à l'opérateur (ddr/density)
        Cette fonction peut prendre en compte les conditions d'altitude
        (si elles ont été bien renseignées auparavant)

        Returns:
            dataarray : Le dataarray de risque pour cet évènement "unitaire".
        """
        new_risk_da = risk_da
        if self.aggregation is not None and self.aggregation.method.is_after_threshold:

            agg_handler = Aggregator(new_risk_da)
            aggregation_kwargs = dict(self.aggregation.kwargs or {})
            new_risk_da = agg_handler.compute(
                self.aggregation.method, **dict(aggregation_kwargs)
            )

        if self.aggregation is not None:
            # Si on est dans le cas de l'aggregation AMONT on sait si le risque est
            # activee ou non
            self._values_ds["occurrence_event"] = new_risk_da
        LOGGER.debug(
            f"FieldName is {field_name}.", param=field_name, func="compute_event",
        )
        self._values_ds["weatherVarName"] = ("tmp", [field_name])
        if hasattr(self._values_ds, "min_plain"):
            self._values_ds["units"] = ("tmp", [self._values_ds.min_plain.units])
        return new_risk_da


class EventBertrandComposite(EventComposite):
    """Création d'un objet Element contenant la configuration des Elementsevent
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Element
    """

    process: str = PydanticField("Bertrand", const=True)
    field_1: FieldComposite
    cum_period: int

    def init_fields(self):
        field_da, alt_field_da = super().init_fields()
        rr1_da = self.field_1.compute() * self._mask_da

        if field_da.GRIB_stepUnits != rr1_da.GRIB_stepUnits:
            raise ValueError(
                "Both cumul field not have the same stepUnits. "
                f"Simple field is {field_da.GRIB_stepUnits} and "
                f"cumulField is {rr1_da.GRIB_stepUnits}."
            )

        # On divise le temps sur lequel on prend des cumuls par la taille de la step
        # On obtient ainsi un risque qui est correctement défini.
        n = int(self.cum_period / rr1_da.GRIB_stepUnits)
        max_p = field_da[self.time_dimension].size
        if n < max_p:
            max_p = n
        self._representative_field_da = field_da.rolling(
            {self.time_dimension: max_p}, min_periods=1
        ).max()
        self._representative_field_da.attrs.update(field_da.attrs)
        self._representative_field_da.name = field_da.name
        return field_da, alt_field_da

    def get_risk(
        self,
        comp_op: ComparisonOperator,
        field_da: xr.DataArray,
        threshold: Any,
        mask_da: xr.DataArray,
    ) -> xr.DataArray:
        """Specify the risk for cumulative event such Rainfall

        Args:
            comp_op ([type]): L'opérateur de comparaison
            field ([type]): Le champ (RRn dans le futur)
            threshold ([type]): Le threshold pour l'evenement de type "betrand"
            mask (dataArray) : Le masque utilisé
        """
        # On masque en utilisant le masque fournit par le champ.

        LOGGER.debug("Entering get_risk for Bertrand", func="get_risk")

        rr1_da = self.field_1.compute() * mask_da
        aggregation = self.aggregation

        if field_da.GRIB_stepUnits != rr1_da.GRIB_stepUnits:
            raise ValueError(
                "Both cumul field not have the same stepUnits. "
                f"Simple field is {field_da.GRIB_stepUnits} and "
                f"cumulField is {rr1_da.GRIB_stepUnits}."
            )

        if aggregation is not None and not aggregation.method.is_after_threshold:
            agg_handler = Aggregator(rr1_da)
            # Cas ou le risque est calcule a partir de valeur aggregee (moyenne)
            aggregation_kwargs = dict(aggregation.kwargs or {})
            aggregation_algo = aggregation.method
            rr1_da = agg_handler.compute(aggregation_algo, **aggregation_kwargs)

        # On va remplacer n par la taille maxi du dataset. Sinon on ne peut
        # pas prendre de max
        # On divise le temps sur lequel on prend des cumuls par la taille de la step
        # On obtient ainsi un risque qui est correctement défini.
        n = int(self.cum_period / rr1_da.GRIB_stepUnits)
        max_p = field_da[self.time_dimension].size
        if n < max_p:
            max_p = n
        else:
            LOGGER.debug(f"Going from {n} to {max_p} for rolling operation")

        cum_max = field_da.rolling({self.time_dimension: max_p}, min_periods=1).max()
        start = operator.and_(
            comp_op(cum_max, threshold), comp_op(rr1_da, threshold / n)
        )
        keep = operator.and_(
            comp_op(cum_max, threshold), comp_op(field_da, threshold / n)
        )
        risk = start.copy()
        for step in range(len(risk[self.time_dimension].values)):
            current_risk = risk.isel({self.time_dimension: step})
            if step > 0:
                previous_risk = risk.isel({self.time_dimension: step - 1})
                current_risk = operator.or_(
                    previous_risk * keep.isel({self.time_dimension: step}),
                    start.isel({self.time_dimension: step}),
                )
                risk.isel({self.time_dimension: step})[:] = current_risk[:].compute()
        risk.attrs.update(rr1_da.attrs)
        # On va remettre des atrributs au risque
        LOGGER.debug("Getting out get_risk for Bertrand", func="get_risk")
        return risk
