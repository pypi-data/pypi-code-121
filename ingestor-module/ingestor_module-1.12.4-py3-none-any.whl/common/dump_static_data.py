import warnings

from pandas import read_csv

from static_node_generator import StaticNodeGenerator

warnings.filterwarnings('ignore')

LOCAL_CONNECTION_URI = "ws://localhost:8182/gremlin"
STATIC_FILES_PATH = "static_files/"


def dump_category_nodes():
    """to dump category nodes into GraphDB"""
    cat_data = read_csv(
        STATIC_FILES_PATH +
        "CategoryV5_20220104.csv"
    )
    cat_cls = StaticNodeGenerator(
        data=cat_data,
        label="category",
        connection_uri=LOCAL_CONNECTION_URI
    )
    cat_cls.category_controller()


def dump_subcategory_nodes():
    """to dump subcategory nodes into GraphDB"""
    subcat_data = read_csv(
        STATIC_FILES_PATH +
        "SubCategory_20220104.csv"
    )
    subcat_cls = StaticNodeGenerator(
        data=subcat_data,
        label="subcategory",
        connection_uri=LOCAL_CONNECTION_URI
    )
    subcat_cls.subcategory_controller()


def dump_homepage_nodes():
    """to dump homepage nodes into GraphDB"""
    homepage_data = read_csv(
        STATIC_FILES_PATH +
        "Homepage.csv"
    )
    homepage_cls = StaticNodeGenerator(
        data=homepage_data,
        label="homepage",
        connection_uri=LOCAL_CONNECTION_URI
    )
    homepage_cls.homepage_controller()


def dump_actor_nodes():
    # to dump actor nodes into GraphDB
    actor_data = read_csv(
        STATIC_FILES_PATH +
        "Actor_20220104.csv"
    )
    actor_cls = StaticNodeGenerator(
        data=actor_data,
        label="actor",
        connection_uri=LOCAL_CONNECTION_URI
    )
    actor_cls.actor_controller()


def dump_tag_nodes():
    """to dump tag nodes into GraphDB"""
    tags_data = read_csv(
        STATIC_FILES_PATH +
        "Tags_20220104.csv"
    )
    tags_cls = StaticNodeGenerator(
        data=tags_data,
        label="tags",
        connection_uri=LOCAL_CONNECTION_URI
    )
    tags_cls.tags_controller()


def dump_country_nodes():
    """to dump country nodes into GraphDB"""
    country_data = read_csv(
        STATIC_FILES_PATH +
        "Country_20220104.csv"
    )
    country_cls = StaticNodeGenerator(
        data=country_data,
        label="country",
        connection_uri=LOCAL_CONNECTION_URI
    )
    country_cls.country_controller()


def dump_paytv_nodes():
    """to dump paytv provider nodes into GraphDB"""
    paytv_data = read_csv(
        STATIC_FILES_PATH +
        "PayTVProvider_20220104.csv"
    )
    paytv_cls = StaticNodeGenerator(
        data=paytv_data,
        label="paytv_provider",
        connection_uri=LOCAL_CONNECTION_URI
    )
    paytv_cls.paytv_controller()


def dump_product_nodes():
    """to dump product provider nodes into GraphDB"""
    product_data = read_csv(
        STATIC_FILES_PATH +
        "Product_20220104.csv"
    )
    product_cls = StaticNodeGenerator(
        data=product_data,
        label="product",
        connection_uri=LOCAL_CONNECTION_URI
    )
    product_cls.product_controller()


def dump_package_nodes():
    """to dump product package nodes into GraphDB"""
    package_data = read_csv(
        STATIC_FILES_PATH +
        "Package_20220104.csv"
    )
    package_cls = StaticNodeGenerator(
        data=package_data,
        label="package",
        connection_uri=LOCAL_CONNECTION_URI
    )
    package_cls.package_controller()


def dump_season_nodes():
    """to dump product package nodes into GraphDB"""
    season_data = read_csv(
        STATIC_FILES_PATH +
        "Season_20220104.csv"
    )
    season_cls = StaticNodeGenerator(
        data=season_data,
        label="season",
        connection_uri=LOCAL_CONNECTION_URI
    )
    season_cls.season_controller()


if __name__ == '__main__':
    print("Dumping Category nodes....")
    dump_category_nodes()

    print("Dumping SubCategory nodes....")
    dump_subcategory_nodes()

    print("Dumping Homepage nodes....")
    dump_homepage_nodes()

    print("Dumping Actor nodes....")
    dump_actor_nodes()

    print("Dumping Tag nodes....")
    dump_tag_nodes()

    print("Dumping Country nodes....")
    dump_country_nodes()

    print("Dumping PayTVProvider nodes....")
    dump_paytv_nodes()

    print("Dumping Product nodes....")
    dump_product_nodes()

    print("Dumping Package nodes....")
    dump_package_nodes()

    print("Dumping Season nodes....")
    dump_season_nodes()
