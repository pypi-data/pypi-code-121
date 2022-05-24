import shapely.geometry as geom
from geojson import Feature, FeatureCollection


def get_rid_doublon(l_sub, percent):
    """
    Hypothesis : the region list is sort. Chosen region is the first encountered.
    This function delete "area" too closed (IoU > percent)
    """
    res = l_sub.pop(0)
    l_res = [
        res,
    ]
    geo_ref = geom.asShape(res["geometry"])
    if geo_ref.geometryType not in ["Polygon"]:
        buffering = True
        geo_ref = geo_ref.buffer(0.01)
    for x in l_sub:
        test_ref = geom.asShape(x["geometry"])
        if buffering:
            test_ref = test_ref.buffer(0.01)
        if geo_ref.intersection(test_ref).area / test_ref.union(geo_ref).area > percent:
            # print(f"On vire {x['properties']['name']}")
            l_sub.remove(x)

    if len(l_sub) == 0:
        return l_res
    else:
        l_res.extend(get_rid_doublon(l_sub, percent=percent))
        return l_res


def get_nw_opt1(geo, percent):
    [min_lon, min_lat, max_lon, max_lat] = geo.bounds
    delta_lon = max_lon - min_lon
    delta_lat = max_lat - min_lat
    coords = (
        (min_lon, max_lat),
        (min_lon, max_lat - percent * delta_lat),
        (min_lon + percent * delta_lon, max_lat),
    )

    return geom.Polygon(coords)


def get_ne(geo, percent):
    [min_lon, min_lat, max_lon, max_lat] = geo.bounds
    delta_lon = max_lon - min_lon
    delta_lat = max_lat - min_lat
    coords = (
        (max_lon, max_lat),
        (max_lon, max_lat - percent * delta_lat),
        (max_lon - percent * delta_lon, max_lat),
    )
    return geom.Polygon(coords)


def get_sw(geo, percent):
    [min_lon, min_lat, max_lon, max_lat] = geo.bounds
    delta_lon = max_lon - min_lon
    delta_lat = max_lat - min_lat
    coords = (
        (min_lon, min_lat),
        (min_lon, min_lat + percent * delta_lat),
        (min_lon + percent * delta_lon, min_lat),
    )
    return geom.Polygon(coords)


def get_se(geo, percent):
    [min_lon, min_lat, max_lon, max_lat] = geo.bounds
    delta_lon = max_lon - min_lon
    delta_lat = max_lat - min_lat
    coords = (
        (max_lon, min_lat),
        (max_lon, min_lat + percent * delta_lat),
        (max_lon - percent * delta_lon, min_lat),
    )
    return geom.Polygon(coords)


def get_south_polygon(geo, percent):
    [min_lon, min_lat, max_lon, max_lat] = geo.bounds
    delta_lat = max_lat - min_lat
    coords = (
        (min_lon, min_lat),
        (min_lon, min_lat + percent * delta_lat),
        (max_lon, min_lat + percent * delta_lat),
        (max_lon, min_lat),
    )
    return geom.Polygon(coords)


def get_north_polygon(geo, percent):
    [min_lon, min_lat, max_lon, max_lat] = geo.bounds
    delta_lat = max_lat - min_lat
    coords = (
        (min_lon, max_lat),
        (min_lon, max_lat - percent * delta_lat),
        (max_lon, max_lat - percent * delta_lat),
        (max_lon, max_lat),
    )
    return geom.Polygon(coords)


def get_west_polygon(geo, percent):
    [min_lon, min_lat, max_lon, max_lat] = geo.bounds
    delta_lon = max_lon - min_lon
    coords = (
        (min_lon, min_lat),
        (min_lon, max_lat),
        (min_lon + percent * delta_lon, max_lat),
        (min_lon + percent * delta_lon, min_lat),
    )
    return geom.Polygon(coords)


def get_east_polygon(geo, percent):
    [min_lon, min_lat, max_lon, max_lat] = geo.bounds
    delta_lon = max_lon - min_lon
    coords = (
        (max_lon, min_lat),
        (max_lon, max_lat),
        (max_lon - percent * delta_lon, max_lat),
        (max_lon - percent * delta_lon, min_lat),
    )
    return geom.Polygon(coords)


def test_area(geo, sub, min_area, max_area):
    """
    Test si la nouvelle zone est bien "assez grande" mais "pas trop grande"
    par rapport à sa zone d'origine.

    Args:
        geo ([type]): Zone géographique d'origine
        sub ([type]): Découpe
        min_area ([type]): Pourcentage minimum de l'aire geographique
            (vis à vis de la zone d'origine)
        max_area ([type]): Pourcentage maximum de l'aire géographique
            (vis à vis de la zone d'origine)

    Returns:
        [type]: [description]
    """
    if geo.geometryType not in ["Polygon"]:
        geo_t = geo.buffer(0.05)
        sub_t = sub.buffer(0.05)
    else:
        geo_t = geo
        sub_t = geo
    if (sub_t.area > geo_t.area * min_area / 100) and (
        sub_t.area < geo_t.area * max_area / 100
    ):
        return True
    else:
        # print("Test failed")
        return False


def return_name(collection, key="name"):
    """
    Fonction qui retourne les noms des polygones.
    Permet d'aider au choix (si on ne connait pas les noms c'est complexe).
    La clé utilisée est "key".
    """
    l_name = []
    for feature in collection["features"]:
        l_name.append(feature["properties"][key])
    return l_name


def return_poly(poly_list, name, key="name"):
    """
    Retourne le polygone ayant le nom name.
    La clé utilisée est "key"
    """
    for poly in poly_list["features"]:
        if poly["properties"][key] == name:
            return poly
    names = sorted(return_name(poly_list, key=key))
    raise ValueError(f"Name {name} not found. Possibilies are {names}.")


def get_Bertrand_proposal(geo, parent_id=""):
    percent_one = 0.5
    percent_small = 0.35
    percent_big = 0.65
    percent_x = 0.8
    min_area = 10
    max_area = 80
    l_feat = []
    l_name = []

    buffer_size = 0.02  # Sert à ne pas avoir des zones trop petites
    west = get_west_polygon(geo, percent_one)
    name = "dans l'Ouest"
    inter = geo.intersection(west)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_Ouest",
                properties={"name": name},
            )
        )
    west = get_west_polygon(geo, percent_small)
    name = "dans une petite moitié Ouest"
    inter = geo.intersection(west)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_SmallOuest",
                properties={"name": name},
            )
        )
    west = get_west_polygon(geo, percent_big)
    name = "dans une grande moitié Ouest"
    inter = geo.intersection(west)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_BigOuest",
                properties={"name": name},
            )
        )

    south = get_south_polygon(geo, percent_one)
    name = "dans le Sud"
    inter = geo.intersection(south)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_Sud",
                properties={"name": name},
            )
        )
    south = get_south_polygon(geo, percent_small)
    name = "dans une petite moitié Sud"
    inter = geo.intersection(south)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_SmallSud",
                properties={"name": name},
            )
        )
    south = get_south_polygon(geo, percent_big)
    name = "dans une grande moitié Sud"
    inter = geo.intersection(south)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_BigSud",
                properties={"name": name},
            )
        )

    north = get_north_polygon(geo, percent_one)
    name = "dans le Nord"
    inter = geo.intersection(north)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_Nord",
                properties={"name": name},
            )
        )

    north = get_north_polygon(geo, percent_small)
    name = "dans une petite moitié Nord"
    inter = geo.intersection(north)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_SmallNord",
                properties={"name": name},
            )
        )

    north = get_north_polygon(geo, percent_big)
    name = "dans une grande moitié Nord"
    inter = geo.intersection(north)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_BigNord",
                properties={"name": name},
            )
        )

    east = get_east_polygon(geo, percent_one)
    name = "dans l'Est"
    inter = geo.intersection(east)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_Est",
                properties={"name": name},
            )
        )
    east = get_east_polygon(geo, percent_small)
    name = "dans une petite moitié Est"
    inter = geo.intersection(east)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_SmallEst",
                properties={"name": name},
            )
        )
    east = get_east_polygon(geo, percent_big)
    name = "dans une grande moitié Est"
    inter = geo.intersection(east)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_BigEst",
                properties={"name": name},
            )
        )

    nw = get_nw_opt1(geo, percent_x)
    name = "dans le Nord-Ouest"
    inter = geo.intersection(nw)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_NordOuest",
                properties={"name": name},
            )
        )

    ne = get_ne(geo, percent_x)
    name = "dans le Nord-Est"
    inter = geo.intersection(ne)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_NordEst",
                properties={"name": name},
            )
        )

    sw = get_sw(geo, percent_x)
    name = "dans le Sud-Ouest"
    inter = geo.intersection(sw)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_SudOuest",
                properties={"name": name},
            )
        )

    se = get_se(geo, percent_x)
    name = "dans le Sud-Est"
    inter = geo.intersection(se)
    if test_area(geo, inter, min_area, max_area):
        l_name.append(name)
        l_feat.append(
            Feature(
                geometry=inter.buffer(buffer_size),
                id=parent_id + "_SudEst",
                properties={"name": name},
            )
        )

    if not l_feat:
        return FeatureCollection([]), []

    no_doublon = get_rid_doublon(l_feat.copy(), percent=0.85)
    l_name = return_name(FeatureCollection(no_doublon), key="name")
    return FeatureCollection(no_doublon), l_name
