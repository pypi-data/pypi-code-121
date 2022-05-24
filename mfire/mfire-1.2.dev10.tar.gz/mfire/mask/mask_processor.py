"""
This module should do mask preprocessing and transform geojson to netcdf.

History :
    (Vincent Chabot ) : Forcing small polygon to be represented as point or line.
    (Vincent Chabot) February 2021 :
        Adding splitting by
            - compass direction
            - altitude
"""
import os
import xarray as xr
import shapely.geometry as geom
from geojson import Feature
import numpy as np
from PIL import Image, ImageDraw
import mfire.utils.hash as hashmod
from mfire.mask.north_south_mask import get_Bertrand_proposal
from mfire.mask.altitude_mask import generate_mask_by_altitude
from mfire.mask.fusion import (
    extract_areaName,
    perform_poly_fusion,
)
from mfire.localisation.area_algebre import compute_IoU
from mfire.settings import get_logger, Settings

# Logging
LOGGER = get_logger(name="mask_processor", bind="mask")


xr.set_options(keep_attrs=True)


def lon_lat_to_img(point, g):
    """
    Transform to apply to an img to get coordinates
    :param point: lon/lat of point
    :param g: geometry grid as dict
    """

    lon, lat = point[0], point[1]
    # x / lon transform
    a_x = (g["nb_c"] - 1) / (g["last_lon"] - g["first_lon"])
    b_x = -g["first_lon"] * a_x
    x = a_x * lon + b_x
    # y  / Lat transform
    a_y = (g["nb_l"] - 1) / (g["last_lat"] - g["first_lat"])
    b_y = -g["first_lat"] * a_y
    y = a_y * lat + b_y
    return (x, y)


def lon_lat_shape_to_img(poly, g):
    """lon_lat_shape_to_img

    Args:
        poly (A polygon (shapely)): The polygon for which we need to find
            the exterior bound.
        g (dict): A dictionnary describing the grid.

    Returns:
        [list]: The list of exterior point of the polygon.
    """
    return [
        lon_lat_to_img(point, g)
        for point in poly.exterior.__geo_interface__["coordinates"]
    ]


def lon_lat_point_to_img(point, g):
    """
    Args:
        point (A Point (shapely))
        g (dict): A dictionnary describing the grid.
    """
    return [lon_lat_to_img(point.__geo_interface__["coordinates"], g)]


def lon_lat_linestring_to_img(line, g):
    """lon_lat_linestring_to_img

    Args:
        line (A line (shapely)): The Line for which we need to find the exterior bound.
        g (dict): A dictionnary describing the grid.

    Returns:
        [list]: The list of point of the line.
    """
    return [lon_lat_to_img(point, g) for point in line.__geo_interface__["coordinates"]]


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


def is_point(img_shape):
    """
    Permet de savoir si un polygon est en fait un point
    Args:
        img_shape ([type]): [description]

    Returns:
        [type]: [description]
    """
    mini = np.asarray(img_shape).min(axis=0)
    maxi = np.asarray(img_shape).max(axis=0)
    return np.max(maxi - mini) < 1


def is_line(img_shape) -> bool:
    """ Enable to know if a polygon is in fact a line (for a specific grid)

    Args:
        img_shape ([type]): [description]

    Returns:
        [bool]: True if it is a line, False otherwise
    """
    mini = np.asarray(img_shape).min(axis=0)
    maxi = np.asarray(img_shape).max(axis=0)
    return np.min(maxi - mini) < 1


def create_mask_PIL(poly, g, ds_grid):
    """ Create mask using PIL library.
        Passage du format vectoriel au format grille.
    Args:
       poly : La shape que l'on souhaite transformer
       g (dict) : Un dictionnaire contenant pas mal d'info sur la grille
       ds_grid(dataarray) : La grille sur laquelle on met les données

    """
    img = Image.new("1", (int(g["nb_c"]), int(g["nb_l"])))
    if poly.geometryType() == "Polygon":
        img_shape = lon_lat_shape_to_img(poly, g=g)
        if is_point(img_shape):
            point_shape = np.floor(np.asarray(img_shape).min(axis=0))
            ImageDraw.Draw(img).point(tuple(point_shape), fill=1)
        elif is_line(img_shape):
            mini = np.asarray(img_shape).min(axis=0)
            maxi = np.asarray(img_shape).max(axis=0)
            ImageDraw.Draw(img).line([tuple(mini), tuple(maxi)], fill=1)
        else:
            ImageDraw.Draw(img).polygon(img_shape, fill=1, outline=1)
            img_holes = []
            for holes in poly.holes:
                # --------------------------------------------------
                # The rounding is here in order to get a better hole.
                # However, for large grid, some problem can occured.
                # ---------------------------------------------------
                img_holes = [
                    tuple(np.round(lon_lat_to_img(point, g)).tolist())
                    for point in holes
                ]
                ImageDraw.Draw(img).polygon(img_holes, fill=-1, outline=0)

    elif poly.geometryType() == "MultiPolygon":
        for small in poly:
            img_shape = lon_lat_shape_to_img(small, g=g)
            if is_point(img_shape):
                point_shape = np.floor(np.asarray(img_shape).min(axis=0))
                ImageDraw.Draw(img).point(tuple(point_shape), fill=1)
            elif is_line(img_shape):
                mini = np.asarray(img_shape).min(axis=0)
                maxi = np.asarray(img_shape).max(axis=0)
                ImageDraw.Draw(img).line([tuple(mini), tuple(maxi)], fill=1)
            else:
                ImageDraw.Draw(img).polygon(img_shape, fill=1, outline=1)
                for holes in geom.asShape(small).holes:
                    img_holes = [
                        tuple(np.round(lon_lat_to_img(point, g)).tolist())
                        for point in holes
                    ]
                    ImageDraw.Draw(img).polygon(img_holes, fill=-1, outline=0)
    elif poly.geometryType() == "Point":
        img_shape = lon_lat_point_to_img(poly, g=g)
        ImageDraw.Draw(img).point(img_shape, fill=1)
    elif poly.geometryType() == "MultiPoint":
        for point in poly:
            img_shape = lon_lat_point_to_img(point, g=g)
            ImageDraw.Draw(img).point(img_shape, fill=1)
    elif poly.geometryType() == "LineString":
        img_shape = lon_lat_linestring_to_img(poly, g=g)
        ImageDraw.Draw(img).line(img_shape, fill=1)
    elif poly.geometryType() == "MultiLineString":
        for line in poly:
            img_shape = lon_lat_linestring_to_img(line, g=g)
            ImageDraw.Draw(img).line(img_shape, fill=1)
    else:
        raise ValueError(
            f"Type of geometry {poly.geometryType()} not taken into account."
        )

    ds = xr.Dataset()
    for x in list(ds_grid.dims):
        ds.coords[x] = ds_grid[x].values
    ds[ds_grid.name] = (ds_grid.dims, np.array(img))
    return (
        ds.where(ds[ds_grid.name] > 0)
        .dropna(dim=ds_grid.dims[0], how="all")
        .dropna(dim=ds_grid.dims[1], how="all")
    )


def get_g(ds_grid):
    """get_g Function which return information about grid.

    Args:
        ds_grid (xr.Dataset): We will use only the lat/lon grid
            The grid should have latitude and longitude dimension
            (possibly with _myname added)

    Returns:
        [dict]: A dictionnary with the following keys :
           - first_lat(lon) : First latitude(longitude) of the grid
           - last_lat(lon) : Last latitude(longitude) of the grid
           - step_lat(lon) : Step size for latitude(longitude)
           - nb_l : Number of latitude
           - nb_c : Number of longitude
    """
    g = {}
    dict_dims = {}
    for x in ds_grid.dims:
        dict_dims[x] = x.split("_")[0]
    ds_grid = ds_grid.rename(dict_dims)
    g["first_lat"] = ds_grid.latitude[0].values.round(4)
    g["last_lat"] = ds_grid.latitude[-1].values.round(4)
    g["step_lat"] = (g["last_lat"] - g["first_lat"]) / (ds_grid.latitude.size - 1)
    g["nb_l"] = ds_grid.latitude.size
    g["first_lon"] = ds_grid.longitude[0].values.round(4)
    g["last_lon"] = ds_grid.longitude[-1].values.round(4)
    g["step_lon"] = (g["last_lon"] - g["first_lon"]) / (ds_grid.longitude.size - 1)
    g["nb_c"] = ds_grid.longitude.size
    return g


class MaskProcessor:
    """
    Permet de creer les masques pour un msb
    """

    _warning = (
        False  # Permet de savoir si on a deja averti au moins une fois pour ce bug.
    )

    def __init__(self, config_dict: dict, **kwargs):
        """
        Args:
            config_dict (dict): Dictionnaire de configuration de la production
                contenant au moins la clé 'geos'.
        Kwargs :
            output_dir : utilisé si pas de file dans le dictionnaire
        """
        self.data = config_dict
        self.change_geometry()
        self.grid_ds = xr.open_dataset(Settings().altitudes_filename)
        self.grid_list = self.grid_ds.data_vars
        self.kwargs = kwargs

    def change_geometry(self):
        for i, area in enumerate(self.data["geos"]["features"]):
            if geom.asShape(area["geometry"]).geometryType() in [
                "Polygon",
                "MultiPolygon",
                "LineString",
                "MultiLineString",
            ]:
                x = geom.asShape(area["geometry"]).buffer(1e-5)  # .buffer(-1e-5)
                self.data["geos"]["features"][i]["geometry"] = Feature(geometry=x)[
                    "geometry"
                ]

    @staticmethod
    def get_mask(ds_grid, grid, poly):
        """get_mask

        Args:
            ds_grid (xr.dataset): The grid.
            grid (str): The variable name.
            poly (shapely.geometry.shape): The shape to transform in netcdf.

        Returns:
            xr.Dataset: The mask dataset.
        """
        ds_grid = ds_grid[grid]
        longitude_name = [x for x in ds_grid.dims if "longitude" in x][0]
        change_longitude = False
        if ds_grid[longitude_name].max() > 180:
            change_longitude = True
            ds_grid = from_0_360(ds_grid)
        g = get_g(ds_grid)
        dout = create_mask_PIL(poly, g=g, ds_grid=ds_grid)
        if change_longitude:
            dout = from_center_to_0_360(dout)
        return dout

    @staticmethod
    def get_axe(feature):
        return feature["properties"].get("is_axe", False)

    @staticmethod
    def merge_area(ds: xr.Dataset, merged_list: list, grid: str) -> xr.Dataset:
        """ Permet de merger les zones.

        Args:
            ds (xr.Dataset): Le dataset de masques déjà créér
            merged_list (list): La liste des zones à créer
            grid (str): La grille d'intérêt

        Returns:
            xr.Dataset: Les zones fusionnées.
        """
        dgrid = ds[grid]
        list_area = []
        for new_zone in merged_list:
            dtemp = dgrid.sel(id=new_zone["base"]).max("id")
            IoU = compute_IoU(
                dtemp.rename(
                    {
                        "latitude_%s" % grid: "latitude",
                        "longitude_%s" % grid: "longitude",
                    }
                ),
                dgrid.rename(
                    {
                        "latitude_%s" % grid: "latitude",
                        "longitude_%s" % grid: "longitude",
                    }
                ),
            )
            if IoU.max("id") < 0.97:
                dtemp = dtemp.expand_dims(dim="id").assign_coords(id=[new_zone["id"]])
                dtemp["areaName"] = (("id"), [new_zone["name"]])
                dtemp["areaType"] = (("id"), [new_zone["areaType"]])
                list_area.append(dtemp)
            else:
                LOGGER.debug(
                    f"On ne cree pas {new_zone['name']} pour cette grille {grid}"
                )

        if len(list_area) > 0:
            dout = xr.merge(list_area)
            res = dout.reset_coords(["areaName", "areaType"])
        else:
            res = None
        return res

    def create_masks(self):
        """
        create_masks
        This function create all the mask from a geojson dictionnary.
        The creation is performed only if the output file is not present.
        """
        dmask = xr.Dataset()
        if "mask_hash" in self.data:
            current_hash = self.data.get("mask_hash")
        else:
            handler = hashmod.MD5(self.data["geos"])
            current_hash = handler.hash
        # Pour chaque msb on va creer un nouveau fichier
        if "file" in self.data:
            fout = self.data["file"]
        elif "uid" in self.data:
            fout = self.kwargs.get("output_dir", "./") + self.data["uid"] + ".nc"
        else:
            raise ValueError(
                "You should have in the file something to name the output."
            )
        output_dir = os.path.dirname(fout)
        os.makedirs(output_dir, exist_ok=True)
        # On tri les zones pour mettre les axes en dernier
        self.data["geos"]["features"].sort(key=self.get_axe)

        merged_list = []
        for area in self.data["geos"]["features"]:
            # On recupere les infos qui nous interessent
            area_id = area["id"]
            # On récupere l'info pour savoir si c'est un axe
            is_axe = area["properties"].get("is_axe", False)
            # Introduire ici le truc sur le hash
            poly = geom.asShape(area["geometry"])

            if is_axe and poly.geometryType() in ["Polygon", "MultiPolygon"]:
                merged_list.extend(
                    perform_poly_fusion(poly, self.data["geos"], area_id)
                )

            for grid in self.grid_list:
                l_temp = []
                dtemp = self.get_mask_on_grid(grid, poly, area_id, area["properties"])
                l_temp.append(dtemp)
                if is_axe and poly.geometryType() in ["Polygon", "MultiPolygon"]:
                    LOGGER.debug(
                        "Creating altitude and geographical mask",
                        area_id=area_id,
                        grid=grid,
                        func="create_masks",
                    )
                    ds_mask_compass = self.get_compass_area(grid, poly, area_id)
                    if ds_mask_compass and ds_mask_compass.id.size > 1:
                        l_temp.append(ds_mask_compass)
                    ds_mask_alti = generate_mask_by_altitude(
                        dtemp[grid], self.grid_ds[grid], area_id + "_alt_"
                    )
                    if ds_mask_alti is not None:
                        l_temp.append(ds_mask_alti)
                try:
                    dpartial = xr.merge(l_temp)
                    dmask = xr.merge([dmask, dpartial])
                except Exception as excpt:
                    LOGGER.warning(f"Le merge partiel {l_temp}")
                    LOGGER.warning(
                        "Failed to merge masks.",
                        dmask=dmask,
                        dtemp=dtemp,
                        area_id=area_id,
                        grid=grid,
                        func="create_masks",
                    )
                    raise excpt
        # On va ajouter les régions fusionnées ensuite.
        l_temp = []
        for grid in self.grid_list:
            dmerged = self.merge_area(dmask, merged_list, grid)
            if dmerged is not None:
                l_temp.append(dmerged)
        if l_temp != []:
            dpartial = xr.merge(l_temp)
            dmask = xr.merge([dmask, dpartial])
        dmask.attrs["md5sum"] = current_hash
        dmask.to_netcdf(fout)

    def get_compass_area(self, grid, poly, area_id):
        """ Effectue la découpe selon les points cardinaux

        Args:
            grid (dataArray): La grille sur laquelle on veut projeter le JSON
            poly (shape): Le shape de la zone a découper
            area_id (str): L'identifiant original de la zone

        Returns:
            Dataset : Un dataset de la découpe
        """
        dmask = xr.Dataset()
        geo_B, _ = get_Bertrand_proposal(poly, parent_id=area_id + "_compass_")
        for area in geo_B["features"]:
            compass_poly = geom.asShape(area["geometry"])
            compass_id = area["id"]
            area["properties"]["type"] = "compass"
            dtemp = self.get_mask_on_grid(
                grid, compass_poly, compass_id, area["properties"]
            )
            try:
                dmask = xr.merge([dmask, dtemp])
            except Exception as excpt:
                LOGGER.warning(
                    "Failed to merge masks.",
                    dmask=dmask,
                    dtemp=dtemp,
                    area_id=area_id,
                    grid=grid,
                    func="get_compass_area",
                )
                raise excpt
        return dmask

    def get_mask_on_grid(self, grid, poly, area_id, properties):
        """
        Args:
            grid (dataset): La grille d'intérêt
            poly (shape): The shape we will transfer to netcdf
            area_id (str): Id
            properties (dict): Dictionnary of properties

        History :
           Removing md5sum by area.
        """
        areaType = properties.get("type", "")
        areaName = extract_areaName(properties)
        dtemp = self.get_mask(self.grid_ds, grid, poly)
        dtemp = dtemp.expand_dims(dim="id").assign_coords(id=[area_id])
        dtemp["areaName"] = (("id",), [areaName])
        dtemp["areaType"] = (("id",), [areaType])
        return dtemp
