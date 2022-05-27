from ingestor.common.constants import (
    CONTENT_ID,
    YEAR,
    DURATION_MINUTE,
    TITLE,
    STATUS,
    IS_GEO_BLOCK,
    IS_FREE,
    IS_ORIGINAL,
    IS_BRANDED,
    IS_EXCLUSIVE,
    SYNOPSIS,
    SYNOPSIS_EN,
    START_DATE,
    END_DATE,
    MODIFIED_ON,
    CREATED_ON,
    TYPE,
    RATING,
)


def fetch_setup_default_minus_one(node_property, feature, property_value):
    if feature in property_value.keys():
        node_property[feature] = property_value[feature]
    else:
        node_property[feature] = -1
    return node_property


def fetch_setup_default_minus_one_str(node_property, feature, property_value):
    if feature in property_value.keys():
        node_property[feature] = property_value[feature]
    else:
        node_property[feature] = "-1"
    return node_property


def fetch_setup_default_minus_one_date(node_property, feature, property_value):
    if feature in property_value.keys():
        node_property[feature] = str(property_value[feature])
    else:
        node_property[feature] = "-1"
    return node_property


# Content Node Properties
def content_node_properties(property_value):
    node_property = {}
    node_property = fetch_setup_default_minus_one(node_property, CONTENT_ID, property_value)
    node_property = fetch_setup_default_minus_one(node_property, YEAR, property_value)
    node_property = fetch_setup_default_minus_one(node_property, DURATION_MINUTE, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, TITLE, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, STATUS, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, IS_GEO_BLOCK, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, IS_FREE, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, IS_ORIGINAL, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, IS_BRANDED, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, IS_EXCLUSIVE, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, SYNOPSIS, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, SYNOPSIS_EN, property_value)
    node_property = fetch_setup_default_minus_one_date(node_property, START_DATE, property_value)
    node_property = fetch_setup_default_minus_one_date(node_property, END_DATE, property_value)
    node_property = fetch_setup_default_minus_one_date(node_property, MODIFIED_ON, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, CREATED_ON, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, TYPE, property_value)
    node_property = fetch_setup_default_minus_one_str(node_property, RATING, property_value)
    return node_property


"""DEFINING RELATIONSHIP NAMES"""
HAS_CATEGORY = "HAS_CATEGORY"
HAS_SUBCATEGORY = "HAS_SUBCATEGORY"
HAS_COUNTRY = "HAS_COUNTRY"
HAS_TAG = "HAS_TAG"
HAS_ACTOR = "HAS_ACTOR"
HAS_CONTENT_CORE = "HAS_CONTENT_CORE"
HAS_PRODUCT = "HAS_PRODUCT"
HAS_PACKAGE = "HAS_PACKAGE"
HAS_HOMEPAGE = "HAS_HOMEPAGE"
