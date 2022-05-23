import sysconfig

NAME = "Ewoks example super-category"

DESCRIPTION = "Short super-category description"

LONG_DESCRIPTION = "Long super-category description"

ICON = "icons/category.svg"

BACKGROUND = "light-blue"

WIDGET_HELP_PATH = (
    # Development documentation (make htmlhelp in ./doc)
    ("{DEVELOP_ROOT}/doc/_build/htmlhelp/index.html", None),
    # Documentation included in wheel
    ("{}/help/orange3-example/index.html".format(sysconfig.get_path("data")), None),
    # Online documentation url
    ("http://orange3-example-addon.readthedocs.io/en/latest/", ""),
)


def widget_discovery(discovery):
    import pkg_resources

    distroname = pkg_resources.safe_name("ewoks-example-1-addon")
    dist = pkg_resources.get_distribution(distroname)
    pkgs = [
        "orangecontrib.ewoks_example_supercategory.ewoks_example_subcategory",
    ]
    for pkg in pkgs:
        discovery.process_category_package(pkg, distribution=dist)
