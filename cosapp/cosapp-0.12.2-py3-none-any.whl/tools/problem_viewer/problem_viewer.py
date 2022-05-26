import os
import json

from typing import Any, Dict, Union

from collections import OrderedDict
import logging
import base64

from cosapp.systems import System
from cosapp.ports.port import BasePort, ExtensiblePort

from cosapp.utils.helpers import check_arg

logger = logging.getLogger(__name__)


def _get_tree_dict(
    obj: Union[System, BasePort],
    include_orphan_vars=True
) -> Dict[str, Any]:
    """Get a dictionary representation of the system hierarchy.
    """
    def init_tree(obj, subtype):
        return OrderedDict(
            name = obj.name,
            type = 'subsystem',
            subsystem_type = subtype,
        )

    def port_tree(port):
        tree_dict = init_tree(port, 'component')
        tree_dict['children'] = children = list()

        if include_orphan_vars or not isinstance(port, ExtensiblePort):
            dtype = 'param' if port.is_input else 'unknown'
            children.extend(
                map(lambda n: OrderedDict(name=n, type=dtype), iter(port))
            )
        return tree_dict

    def system_tree(system):
        tree_dict = init_tree(system, 'group')
        tree_dict['children'] = children = list()

        def add_ports(ports):
            nonlocal children
            children.extend(port_tree(port)
                for port in filter(lambda p: len(p) > 0, ports)
            )

        add_ports(system.inputs.values())

        children.extend(system_tree(child)
            for child in system.children.values()
        )
        # outputs come after child list for a matter of visualization
        add_ports(system.outputs.values())
        
        return tree_dict

    if isinstance(obj, System):
        return system_tree(obj)
    elif isinstance(obj, BasePort):
        return port_tree(obj)
    else:
        raise TypeError(f"Object must be a port or a system; got {type(obj)}.")


def _get_connections(system: System, include_orphan_vars: bool) -> Dict[str, str]:
    """Get a dictionary representation of the system connections. Structure is {'_in': '_out'}."""
    connections = OrderedDict()
    def add_prefix(name, s):
        return s if s.startswith(name) else f"{name}.{s}"

    # Gather connections for current system
    for c in system.connectors.values():
        if not include_orphan_vars and isinstance(c.sink, ExtensiblePort):
            continue

        for target, origin in c.mapping.items():
            connections[f"{c.sink.contextual_name}.{target}"] = f"{c.source.contextual_name}.{origin}"

    # Recursively gather children's connections
    for name, child in system.children.items():
        child_connections = _get_connections(child, include_orphan_vars)
        for k, v in child_connections.items():
            connections[add_prefix(name, k)] = add_prefix(name, v)

    return connections


def _get_viewer_data(system: System, include_orphan_vars: bool) -> Dict:
    """Get the data needed by the N2 viewer as a dictionary."""
    if isinstance(system, System):
        root_group = system
    else:
        raise TypeError('get_model_viewer_data only accepts System')

    if not include_orphan_vars:
        logger.warning('The system may contain inwards or outwards.')

    data_dict = {}
    data_dict['tree'] = _get_tree_dict(root_group, include_orphan_vars)
    connections_list = []
    connections = _get_connections(root_group, include_orphan_vars)
    for in_abs, out_abs in connections.items():
        if out_abs is None:
            continue
        connections_list.append(OrderedDict(src=out_abs, tgt=in_abs))
    data_dict['connections_list'] = connections_list

    return data_dict


def view_model(
    problem_or_filename,
    outfile='n2.html',
    show_browser=True,
    embeddable=False,
    draw_potential_connections=False,
    include_orphan_vars=True,
):
    """
    Generates an HTML file containing a tree viewer. Optionally pops up a web browser to
    view the file.

    Parameters
    ----------
    problem_or_filename : A System
        System : The System for the desired tree.

    outfile : str, optional
        The name of the final output file

    show_browser : bool, optional
        If True, pop up the system default web browser to view the generated html file.
        Defaults to True.

    embeddable : bool, optional
        If True, gives a single HTML file that doesn't have the <html>, <DOCTYPE>, <body>
        and <head> tags. If False, gives a single, standalone HTML file for viewing.

    draw_potential_connections : bool, optional
        If true, allows connections to be drawn on the N2 that do not currently exist
        in the model. Defaults to True.

    include_orphan_vars : bool, optional
    If True, display inwards and outwards on the N2 diagram. Defaults to True.
    """
    html_begin_tags = """<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    </head>
    <body>\n"""
    html_end_tags = """
    </body>
</html>"""

    code_dir = os.path.dirname(os.path.abspath(__file__))
    vis_dir = os.path.join(code_dir, "visualization")
    libs_dir = os.path.join(vis_dir, "libs")
    src_dir = os.path.join(vis_dir, "src")
    style_dir = os.path.join(vis_dir, "style")

    #grab the libraries
    with open(os.path.join(libs_dir, "awesomplete.js"), "r") as f:
        awesomplete = f.read()
    with open(os.path.join(libs_dir, "d3.v4.min.js"), "r") as f:
        d3 = f.read()
    with open(os.path.join(libs_dir, "vkBeautify.js"), "r") as f:
        vk_beautify = f.read()

    #grab the src
    with open(os.path.join(src_dir, "constants.js"), "r") as f:
        constants = f.read()
    with open(os.path.join(src_dir, "draw.js"), "r") as f:
        draw = f.read()
    with open(os.path.join(src_dir, "legend.js"), "r") as f:
        legend = f.read()
    with open(os.path.join(src_dir, "modal.js"), "r") as f:
        modal = f.read()
    with open(os.path.join(src_dir, "ptN2.js"), "r") as f:
        pt_n2 = f.read()
    with open(os.path.join(src_dir, "search.js"), "r") as f:
        search = f.read()
    with open(os.path.join(src_dir, "svg.js"), "r") as f:
        svg = f.read()

    #grab the style
    with open(os.path.join(style_dir, "awesomplete.css"), "r") as f:
        awesomplete_style = f.read()
    with open(os.path.join(style_dir, "partition_tree.css"), "r") as f:
        partition_tree_style = f.read()
    with open(os.path.join(style_dir, "fontello.woff"), "rb") as f:
        encoded_font = str(base64.b64encode(f.read()).decode("ascii"))

    #grab the index.html
    with open(os.path.join(vis_dir, "index.html"), "r") as f:
        index = f.read()

    #grab the model viewer data
    data = _get_viewer_data(problem_or_filename, include_orphan_vars)
    model_viewer_data = f"var modelData = {json.dumps(data)}"

    #add the necessary HTML tags if we aren't embedding
    if not embeddable:
        index = html_begin_tags + index + html_end_tags

    #put all style and JS into index
    index = index.replace('{{awesomplete_style}}', awesomplete_style)
    index = index.replace('{{partition_tree_style}}', partition_tree_style)
    index = index.replace('{{fontello}}', encoded_font)
    index = index.replace('{{d3_lib}}', d3)
    index = index.replace('{{awesomplete_lib}}', awesomplete)
    index = index.replace('{{vk_beautify_lib}}', vk_beautify)
    index = index.replace('{{model_data}}', model_viewer_data)
    index = index.replace('{{constants_lib}}', constants)
    index = index.replace('{{modal_lib}}', modal)
    index = index.replace('{{svg_lib}}', svg)
    index = index.replace('{{search_lib}}', search)
    index = index.replace('{{legend_lib}}', legend)
    index = index.replace('{{draw_lib}}', draw)
    index = index.replace('{{ptn2_lib}}', pt_n2)
    if draw_potential_connections:
        index = index.replace('{{draw_potential_connections}}', 'true')
    else:
        index = index.replace('{{draw_potential_connections}}', 'false')

    with open(outfile, 'w') as f:
        f.write(index)

    #open it up in the browser
    if show_browser:
        from cosapp.tools.problem_viewer.webview import webview
        webview(outfile)
