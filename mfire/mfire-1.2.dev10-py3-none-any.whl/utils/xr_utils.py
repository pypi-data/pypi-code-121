"""Ce module regroupe quelques fonctions manipulant des arrays et utiles dans
le projet PROMETHEE."""
import os
from pydantic import BaseModel
import xarray as xr
import numpy as np
import operator
import functools
from typing import Any, Optional, Union, List, Callable
from mfire.utils.date import Datetime
from mfire.settings import get_logger, Settings


class InputError(ValueError):
    """InputError : gere les erreur dûes aux entrees
    """

    pass


xr.set_options(keep_attrs=True)

# Logging
LOGGER = get_logger(name="utils", bind="xr_utils")


def rounding(da: xr.DataArray) -> xr.DataArray:
    """Perform the rounding of latitude/longitude
    Args:
        da (dataArray/dataSet):  Le dataset auquel on peut changer les coordonnées

    Returns:
        dataArray/dataSet: Le dataset avec les coordonnées changées
    """
    for var in ("latitude", "longitude"):
        if hasattr(da, var):
            da[var] = da[var].round(5)
    return da


def identity_da(da: xr.DataArray) -> xr.DataArray:
    """Returns a copy of this dataset.
    A deep copy is made of each of the component variables
    """
    return da.copy(deep=True)


def mask_set_up(mask: xr.DataArray, da: xr.DataArray):
    """
    This function ensure that there is no 'holes' in the mask setting.
    To do so, we compare it to the dataarray.
    It make the hypothesis that both dataarray leave in the same space.
    """
    min_lat = np.max([mask.latitude.values.min(), da.latitude.values.min()])
    max_lat = np.min([mask.latitude.values.max(), da.latitude.values.max()])
    index_lat_field = operator.and_(da.latitude >= min_lat, da.latitude <= max_lat)
    min_lon = np.max([mask.longitude.values.min(), da.longitude.values.min()])
    max_lon = np.min([mask.longitude.values.max(), da.longitude.values.max()])
    index_lon_field = operator.and_(da.longitude >= min_lon, da.longitude <= max_lon)
    dempty = xr.Dataset()
    dempty["longitude"] = da.longitude.isel(longitude=index_lon_field).values
    dempty["latitude"] = da.latitude.isel(latitude=index_lat_field).values
    return mask.broadcast_like(dempty)


class LoaderError(Exception):
    """LoaderError : handles errors due to the opening of the complete
    NetCDF dataset
    """

    pass


def loader_error_decorator(func: Callable) -> Callable:
    """loader error decorator
    Args:
        func (Callable): fonction

    Raises:
        LoaderError

    """

    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> xr.DataArray:
        """function used in a decorator and adds copy functionality
        """
        try:
            return func(self, *args, **kwargs)
        except FileNotFoundError as excpt:
            raise excpt
        except Exception as excpt:
            raise LoaderError(
                f"{self!r}.{func.__name__}(*{args}, **{kwargs}): failed."
            ) from excpt

    return wrapper


class Loader(BaseModel):
    """Class made for properly opening and loading a whole NetCDF dataset

    Raises:
        FileNotFoundError: If given file doesn't exist.
    """

    filename: str

    @loader_error_decorator
    def load(self) -> xr.Dataset:
        """Method for loading a netcdf dataset

        Returns:
            xr.Dataset: Loaded Dataset
        """
        with xr.open_dataset(self.filename) as tmp_ds:
            dataset = tmp_ds.load()
        return rounding(dataset)

    @loader_error_decorator
    def dump(self, data: xr.Dataset) -> bool:
        """Method for dumping a dataset to a NetCDF file

        Args:
            data (xr.Dataset): Dataset to dump
        """
        if os.path.isfile(self.filename):
            LOGGER.warning(
                f"{self.__class__.__name__} : Dumping to existing {self.filename}."
            )
        data.to_netcdf(self.filename)
        return os.path.isfile(self.filename)


class ArrayLoader(Loader):
    """Specific loader for opening NetCDF DataArray.
    """

    @loader_error_decorator
    def load(self, var_name: Optional[str] = None) -> xr.DataArray:
        """Load a DataArray

        Args:
            var_name (Optional[str]): Variable to retrieve from the Dataset.
                If None given, it opens and loads the file as a DataArray,
                which can cause errors if the Dataset has mutiple variables.
                Defaults to None.

        Raises:
            ValueError : if no var_name given and the file contains more than
                one variable.

        Returns:
            xr.DataArray: Loaded Dataarray
        """
        if var_name:
            with xr.open_dataset(self.filename) as tmp_ds:
                dataarray = tmp_ds[var_name].load()
        else:
            with xr.open_dataarray(self.filename) as tmp_da:
                dataarray = tmp_da.load()

        return rounding(dataarray)


class MaskLoader(Loader):
    """Specific loader for opening NetCDF DataArray as masks
    """

    grid_name: Optional[str]

    @loader_error_decorator
    def load(self, ids_list: Union[List[str], str] = None) -> xr.DataArray:
        """Load a xr.DataArray as a mask

        Args:
            ids_list (Union[List[str], str], optional): List of ids to select.
                All ids are selected if None. Defaults to None.

        Returns:
            xr.DataArray: Mask DataArray
        """
        opt_das = {"areaName": None, "areaType": None}
        if self.grid_name:
            with xr.open_dataset(self.filename) as tmp_ds:
                mask_da = tmp_ds[self.grid_name].load()
                for var in opt_das:
                    opt_das[var] = tmp_ds[var].load() if var in tmp_ds else None
        else:
            with xr.open_dataarray(self.filename) as tmp_da:
                mask_da = tmp_da.load()

        # On renomme les dimension pour avoir latitude et longitude (au lieu de
        # latitude_glob05 par exemple)
        dict_dims = {}
        for x in mask_da.dims:
            dict_dims[x] = x.split("_")[0]
        mask_da = mask_da.rename(dict_dims)
        # On selectionne les masques qui nous interessent au sein du lot de
        # masque.
        if ids_list:
            # on selectionne uniquement les ids souhaités
            if isinstance(ids_list, str):
                ids = set([ids_list])
            else:
                ids = set(ids_list)
            ds_ids = set(mask_da.id.values)
            intersection = ids.intersection(ds_ids)
            if intersection != ids:
                LOGGER.warning(
                    f"Toutes les id n'ont pas ete trouves dans la liste {ids} "
                )
            mask_da = mask_da.sel(id=list(intersection))
        else:
            LOGGER.debug("No selection on mask is performed")

        mask_da = rounding(mask_da)

        # la boucle suivante permet de rajouter areaName et areaType
        # en tant que coordonnées et non en tant que variable
        # on retourne donc bien un DataArray
        for var, opt_da in opt_das.items():
            if opt_da is not None and var not in mask_da.coords:
                mask_da = xr.merge([mask_da, opt_da.sel(id=mask_da.id)])
                mask_da = mask_da.swap_dims({"id": var}).swap_dims({var: "id"})[
                    self.grid_name
                ]

        return mask_da


def special_merge(dfirst: xr.Dataset, dsecond: xr.Dataset) -> xr.Dataset:
    """
    Permet de merger des variables "non mergeables".
    Les variables non mergeables doivent être déclarées dans SPECIAL_VAR.
    Pour ces variables, on prendra soit le max, soit le min, soit la moyenne
    (selon le cas).
    Pour l'instant seul le max est implémenté. Implémentation des autres cas à prévoir.
    """

    special_vars = {"summarized_density": "max", "risk_summarized_density": "max"}

    dvars = set(dsecond.data_vars).intersection(set(special_vars))
    dvars1 = set(dfirst.data_vars).intersection(set(special_vars))
    inter = dvars.intersection(dvars1)
    dout = xr.Dataset()

    for var in inter:
        var1 = dfirst[var]
        lev1 = set(var1.risk_level.values)
        var2 = dsecond[var]
        lev2 = set(var2.risk_level.values)
        lev_inter = lev2.intersection(lev1)
        if lev_inter != set():
            if special_vars[var] == "max":
                dout[var] = xr.ufuncs.fmax(var1, var2.broadcast_like(var1))
                dfirst = dfirst.drop_vars(var)
                dsecond = dsecond.drop_vars(var)
            else:
                raise ValueError("Method not implemented")
    return xr.merge([dfirst, dsecond, dout])


def replace_middle(x: np.ndarray, axis: int, **kwargs) -> np.ndarray:
    """Cette fonction remplace la valeur du milieu d'un risque si elle est
    inférieur à ses voisins. On "scan" et on remplace. Ainsi [2,1,2] =>

    [2,2,2]

    [5,1,4] => [5,4,4]
    [5,4,1] = [5,4,1]

    C'est cette fonction qui bouche les trous.
    Par contre, comme vu avec les specificateurs,
    c'est pas grave que les autres valeurs ne soient pas cohérentes ...

    Args:
        x ([ndarray]):
            L'array comprenant les risques à boucher.
            Cette array doit être passée par un rolling (sur 3 time_dimension).
            Ainsi on a une array qui possède une dimension de plus
            (par rapport à l'originale)
        axis ([axis]):
                    Passé directement par reduce (on dirait).
                    Concerne l'axe sur lequel on a "roller".
        kwargs : Obligatoire pour être compatible avec reduce de xarray
    Returns:
        [ndarray]: Une array de la dimension originale (avant rolling).

    """
    if isinstance(axis, tuple) and len(axis) == 1:
        axis = axis[0]
    x_borders = np.min(x.take([0, 2], axis=axis), axis=axis)
    x_middle = x.take(1, axis=axis)
    x_out = np.nanmax([x_borders, x_middle], axis=0)
    return x_out


#
# Fonction permettant le changement de grilles.
#
def from_0_360(ds_grid):
    """Passage d'une grille [0:360] à [-180:180]

    Args:
        ds_grid (dataarray): Le datarray à transformer

    Returns:
        [dataarray]: Le dataarray transformé
    """
    longitude_name = [x for x in ds_grid.dims if "longitude" in x][0]
    new_longitude = np.where(
        ds_grid[longitude_name] < 180,
        ds_grid[longitude_name],
        ds_grid[longitude_name] - 360,
    )
    ds_grid[longitude_name] = new_longitude
    ds_grid = ds_grid.sortby(longitude_name)
    return ds_grid


def from_center_to_0_360(ds_grid):
    """Passage d'une grille [-180:180] à [0:360]

    Args:
        ds_grid (dataarray): Le datarray à transformer

    Returns:
        [dataarray]: Le dataarray transformé
    """
    longitude_name = [x for x in ds_grid.dims if "longitude" in x][0]
    new_longitude = np.where(
        ds_grid[longitude_name] >= 0,
        ds_grid[longitude_name],
        360 + ds_grid[longitude_name],
    )
    ds_grid[longitude_name] = new_longitude
    ds_grid = ds_grid.sortby(longitude_name)
    return ds_grid


def change_grid(da: xr.DataArray, grid_out: str) -> xr.DataArray:
    """change_grid : Fonction qui permet d'effectuer un changement de grille au
    sein de PROMETHEE Ce Changement de grille est fait par interpolation
    bilinéaire. Les résultats sont donc à prendre avec des pincettes si quelque
    chose de précis est nécessaire.

    Le nom de la grille d'entree est pour l'instant non utilisee.
    Servira dans le futur pour gerer les différents cas un peu etrange.

    Args:
        da (xr.Dataarray): Le dataset d'entrée que l'on doit interpoler.
            Ses dimensions comprennent latitude, longitude.

        grid_out (str): Le nom de la grille de sortie.
            Doit être connue dans Settings().altitudes_filename
    """
    # Ouverture du fichier contenant les grilles
    dgrid = xr.open_dataset(Settings().altitudes_filename, cache=False)
    LOGGER.info(f"Grille d'arrivee {grid_out}")
    dgrid_out = dgrid[grid_out].rename(
        {f"latitude_{grid_out}": "latitude", f"longitude_{grid_out}": "longitude"}
    )
    # On change les coordonnées de la grille d'entree pour que ça corresponde
    # à la grille de sortie
    if dgrid_out.longitude.max().values > 180 and da.longitude.min().values < 0:
        da_b = from_center_to_0_360(da)
    elif dgrid_out.longitude.min().values < 0 and da.longitude.max().values > 180:
        da_b = from_0_360(da)
    else:
        da_b = da

    step_lat_new = (dgrid_out.latitude[1] - dgrid_out.latitude[0]).values
    min_lat = da_b.latitude.min().values - abs(step_lat_new)
    max_lat = da_b.latitude.max().values + abs(step_lat_new)
    if step_lat_new < 0:
        slice_lat = slice(max_lat, min_lat)
    else:
        slice_lat = slice(min_lat, max_lat)

    step_lon_new = (dgrid_out.longitude[1] - dgrid_out.longitude[0]).values
    min_lon = da_b.longitude.min().values - abs(step_lon_new)
    max_lon = da_b.longitude.max().values + abs(step_lon_new)
    if step_lon_new < 0:
        slice_lon = slice(max_lon, min_lon)
    else:
        slice_lon = slice(min_lon, max_lon)

    # Cas simple : les grilles sont centrées de la meme maniere.
    dout = da_b.interp_like(dgrid_out.sel(latitude=slice_lat).sel(longitude=slice_lon))
    dgrid.close()
    return dout


# Fonctions gérant les cumuls
def compute_stepsize(
    ds: Union[xr.DataArray, xr.Dataset], var: str = "step"
) -> xr.DataArray:
    """
    compute_stepsize : Cette fonction retourne le pas de temps (en chaque point).
    Ce pas de temps peu varier d'une step à une autre.
    On ne fait donc pas confiance aux méta-données du fichier pour nous renseigner
    la dessus.

    Args:
        ds (dataset ou dataarray): L'array sur laquelle on veut calculer
            le pas de temps
        var (str): la coordonnée servant à calculer la stepsize.
            Cette coordonnée doit être un timedelta64s ou un datetime64
    Exemple :
       da.step = 1,2,5,10

    Returns : A dataset with stepsize as variable and "var" as coordinate.
              Stepsize is express in hour (but as int).
    """

    # On va perdre la dernière occurrence de stepsize via diff
    stepsize = (ds[var].diff(var).dt.seconds / 3600).astype(np.int)
    stepsize.name = "stepsize"
    stepsize.attrs["units"] = "hours"
    # On rajoute la dernière occurrence en remetteant stepsize sur la grille
    # temporelle de la variable d'entree
    # On suppose que la dernière occurrence est identique à l'avant dernière.

    step_comp = (
        stepsize.broadcast_like(ds[var])
        .shift({var: -1})
        .isel({var: 0})
        .expand_dims(var)
    )
    stepout = xr.merge([stepsize, step_comp]).astype(np.int)
    return stepout["stepsize"]


def desagregate_sum_values(
    ds: xr.Dataset, da_step: xr.DataArray, stepout: int = 1, var: str = "step"
) -> xr.Dataset:
    """interpolate_values [summary]

    Args:
        ds (Dataset):  Le dataset pour lequel il faut reinterpoler
        stepvar ([type]): Un dataarray donnant la valeur du stepSize
            à chaque pas de temps de l'array initale.
        stepout (int, optional): La valeur (en heure) du pas de temps en sortie.
               Doit être supérieur ou égal au plus petit pas de temps.

    Hypothèse : On suppose que lorsqu'il y a besoin d'interpoler,
    la valeur est celle qui est après.
    On suppose de plus que la série est triée selon la variable
    d'interpolation (et que celle ci dépend du temps)
    """

    if not isinstance(da_step, xr.DataArray):
        raise InputError(f"da_step should be a dataarray. Get {type(da_step)}")

    ds_fill = (ds / da_step * stepout).resample({var: str(stepout) + "H"}).bfill()
    ds_fill.attrs["stepUnits"] = stepout
    ds_fill.attrs["GRIB_stepUnits"] = stepout
    ds_fill.attrs["history"] = (
        "Desagregation perform. The hypothesis that we need to fill by the forward "
        "value was made. The value has been desagregated by taking the mean."
    )
    return ds_fill


def compute_sum_futur(
    da: xr.DataArray, stepout: int = 6, var: str = "step", da_step: int = None
) -> xr.DataArray:
    """
    compute_sum_futur
    Permet de calculer une somme dans le futur.
    Ainsi à l'instant t, on a l'information sommée entre t et t+stepout.
    On echantillone en fonction du plus petit StepSize.
    Ainsi si une série comprend des stepSize entre 1H et 6H,
    l'espacement entre les steps sera de 1H.
    Args:
        da (xr.DataArray): Dataarray
        stepout (int, optional): Nombre d'heure sur lesquelles on somme.
            Defaults to 6.
        var (str, optional): Variable sur laquelle on somme.
            Defaults to "step".

    Returns:
        xr.DataArray: Nouveau DataArray
    """
    if not isinstance(da, xr.DataArray):
        raise InputError(f"da should be a dataarray. Get {type(da_step)}")

    # On calcul l'ecartement entre les pas de temps successifs.
    # Cet ecartement est propage aussi pour la premiere valeure.
    stepsize = compute_stepsize(da, var=var)
    if da_step is not None:
        # On va regarder si ce qu'on nous donne en entree est coherent avec les
        # espacements ...
        if (stepsize != da_step).any():
            LOGGER.warning(
                "Attention les pas de temps ne correspondent pas aux espacements.\n"
                f"Du coté des pas de temps on a {da_step.values} tandis que les "
                f"espacements entre deux temps successifs sont {stepsize.values} "
            )
            if (stepsize > da_step).any():
                raise InputError(
                    "Au moins un espacement est plus important que la 'stepSize' "
                    "correspondante. Cas pas encore implementé ... "
                    "et sans doute jamais..."
                )
        else:
            LOGGER.info("Les steps et l'ecartement correspondent")
        stepsize = da_step
    else:
        LOGGER.info(
            "Les pas de temps n'ont pas ete fournis. "
            "On se base sur les calculs interne."
        )
    stepmin = stepsize.min().values
    LOGGER.debug(
        "Stepsizes : ", stepmin=stepmin, stepout=stepout, da_step=da_step, var=var
    )

    if stepmin != stepsize.max().values or stepmin > stepout:
        if stepmin > stepout:
            RR = desagregate_sum_values(da, stepsize, stepout=stepout, var=var)
            LOGGER.debug(
                "Comparing max values", rr_max=RR.max().values, da_max=da.max().values
            )
        else:
            # Dans ce cas, on va avoir besoin de desagreger avant de faire la somme
            RR = desagregate_sum_values(da, stepsize, stepout=stepmin, var=var)
    else:
        RR = da.copy()

    # Si on doit cumuler
    if stepout >= stepmin:
        n = int(stepout / stepmin)
    else:
        # On va selectionner seulement par pas de stepmin
        LOGGER.debug(f"'{var}' avant selection", var=var, values=RR[var].values)
        RR = RR.sel({var: da[var]})
        LOGGER.debug(f"'{var}' après selection", var=var, values=RR[var].values)
        LOGGER.debug(
            "Impossible de stepout, entrées espacées de stepmin, on garde stepmin",
            stepout=stepout,
            stepmin=stepmin,
            var=var,
        )
        # Si on desagrege on conserve toutes les valeurs.
        n = 1

    LOGGER.debug("valeurs finales", stepout=stepout, n=n, stepmin=stepmin, var=var)
    # On va maintenant calculer la somme sur les "n" prochaines heures.
    nb_step = RR[var].size
    # Le debut de la serie
    RR6_beg = (
        RR.rolling({var: n}, min_periods=1)
        .sum()
        .shift({var: -(n) + 1})
        .isel({var: range(nb_step - n + 1)})
    )
    # La fin de la serie
    RR6_end = (
        RR.shift({var: -n + 1})
        .rolling({var: n}, min_periods=1)
        .sum()
        .isel({var: range(nb_step - n + 1, nb_step)})
    )
    # On remet le nom correctement. Indispensable pour le merge.
    RR6_beg.name = da.name
    RR6_end.name = da.name
    # On redonne aux attributs la valeur qu'ils avaient en entrant.
    # Attention, c'est certainement abusif et certains attributs devraient
    # certainement être filtré (typ Grib_StepUnits si présent)
    RR6_beg.attrs = RR.attrs
    RR6_end.attrs = RR.attrs
    # On merge
    dout = xr.merge([RR6_beg, RR6_end])[da.name].astype("float32")
    # Maintenant on rempli des infos dans les attributs.
    dout.attrs["accum_hour"] = stepout
    dout.attrs["accum_type"] = "futur"
    if "GRIB_startStep" in dout.attrs:
        dout.attrs["GRIB_endStep"] = dout.attrs["GRIB_startStep"] + stepout
        dout.attrs["GRIB_stepRange"] = "{}-{}".format(
            dout.attrs["GRIB_startStep"], dout.attrs["GRIB_endStep"]
        )
    return dout


def slice_dataarray(
    da: xr.DataArray,
    start: np.datetime64 = None,
    stop: np.datetime64 = None,
    step: np.timedelta64 = None,
    dim: str = "valid_time",
) -> xr.DataArray:
    """slice_dataarray : slice a given dataarray along a given dimension

    Args:
        da (xr.DataArray): DataArray to slice.
        start (np.datetime64, optional): Start of the slice. If None, the minimum value
            along the given dimension is taken. Defaults to None.
        stop (np.datetime64, optional): Stop of the slice. If None, the maximum value
            along the given dimension is taken. Defaults to None.
        step (np.timedelta64, optional): Step of the slice. Defaults to None.
        dim (str, optional): Dimension along which to apply slicing.
            Defaults to "valid_time".

    Returns:
        xr.DataArray: Sliced DataArray.
    """
    vals = da[dim].values
    real_start = start if start is not None else vals.min()
    real_start = Datetime(real_start).as_np_datetime64()
    real_stop = stop if stop is not None else vals.max()
    real_stop = Datetime(real_stop).as_np_datetime64()
    if all(vals[i] > vals[i + 1] for i in range(len(vals) - 1)):
        # Changing start/stop order if dim's values are reversed
        real_start, real_stop = real_stop, real_start
    return da.sel({dim: slice(real_start, real_stop, step)})


def extend_dataarray(
    da: xr.DataArray,
    start: np.datetime64 = None,
    stop: np.datetime64 = None,
    step: int = 1,
    dim: str = "valid_time",
    freq_base: str = "h",
) -> xr.DataArray:
    """extend_dataarray: extend a given dataarray to a new given start and
    a new given stop and gives a new step. Beware, it doesn't fill new steps

    Args:
        da (xr.DataArray):  DataArray to extend.
        start (np.datetime64, optional): New start datetime.
            Defaults to None.
        stop (np.datetime64, optional): New stop datetime.
            Defaults to None.
        step (int, optional): New step. Defaults to 1.
        dim (str, optional): Step's dimension name. Defaults to "valid_time".
        freq_base (str, optional): Frequency base to choose among all pandas's
            frequency strings available here :
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html.
            Defaults to "h".

    Returns:
        xr.DataArray: new dataarray with extend steps.
    """
    delta = np.timedelta64(step, freq_base)
    real_start = (
        Datetime(start).as_np_datetime64()
        if start is not None
        else da[dim].values.min()
    )
    real_stop = (
        Datetime(stop).as_np_datetime64() if stop is not None else da[dim].values.max()
    )
    new_range = np.arange(real_start, real_stop + delta, delta)
    new_range_da = xr.DataArray(
        np.ones(new_range.shape), dims=dim, coords={dim: new_range},
    )
    return da.broadcast_like(new_range_da)


def fill_dataarray(
    da: xr.DataArray,
    source_steps: List[int],
    target_step: int = 1,
    dim: str = "valid_time",
    freq_base: str = "h",
) -> xr.DataArray:
    """fill_dataarray : fill values in a given dataarray along a given 'dim'
    dimension to a 'target_step' and with a filling tolerance of 'source_step'

    Args:
        da (xr.DataArray): DataArray to fill
        source_steps (List[int]): List of source files step lengths. Used for
            limiting the filling of values.
        target_step (int, optional): Target file step length. Defaults to 1.
        dim (str, optional): Step's dimension name. Defaults to "valid_time".
        freq_base (str, optional): Frequency base to choose among all pandas's
            frequency strings available here :
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html.
            Defaults to "h".

    Returns:
        xr.DataArray: new dataarray with filled values.
    """
    if len(source_steps) != len(da[dim]):
        LOGGER.error(
            "Source steps list and given datarray must have the same length",
            source_steps_len=len(source_steps),
            da_len=len(da[dim]),
        )
        return da

    delta = np.timedelta64(1, freq_base)
    new_das = []

    # Extension de chaque step
    for i, local_stop in enumerate(da[dim].values):
        sub_da = da.sel({dim: local_stop})
        source_step = source_steps[i] - 1
        local_start = local_stop - source_step * delta
        new_das.append(
            extend_dataarray(
                da=sub_da,
                start=local_start,
                stop=local_stop,
                step=target_step,
                dim=dim,
                freq_base=freq_base,
            ).bfill(dim=dim)
        )

    # Reconcatenation du nouveau dataarray
    return xr.concat(new_das, dim=dim)
