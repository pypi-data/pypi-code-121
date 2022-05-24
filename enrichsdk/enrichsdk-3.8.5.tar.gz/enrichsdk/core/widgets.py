import os
import re
import json
from ..lib import renderlib


class Widgets(object):
    """
    List of available widgets
    """

    pass


############################################
# Update the widget class with attributes.
############################################
thisdir = os.path.dirname(__file__)
templatedir = os.path.join(thisdir, "..", "templates")
templatedir = os.path.abspath(templatedir)
widgetdir = os.path.join(templatedir, "widgets")


def get_func(attrname, filename):
    def dummyfunc():
        pass

    content = open(os.path.join(widgetdir, filename)).read()
    try:
        content = re.search(r"<!--(.*)-->", content).group(1)
    except:
        content = "Widget"

    # Get variables...
    variables = renderlib.template_get_variables(widgetdir, attrname)

    if len(variables) > 0:
        content += """

    Args:

"""
        for v in variables:
            content += "        " + v + "(str): parameter\n"

    content += """
    Returns:

       Rendered html 
"""
    dummyfunc.__doc__ = content
    return dummyfunc


for filename in os.listdir(widgetdir):
    if not filename.endswith(".html"):
        continue

    attrname = filename.replace(".html", "")
    attr = get_func(attrname, filename)
    setattr(Widgets, attrname, property(attr))
