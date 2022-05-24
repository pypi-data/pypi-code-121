"""
Module containing utils for the dataset package.

Author: Riccardo Spezialetti
Mail: riccardo.spezialetti@unibo.it
"""

from typing import Dict


def get_shape_net_categories() -> Dict[str, str]:
    """Get ShapeNet categories.

    Returns:
        A dictionary containing the id and name of the category as key and values respectively.
    """
    dict_cat_name: Dict[str, str] = {
        "02691156": "airplane",
        "02747177": "trash bin",
        "02773838": "bag",
        "02801938": "basket",
        "02808440": "bathtub",
        "02818832": "bed",
        "02828884": "bench",
        "02834778": "bicycle",
        "02843684": "birdhouse",
        "02871439": "bookshelf",
        "02876657": "bottle",
        "02880940": "bowl",
        "02924116": "bus",
        "02933112": "cabinet",
        "02942699": "camera",
        "02946921": "can",
        "02954340": "cap",
        "02958343": "car",
        "03001627": "chair",
        "03085013": "keyboard",
        "03207941": "dishwasher",
        "03211117": "display",
        "03261776": "earphone",
        "03325088": "faucet",
        "03337140": "file cabinet",
        "03467517": "guitar",
        "03593526": "jar",
        "03624134": "knife",
        "03636649": "lamp",
        "03642806": "laptop",
        "03691459": "loudspeaker",
        "03710193": "mailbox",
        "03759954": "microphone",
        "03790512": "motorbike",
        "03797390": "mug",
        "03928116": "piano",
        "03938244": "pillow",
        "03948459": "pistol",
        "04004475": "printer",
        "04074963": "remote",
        "04090263": "rifle",
        "04099429": "rocket",
        "04225987": "skateboard",
        "04256520": "sofa",
        "04330267": "stove",
        "04379243": "table",
        "04401088": "telephone",
        "04460130": "tower",
        "04468005": "train",
        "04530566": "watercraft",
        "04554684": "washer",
    }

    return dict_cat_name


def get_shape_net_category_name_from_id(id: str) -> str:
    """Get the name of ShapeNet category from the id.

    Args:
        id: the the category id.

    Raises:
        KeyError: if the id is not present in the set of categories.

    Returns:
        The name of the category.
    """
    dict_id_to_name = get_shape_net_categories()

    name_category = dict_id_to_name.get(id)

    if not name_category:
        raise KeyError(f"Category with id: {id} not found in {dict_id_to_name}.")

    return name_category
