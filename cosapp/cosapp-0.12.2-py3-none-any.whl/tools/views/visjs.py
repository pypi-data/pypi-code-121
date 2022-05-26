"""Build a VISjs view of a System."""

import os
from typing import Dict, List, Optional, Tuple, Union

from cosapp.drivers import Driver
from cosapp.ports.port import BasePort, ExtensiblePort
from cosapp.systems import System
from cosapp.tools import templates

from .baseRenderer import BaseRenderer


class VisJsRenderer(BaseRenderer):
    """
    Utility class to export a system as HTML using vis.JS library.

    Parameters
    ----------
    system : System
        System to export
    embeddable: bool, optional
        Is the HTML to be embedded in an existing page? Default: False
    """

    __globals = None

    def __init__(self, system: System, embeddable=False):
        super().__init__(system, embeddable)

    def get_data(self, focus_system: Optional[System] = None) -> Dict:
        """Convert the `System` in a dictionary with 4 keys: title, nodes, edges and groups.

        The title is a string with the Module name.
        The nodes is a list of dictionaries defining node for vis JS library.
        The edges is a list of dictionaries defining edge for vis JS library.
        The groups is a list of string defining the nodes clusters for vis JS library.

        Parameters
        ----------
        focus_system : System or None
            System on which the visualization should focus by default

        Returns
        -------
        dict
            Dictionary containing elements to draw the `System` using visJS library
        """
        def visjs_data(system, focus_system: Optional[System] = None) -> Dict:
            if system.parent is not None:
                center = system if focus_system is None else focus_system
                return visjs_data(system.parent, center)

            def get_component2id(
                system: System,
                cmpt2id: Dict[Union[System, BasePort], int],
                node_id: int,
                edges: List[Dict],
            ) -> Tuple[Dict[Union[System, BasePort], int], int, List[Dict]]:
                """Set the mapping between the `Module` and their unique id.

                Parameters
                ----------
                system : Module
                    The parent `Module` for which id must be set
                cmpt2id : Dict[Union[Module, BasePort], int]
                    Mapping of `Module` or port and its id
                node_id : int
                    Latest used id
                edges : List[Dict]
                    List of connection edges

                Returns
                -------
                tuple (List[Dict], Dict[Union["Module", "BasePort"], int], int)
                    The first is the mapping between each involved system or port and an unique id,
                    the second is the latest used id and
                    the third index is the list of edges (one per connector).
                """

                def get_driver2id(driver, cmpt2id, node_id, edges):
                    if driver not in cmpt2id:
                        cmpt2id[driver] = node_id
                        node_id += 1

                    previous_child = None
                    for child in driver.children.values():
                        cmpt2id, node_id, edges = get_driver2id(
                            child, cmpt2id, node_id, edges
                        )
                        # Connection between same level drivers
                        if previous_child is not None: 
                            edges.append(
                                {
                                    "from": cmpt2id[previous_child],
                                    "to": cmpt2id[child],
                                    "arrows": "to",
                                    "title": "",
                                    "hidden": True,
                                    "physics": False,
                                }
                            )
                        previous_child = child
                        # Connection with parent driver
                        edges.append(
                            {
                                "from": cmpt2id[driver],
                                "to": cmpt2id[child],
                                "title": "",
                                "hidden": True,
                                "physics": False,
                            }
                        )

                    return cmpt2id, node_id, edges

                def connectors_to_visJS(
                    system: System,
                    component_id: Optional[Dict[Union[System, BasePort], int]] = None,
                    node_id: int = 1,
                ) -> Tuple[List[Dict], Dict[Union[System, BasePort], int], int]:
                    """Build the dictionary the list of edges.

                    Parameters
                    ----------
                    system : System
                        System owning the connectors
                    component_id : Dict[Union[System, Port], int], optional
                        Mapping of `System` or `Port` and its unique id; default None
                    node_id : int, optional
                        Latest used id; default 1

                    Returns
                    -------
                    tuple (List[Dict], Dict[Union["System", "BasePort"], int], int)
                        First index is the list of edges (one per connector);
                        second index is the mapping between each involved system/port and a unique id;
                        third index is the latest id used.
                    """
                    edges = list()

                    for connection in system.connectors.values():
                        supplier = connection.source.owner
                        if supplier.children:  # Insert port as node
                            supplier = connection.source

                        if supplier not in component_id:
                            component_id[supplier] = node_id
                            node_id += 1

                        target = connection.sink.owner
                        if target.children:  # Insert port as node
                            target = connection.sink

                        if target not in component_id:
                            component_id[target] = node_id
                            node_id += 1

                        edge = {
                            "from": component_id[supplier],
                            "to": component_id[target],
                            "arrows": "to",
                            "title": "",
                        }
                        if connection.is_mirror():
                            edge["title"] = type(connection.source).__name__
                        else:
                            to = "&#8594;"  # rightarrow
                            edge["title"] = ", ".join(
                                origin if origin == target else f"{origin}{to}{target}"
                                for target, origin in connection.mapping.items()
                            ).join("[]")

                        edges.append(edge)

                        # if supplier or target is top-system, set edge.length = 0
                        if (
                            connection.source.owner is connection.sink.owner.parent
                            or connection.source.owner.parent is connection.sink.owner
                        ):
                            edges[-1]["length"] = 0

                    return edges, component_id, node_id

                for driver in system.drivers.values():
                    cmpt2id, node_id, edges = get_driver2id(driver, cmpt2id, node_id, edges)

                for cpt in system.children.values():
                    if cpt not in cmpt2id:
                        cmpt2id[cpt] = node_id
                        node_id += 1

                    if cpt.children:
                        cmpt2id, node_id, edges = get_component2id(cpt, cmpt2id, node_id, edges)

                local_edges, cmpt2id, node_id = connectors_to_visJS(system, cmpt2id, node_id)
                edges.extend(local_edges)

                return cmpt2id, node_id, edges

            cmpt2id = dict()
            id = 1
            edges = list()
            cmpt2id, id_init, edges = get_component2id(system, cmpt2id, id, edges)

            nodes = list()
            # Add hidden node for the top system
            nodes.append(
                dict(
                    label=f"{system.name}",
                    title=f"{system.name} - {system.__class__.__name__}",
                    id=id_init,
                    level=0,
                    hidden=True,
                    physics=False,
                    group=f".{system.name}",
                )
            )

            # Add edges from uppest level to its children but deactivate physics on
            # them. The goal is to have them available for the hierarchical view but
            # not playing any role in the default layout.
            for child in system.children.values():
                edges.append(
                    {
                        "from": id_init,
                        "to": cmpt2id[child],
                        "hidden": True,
                        "physics": False,
                    }
                )

            groups = list()
            for c, id in cmpt2id.items():
                if isinstance(c, BasePort):
                    ref = dict(
                        title=f"{c.full_name(trim_root=True)}",
                        id=id,
                        group=f"{c.owner.full_name()}",
                        mass=2,
                    )
                    if not isinstance(c, ExtensiblePort):
                        ref["title"] += f" - {type(c).__name__}"

                    # Add edge to bind to central owner node
                    edge = {
                        "from": id,
                        "to": cmpt2id[c.owner] if c.owner in cmpt2id else id_init,
                        "hidden": True,
                    }
                    if id_init in (edge["from"], edge["to"]):
                        edge["physics"] = False
                    edges.append(edge)

                elif isinstance(c, Driver):
                    # Add driver node
                    ref = dict(
                        label=type(c).__name__,
                        title=f"{c.name} - {type(c).__name__}",
                        id=id,
                        level=-0.7,
                        shape="box",
                        hidden=True,
                        physics=False,
                        group=f"{c.owner.full_name()}",
                    )

                    # Add edge to Module owner if top driver
                    if c.parent is None:
                        edges.append(
                            {
                                "from": cmpt2id[c.owner] if c.owner in cmpt2id else id_init,
                                "to": cmpt2id[c],
                                "dashes": True,
                                "hidden": True,
                                "physics": False,
                            }
                        )
                    else:

                        def driver_depth(driver: Driver, depth: int = 0) -> int:
                            if driver.parent is None:
                                return depth
                            else:
                                return driver_depth(driver.parent, depth + 1)

                        ref["level"] += 0.2 * driver_depth(c)

                else:
                    ref = dict(
                        label=f"{c.name}",
                        title=f"{c.full_name(trim_root=True)} - {type(c).__name__}", 
                        id=id,
                    )

                    if c.children:  # Component containing component => Cluster
                        ref["hidden"] = True

                        # Add edge to force binding to central system node
                        for child in c.children.values():
                            edges.append({"from": id, "to": cmpt2id[child], "hidden": True})

                    ref["group"] = f"{c.parent.full_name()}"

                group = ref["group"]
                ref.setdefault("level", 0)
                ref["level"] += group.count(".") + 1  # Set hierarchical level

                nodes.append(ref)
                if group not in groups:
                    groups.append(group)

            # Sort the groups by system to ensure that levels are clustered bottom-up
            groups.sort(reverse=True)

            data = {"title": system.name, "nodes": nodes, "edges": edges, "groups": groups}

            if focus_system is not None:
                data["center_id"] = cmpt2id[focus_system]

            return data

        return visjs_data(self.system, focus_system)

    def html_content(self) -> str:
        """Returns vis.JS HTML content of renderer"s system as a character string."""
        elements = self.get_data()
        common = self.get_globals()
        elements["visJS"] = common["visJS"]
        elements["visCSS"] = common["visCSS"]
        html_begin_tags = common["html_begin_tags"]
        html_end_tags = common["html_end_tags"]
        template = common["template"]
        
        content = template.render(elements)
        if not self.embeddable:
            html_begin_tags = html_begin_tags.replace("{{title}}", elements["title"])
            content = html_begin_tags + content + html_end_tags

        return content

    @classmethod
    def html_resources(cls) -> Dict[str, str]:
        """
        Return a dictionary of two keys.

        - `visJS` key holds the content of vis.js library.
        - `visCSS` key holds the css style of plot.

        Returns
        -------
        Dict[str, Dict]
            The necessary resources to render Jinja template
        """
        ressource_dir = os.path.dirname(os.path.abspath(templates.__file__))
        libs_dir = os.path.join(ressource_dir, "lib")

        with open(os.path.join(libs_dir, "vis.min.js"), "rb") as f:
            vis_js = f.read().decode("utf-8")
        with open(os.path.join(libs_dir, "vis.min.css"), "rb") as f:
            vis_css = f.read().decode("utf-8")

        return {"visJS": vis_js, "visCSS": vis_css}
    
    @classmethod
    def html_template(cls) -> "Template":
        """
        Return the Jinja template used to create HTML file.

        Returns
        -------
        Template
        """
        try:
            from jinja2 import Environment, PackageLoader
        except ImportError:
            raise ImportError("jinja2 needs to be installed to export to vis JS.")

        env = Environment(
            loader=PackageLoader("cosapp.tools", "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template("system_repr.html")
        return template
    
    @classmethod
    def get_globals(cls):
        cg = cls.__globals
        if cg is None:
            cg = super().get_globals()
        return cg


def visjs_html(system: System, embeddable=False) -> str:
    """Returns vis.JS HTML content of `system`.

    Parameters
    ----------
    system : System
        System to export

    embeddable: bool, optional
        Is the HTML to be embedded in an existing page? Default: False
    """
    renderer = VisJsRenderer(system, embeddable)
    return renderer.html_content()


def to_visjs(system: System, filename: str, embeddable=False) -> None:
    """Export a system as HTML using vis.JS library.

    Parameters
    ----------
    system : System
        System to export
    filename : str
        Filename to write to
    embeddable: bool, optional
        Is the HTML to be embedded in an existing page? Default: False
    """
    ext = os.path.splitext(filename)[1]
    html_ext = f"{os.extsep}html"
    if ext != html_ext:
        filename += html_ext

    rendered_html = visjs_html(system, embeddable)
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(rendered_html)
