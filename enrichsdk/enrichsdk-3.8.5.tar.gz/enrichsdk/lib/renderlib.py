import os
import logging
from jinja2 import Environment, FileSystemLoader, meta

logger = logging.getLogger("app")

# Template rendering functions
def template_render(widgetdir, widgetname, context):
    """
    Render a specified template using the context

    Args:
      widgetname (str): Name of the template
      context (dict): Key-value pairs

    Returns:
      Rendered html template that can be embedded

    """
    filename = widgetname + ".html"
    env = Environment(loader=FileSystemLoader(widgetdir))
    try:
        template = env.get_template(filename)
        return template.render(context)
    except:
        logger.exception("Could not find template")
        return ""


def template_get_variables(widgetdir, widgetname):
    """
    Get the variables from a template

    Args:
       widgetname (str): Name of the template

    Returns:
       List of variables
    """
    filename = widgetname + ".html"
    env = Environment(loader=FileSystemLoader(widgetdir))
    try:
        template_source = env.loader.get_source(env, filename)[0]
        parsed_content = env.parse(template_source)
        return meta.find_undeclared_variables(parsed_content)
    except:
        return []
