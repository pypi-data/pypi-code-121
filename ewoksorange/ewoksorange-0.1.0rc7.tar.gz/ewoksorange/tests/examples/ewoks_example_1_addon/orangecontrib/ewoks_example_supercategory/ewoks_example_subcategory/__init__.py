import sysconfig

NAME = "Ewoks example sub-category"

DESCRIPTION = "Short sub-category description"

LONG_DESCRIPTION = "Long sub-category description"

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
