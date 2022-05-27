""" Parser utils for schema viewer
"""
from core_parser_app.tools.parser.parser import XSDParser, remove_child_element
from core_parser_app.tools.parser.renderer.list import ListRenderer
from core_schema_viewer_app.settings import PARSER_DOWNLOAD_DEPENDENCIES
from core_parser_app.components.data_structure_element import (
    api as data_structure_element_api,
)


def get_parser(request=None):
    """Returns parser

    Returns:

    """

    return XSDParser(
        min_tree=True,
        ignore_modules=True,
        collapse=True,
        auto_key_keyref=False,
        implicit_extension_base=False,
        download_dependencies=PARSER_DOWNLOAD_DEPENDENCIES,
        store_type=False,
        request=request,
    )


# FIXME: refactor code
def generate_form(xsd_string, data_structure=None, request=None):
    """Generates the form using the parser, returns the root element

    Args:
        xsd_string:

    Returns:

    """
    # build parser
    parser = get_parser(request=request)
    # generate form
    root_element_id = parser.generate_form(
        xsd_string, data_structure=data_structure, request=request
    )
    # get the root element
    root_element = data_structure_element_api.get_by_id(
        root_element_id, request=request
    )

    return root_element


def render_form(request, root_element):
    """Render the form.

    Args:
        request:
        root_element:

    Returns:

    """
    # build a renderer
    renderer = ListRenderer(root_element, request)
    # render the form
    xsd_form = renderer.render()

    return xsd_form


def generate_element_absent(request, element_id, xsd_string, data_structure=None):
    """Generate an element absent from the form

    Args:
        request:
        element_id:
        xsd_string:

    Returns:

    """
    xsd_parser = get_parser()
    html_form = xsd_parser.generate_element_absent(
        request,
        element_id,
        xsd_string,
        data_structure=data_structure,
        renderer_class=ListRenderer,
    )
    return html_form


def generate_choice_absent(request, element_id, xsd_string):
    """Generate a choice branch absent from the form

    Args:
        request:
        element_id:
        xsd_string:

    Returns:

    """
    xsd_parser = get_parser()
    html_form = xsd_parser.generate_choice_absent(
        request, element_id, xsd_string, renderer_class=ListRenderer
    )
    return html_form


# TODO: need to be reworked + similar as code in curate/explore app
def remove_form_element(request, element_id):
    """Remove an element from the form.

    Args:
        request:
        element_id:

    Returns:

    """
    element_list = data_structure_element_api.get_all_by_child_id(element_id, request)

    if len(element_list) == 0:
        raise ValueError("No Data Structure Element found")
    elif len(element_list) > 1:
        raise ValueError("More than one Data Structure Element found")

    # Removing the element from the data structure
    data_structure_element = element_list[0]
    data_structure_element_to_pull = data_structure_element_api.get_by_id(
        element_id, request
    )

    # number of children after deletion
    children_number = len(data_structure_element.children) - 1

    data_structure_element = remove_child_element(
        data_structure_element, data_structure_element_to_pull, request
    )

    code = 0
    html_form = ""

    if children_number <= data_structure_element.options["min"]:
        # len(schema_element.children) == schema_element.options['min']
        if data_structure_element.options["min"] != 0:
            code = 1
        else:  # schema_element.options['min'] == 0
            code = 2
            renderer = ListRenderer(data_structure_element, request)
            html_form = renderer.render(True)

    return code, html_form
