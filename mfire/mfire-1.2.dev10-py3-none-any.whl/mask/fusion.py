import shapely.geometry as geom
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="mask_processor", bind="fusion")


def extract_areaName(properties: dict) -> str:
    """ This enables to extract the name of the area from the configurations

        Args:
            properties ([dict]): The properties dictionnary.
            This dictionnary may contain "label", "alt_label", "name"

        Raises:
            ValueError: If we are not able to name the area we raise an error

        Returns:
            [str]: The areaName
        """
    for key in ("name", "label", "alt_label", "areaName", "area_name"):
        if key in properties and properties.get(key):
            return properties[key]
    raise ValueError(
        " Name was not found. Label cannot be split using '_' in 1 "
        "or 4 elements.  alt_label was empty."
    )


def check_fusion(my_area, list_poss):
    res = True
    for area in list_poss:
        poly = geom.asShape(area["geometry"])  # .buffer(1e-5).buffer(-1e-5)
        if not poly.intersects(my_area):
            continue
        if not poly.geometryType() in ["Polygon", "MultiPolygon"]:
            LOGGER.info(f"Geometry {poly.geometryType()}")
            continue

        if poly.intersection(my_area).area / poly.union(my_area).area > 0.9:
            # Si la zone n'est pas assez différente d'une des zones descriptive
            res = False
            name = extract_areaName(area["properties"])
            LOGGER.info(f"On a trouvé une zone similaire dans les entrées {name}")
            pass

    return res


def perform_poly_fusion(axe, list_area: list, parent_id: str) -> list:
    """Cette fonction retourne la liste des fusions de zones incluses dans la zone.
    La premiere étape consite à regarder quelle sont les zones au moins inclus à un
    certain pourcentage dans la zone et ne couvrant pas totalement la zone.
    La seconde étape consiste à parcourir ces zones et à essayer de les fusionner.

    A faire:
       Voir si on peut faire une récursion pour pouvoir créer des zones fusionnant
       plus de zones. Mettre une condition d'arrêt sur la taille du nom de la zone
       Améliorer la fusion de nom (par ex. sur le pays de Brocéliande et le pays de
       Caux pourrait se transformer en sur les pays de Brocéliande et de Caux.)

    Args:
        axe (Shape): La forme de l'axe
        list_area (list): La liste des zones que l'on pourrait fusionner
        parent_id (str): L'id de l'axe


    Returns:
        [list]: Une liste permettant de générer les nouvelles zones par fusion de netcdf
                avec les infos nécessaires.
    """
    # On va recupere les zones qui sont inclues dans l'axe.
    percent = 0.9
    l_poss = []
    for area in list_area["features"]:
        poly = geom.asShape(area["geometry"])
        if (
            poly.area > 0
            and poly.intersection(axe).area / poly.area > percent
            and poly.intersection(axe).area / axe.area < 0.97
        ):
            l_poss.append(area)
    l_fus = []
    for i, area1 in enumerate(l_poss[:-1]):
        for area2 in l_poss[i:]:
            p1 = geom.asShape(area1["geometry"])
            p2 = geom.asShape(area2["geometry"])
            # Si l'interesection est inferieur a un certain pourcentage
            # on a une nouvelle zone
            if (
                p1.intersection(p2).area / p1.area < 0.1
                and p1.intersection(p2).area / p2.area < 0.1
            ):
                fusion = p1.union(p2)
                # On va vérifier que la fusion ne soit pas déjà incluse dans les zones
                if check_fusion(fusion, l_poss):
                    name = (
                        extract_areaName(area1["properties"])
                        + " et "
                        + extract_areaName(area2["properties"])
                    )
                    new_id = "__".join([parent_id, area1["id"], area2["id"]])
                    LOGGER.debug(f"On ajout a la liste {name} avec comme id {new_id}")
                    descript = {
                        "name": name,
                        "base": [area1["id"], area2["id"]],
                        "id": new_id,
                        "areaType": "fusion2",
                    }
                    l_fus.append(descript)
    return l_fus


if __name__ == "__main__":
    import json

    def get_axe(feature):
        return feature["properties"].get("is_axe", False)

    input_file = "test_json.json"
    input_file = "/home/labia/chabotv/configProm/CD05/test_area.json"
    with open(input_file, "r") as fp:
        data = json.load(fp)
    data["geos"]["features"].sort(key=get_axe)

    for area in data["geos"]["features"]:
        is_axe = area["properties"].get("is_axe", False)
        if is_axe:
            print(f"Le nom du domaine est {extract_areaName(area['properties'])}")
            poly = geom.asShape(area["geometry"])
            if poly.geometryType() in ["Polygon", "MultiPolygon"]:
                area_id = area["id"]
                output_list = perform_poly_fusion(poly, data["geos"], area_id)
                # print(output_list)
