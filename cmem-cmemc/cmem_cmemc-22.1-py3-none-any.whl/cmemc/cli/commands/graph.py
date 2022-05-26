"""graph commands for cmem command line interface."""
import hashlib
import json
import os
from pathlib import Path
from xml.etree.ElementTree import (  # nosec
    Element,
    SubElement,
    tostring
)
from xml.dom import minidom  # nosec

from six.moves.urllib.parse import quote

import click

from jinja2 import Template

from treelib import Tree

from cmem.cmemc.cli import completion
from cmem.cmemc.cli.commands import CmemcCommand, CmemcGroup
from cmem.cmemc.cli.utils import (
    convert_uri_to_filename,
    get_graphs,
    get_graphs_as_dict,
    iri_to_qname,
    read_rdf_graph_files
)
from cmem.cmempy.config import get_cmem_base_uri
from cmem.cmempy.dp.authorization import refresh
from cmem.cmempy.dp.proxy import graph as graph_api
from cmem.cmempy.dp.proxy.graph import (
    get_graph_import_tree,
    get_graph_imports
)
from cmem.cmempy.dp.proxy.sparql import get as sparql_api


UNKNOWN_GRAPH_ERROR = "The graph {} is not accessible or does not exist."


def count_graph(graph_iri):
    """Count triples in a graph and return integer."""
    query = "SELECT (COUNT(*) as ?triples)" +\
            " FROM <" + graph_iri + ">" +\
            " WHERE { ?s ?p ?o }"
    result = json.loads(sparql_api(query, owl_imports_resolution=False))
    count = result["results"]["bindings"][0]["triples"]["value"]
    return int(count)


# pylint: disable=too-many-arguments
def _get_graph_to_file(
        graph_iri,
        file_path,
        app,
        numbers=None,
        overwrite=True,
        mime_type="application/n-triples"
):
    """Request a single graph to a single file (streamed).

    numbers is a tupel of current and count (for output only).
    """
    if os.path.exists(file_path):
        if overwrite is True:
            app.echo_warning(
                f"Output file {file_path} does exist: will overwrite it."
            )
        else:
            app.echo_warning(
                f"Output file {file_path} does exist: will append to it."
            )
    if numbers is not None:
        running_number, count = numbers
        if running_number is not None and count is not None:
            app.echo_info(
                f"Export graph {running_number}/{count}: "
                f"{graph_iri} to {file_path} ... ",
                nl=False
            )
    # create and write the .ttl content file
    if overwrite is True:
        triple_file = click.open_file(file_path, "wb")
    else:
        triple_file = click.open_file(file_path, "ab")
    with graph_api.get_streamed(graph_iri, accept=mime_type) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                triple_file.write(chunk)
        request_headers = response.request.headers
        request_headers.pop("Authorization")
        app.echo_debug(
            f"cmemc request headers: {request_headers}"
        )
        app.echo_debug(
            f"server response headers: {response.headers}"
        )
    if numbers is not None:
        app.echo_success("done")


def _get_export_names(app, iris, template) -> dict:
    """Get a dictionary of generated file names based on a template.

    Args:
        app: the context click application
        iris: list of graph iris
        template (str): the template string to use

    Returns:
        a dictionary with IRIs as keys and filenames as values

    Raises:
        ValueError in case the template string produces a naming clash,
            means two IRIs result in the same filename
    """
    template_data = app.get_template_data()
    _names = {}
    for iri in iris:
        template_data.update(
            hash=hashlib.sha256(iri.encode("utf-8")).hexdigest(),
            iriname=convert_uri_to_filename(iri)
        )
        _name_created = Template(template).render(template_data) + ".ttl"
        _names[iri] = _name_created
    if len(_names.values()) != len(set(_names.values())):
        raise ValueError(
            "The given template string produces a naming clash. "
            "Please use a different template to produce unique names."
        )
    return _names


def _create_node_label(iri, graphs):
    """Create a label for a node in the tree."""
    if iri not in graphs:
        return "[missing: " + iri + "]"
    title = graphs[iri]["label"]["title"]
    return f"{title} -- {iri}"


def _add_tree_nodes_recursive(tree, structure, iri, graphs):
    """Add all child nodes of iri from structure to tree.

    Call recursively until no child node can be used as parent anymore.

    Args:
        tree (treelib.Tree): the graph where to add the nodes
        structure (dict): the result dict of get_graph_import_tree()
        iri (str): The IRI of the parent
        graphs (list): the result of get_graphs()

    Returns:
        the new treelib.Tree object with the additional nodes
    """
    if not tree.contains(iri):
        tree.create_node(
            tag=_create_node_label(iri, graphs),
            identifier=iri
        )
    if iri not in structure.keys():
        return tree
    for child in structure[iri]:
        tree.create_node(
            tag=_create_node_label(child, graphs),
            identifier=child,
            parent=iri
        )
    for child in structure[iri]:
        if child in structure.keys():
            tree = _add_tree_nodes_recursive(
                tree, structure, child, graphs
            )
    return tree


def _add_ignored_nodes(tree, structure):
    """Add all child nodes as ignored nodes.

    Args:
        tree (treelib.Tree): the graph where to add the nodes
        structure (dict): the result dict of get_graph_import_tree()

    Returns:
        the new treelib.Tree object with the additional nodes
    """
    if len(structure.keys()) > 0:
        for parent in structure:
            for children in structure[parent]:
                tree.create_node(
                    tag="[ignored: " + children + "]",
                    parent=parent
                )
    return tree


def _get_graphs_filtered(filter_name, filter_value):
    """Get graphs but filtered according to name and value."""
    # not filtered means all graphs
    if filter_name is None:
        return get_graphs()
    # check for correct filter names
    possible_filter_names = ("access", "imported-by")
    if filter_name not in possible_filter_names:
        raise ValueError(
            f"{filter_name} is an unknown filter name. "
            f"Use one of {possible_filter_names}."
        )
    # filter by access condition
    if filter_name == "access":
        if filter_value == "writeable":
            graphs = get_graphs(writeable=True, readonly=False)
        elif filter_value == "readonly":
            graphs = get_graphs(writeable=False, readonly=True)
        else:
            raise ValueError(
                "Filter access is either 'readonly' or 'writeable'."
            )
    else:
        # default is all graphs
        graphs = get_graphs()
    # filter by imported-by
    if filter_name == "imported-by":
        if filter_value not in get_graphs_as_dict():
            raise ValueError(
                UNKNOWN_GRAPH_ERROR.format(filter_value)
            )
        imported_graphs = get_graph_imports(filter_value)
        graphs = [
            graph for graph in graphs
            if graph["iri"] in imported_graphs
        ]
    return graphs


def _add_imported_graphs(iris, all_graphs):
    """Get a list of graph IRIs extended with the imported graphs.

    Args:
        iris (list): list of graph IRIs
        all_graphs (dict): output of get_graphs_as_dict (dict of all graphs)

    Returns:
        list of graph IRIs
    """
    extended_list = iris
    for iri in set(iris):
        for _ in get_graph_imports(iri):
            # check if graph exist
            if _ in all_graphs.keys():
                extended_list.append(_)
    return list(set(extended_list))


def _check_and_extend_exported_graphs(
        iris, all_flag, imported_flag, all_graphs
):
    """Get a list of IRIs checked and extended.

    Args:
        iris (list): List or tupel of given user IRIs
        all_flag (bool): user wants all graphs
        imported_flag (bool): user wants imported graphs as well
        all_graphs (dict): dict of all graphs (get_graph_as_dict())

    Returns:
        checked and extended list of IRIs

    Raises:
         ValueError
    """
    # transform given IRI-tupel to a distinct IRI-list
    iris = list(set(iris))
    if len(iris) == 0 and not all_flag:
        raise ValueError(
            "Either provide at least one graph IRI or use the --all option "
            "in order to work with all graphs."
        )
    for iri in iris:
        if iri not in all_graphs.keys():
            raise ValueError(
                UNKNOWN_GRAPH_ERROR.format(iri)
            )
    if all_flag:
        # in case --all is given,
        # list of graphs is filled with all available graph IRIs
        iris = all_graphs.keys()
    elif imported_flag:
        # does not need be be executed in case of --all
        iris = _add_imported_graphs(iris, all_graphs)
    return iris


def _create_xml_catalog_file(app, names, output_dir):
    """Create a Protégé suitable XML catalog file.

    Args:
        app (context): the cmemc context object
        names (dict): output of _get_export_names()
        output_dir: path where to create the XML file

    """
    file_name = os.path.join(output_dir, "catalog-v001.xml")
    catalog = Element("catalog")
    catalog.set("prefer", "public")
    catalog.set("xmlns", "urn:oasis:names:tc:entity:xmlns:xml:catalog")
    for name in names.keys():
        uri = SubElement(catalog, 'uri')
        uri.set("id", "Auto-Generated Import Resolution by cmemc")
        uri.set("name", name)
        uri.set("uri", names[name])
    reparsed = minidom.parseString(  # nosec - since source is trusted
        tostring(catalog, 'utf-8')
    ).toprettyxml(indent="  ")
    file = click.open_file(file_name, "w")
    file.truncate(0)
    file.write(reparsed)
    app.echo_success(
        f"XML catalog file created as {file_name}."
    )


def _prepare_tree_output_id_only(iris, graphs):
    """Prepare a sorted, de-duplicated IRI list of graph imports."""
    output_iris = []
    for iri in iris:
        # get response for one requested graph
        api_response = get_graph_import_tree(iri)

        # add all imported IRIs to the IRI list
        # add the requested graph as well
        output_iris.append(iri)
        for top_graph in api_response["tree"]:
            output_iris.append(top_graph)
            for sub_graph in api_response["tree"][top_graph]:
                output_iris.append(sub_graph)

    # prepare a sorted, de-duplicated IRI list of existing graphs
    # and create a line-by-line output of it
    output_iris = sorted(
        list(set(output_iris)),
        key=lambda x: x.lower()
    )
    filtered_iris = [iri for iri in output_iris if iri in graphs]
    return "\n".join(filtered_iris[0:]) + "\n"


@click.command(cls=CmemcCommand, name="tree")
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Show tree of all (readable) graphs."
)
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON of the graph importTree API response."
)
@click.option(
    "--id-only",
    is_flag=True,
    help="Lists only graph identifier (IRIs) and no labels or other "
         "meta data. This is useful for piping the IRIs into other commands. "
         "The output with this option is a sorted, flat, de-duplicated list "
         "of existing graphs."
)
@click.argument(
    "iris",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.graph_uris
)
@click.pass_obj
def tree_command(app, all_, raw, id_only, iris):
    """Show graph tree(s) of the owl:imports hierarchy.

    You can can output one or more trees of the import hierarchy.

    Imported graphs which do not exists are shown as [missing: IRI].
    Imported graphs which will result in an import cycle are shown as
    [ignored: IRI].
    Each graph is shown with label and IRI.
    """
    graphs = get_graphs_as_dict()
    if iris == () and not all_:
        raise ValueError("Either specify at least one graph IRI or use the "
                         "--all option to show the owl:imports tree of all "
                         "graphs.")
    if all_:
        iris = graphs.keys()

    for iri in iris:
        if iri not in graphs:
            raise ValueError(UNKNOWN_GRAPH_ERROR.format(iri))

    iris = sorted(iris, key=lambda x: graphs[x]["label"]["title"].lower())

    if raw:
        for iri in iris:
            # direct output of the response for one requested graph
            app.echo_info_json(get_graph_import_tree(iri))
        return

    if id_only:
        app.echo_result(
            _prepare_tree_output_id_only(iris, graphs),
            nl=False
        )
        return

    # normal execution
    output = ""
    for iri in iris:
        # get response for on requested graph
        api_response = get_graph_import_tree(iri)

        tree = _add_tree_nodes_recursive(
            Tree(), api_response["tree"], iri, graphs
        )
        tree = _add_ignored_nodes(
            tree, api_response["ignored"]
        )

        # strip empty lines from the tree.show output
        output += os.linesep.join(
            [
                line for line
                in tree.show(key=lambda x: x.tag.lower(), stdout=False)
                .splitlines()
                if line.strip()
            ]
        )
        output += "\n"
    # result output
    app.echo_result(output, nl=False)


@click.command(cls=CmemcCommand, name="list")
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON of the graphs list API response."
)
@click.option(
    "--id-only",
    is_flag=True,
    help="Lists only graph identifier (IRIs) and no labels or other "
         "meta data. This is useful for piping the IRIs into other commands."
)
@click.option(
    "--filter", "filter_",
    type=click.Tuple([
        click.Choice(["access", 'imported-by']),
        str
    ]),
    autocompletion=completion.graph_list_filter,
    default=[None] * 2,
    help="Filter graphs based on effective access conditions or import "
         "closure. "
         "First parameter CHOICE can be 'access' or 'imported-by'. "
         "The second parameter can be 'readonly' or 'writeable' in case "
         "of 'access' or any readable graph in case of 'imported-by'."
)
@click.pass_obj
def list_command(app, raw, id_only, filter_):
    """List accessible graphs."""
    filter_name, filter_value = filter_
    graphs = _get_graphs_filtered(filter_name, filter_value)

    if raw:
        app.echo_info_json(graphs)
        return
    if id_only:
        # output a sorted list of graph IRIs
        for graph_desc in sorted(graphs, key=lambda k: k["iri"].lower()):
            app.echo_result(graph_desc["iri"])
        return
    # output a user table
    table = []
    for _ in graphs:
        if len(_["assignedClasses"]) > 0:
            graph_class = iri_to_qname(sorted(_["assignedClasses"])[0])
        else:
            graph_class = ""
        row = [
            _["iri"],
            graph_class,
            _["label"]["title"],
        ]
        table.append(row)
    app.echo_info_table(
        table,
        headers=["Graph IRI", "Type", "Label"],
        sort_column=2
    )


# pylint: disable=too-many-arguments,too-many-locals
@click.command(cls=CmemcCommand, name="export")
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Export all readable graphs."
)
@click.option(
    "--include-imports",
    is_flag=True,
    help="Export selected graph(s) and all graphs which are imported from "
         "these selected graph(s)."
)
@click.option(
    "--create-catalog",
    is_flag=True,
    help="In addition to the .ttl and .graph files, cmemc will create an "
         "XML catalog file (catalog-v001.xml) which can be used by "
         "applications such as Protégé."
)
@click.option(
    "--output-dir",
    type=click.Path(
        writable=True,
        file_okay=False
    ),
    help="Export to this directory."
)
@click.option(
    "--output-file",
    type=click.Path(
        writable=True,
        allow_dash=True,
        dir_okay=False
    ),
    default="-",
    show_default=True,
    autocompletion=completion.triple_files,
    help="Export to this file."
)
@click.option(
    "--filename-template", "-t", "template",
    default="{{hash}}",
    show_default=True,
    type=click.STRING,
    autocompletion=completion.graph_export_templates,
    help="Template for the export file name(s). "
         "Used together with --output-dir. "
         "Possible placeholders are (Jinja2): "
         "{{hash}} - sha256 hash of the graph IRI, "
         "{{iriname}} - graph IRI converted to filename, "
         "{{connection}} - from the --connection option and "
         "{{date}} - the current date as YYYY-MM-DD. "
         "The file suffix will be appended. "
         "Needed directories will be created."
)
@click.option(
    "--mime-type",
    default="application/n-triples",
    show_default=True,
    type=click.Choice(["application/n-triples", "text/turtle"]),
    help="Define the requested mime type"
)
@click.argument(
    "iris",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.graph_uris
)
@click.pass_obj
def export_command(
        app, all_, include_imports, create_catalog,
        output_dir, output_file, template, mime_type, iris
):
    """Export graph(s) as NTriples to stdout (-), file or directory.

    In case of file export, data from all selected graphs will be concatenated
    in one file.
    In case of directory export, .graph and .ttl files will be created
    for each graph.
    """
    iris = _check_and_extend_exported_graphs(
        iris, all_, include_imports, get_graphs_as_dict()
    )

    count: int = len(iris)
    current: int = 1
    app.echo_debug("graph count is " + str(count))
    if output_dir:
        # output directory set
        app.echo_debug("output is directory")
        # pre-calculate all filenames with the template,
        # in order to output errors on naming clashes as early as possible
        _names = _get_export_names(app, iris, template)
        # create directory
        if not os.path.exists(output_dir):
            app.echo_warning("Output directory does not exist: "
                             + "will create it.")
            os.makedirs(output_dir)
        # one .graph, one .ttl file per named graph
        for iri in iris:
            # join with given output directory and normalize full path
            triple_file_name = os.path.normpath(
                os.path.join(output_dir, _names[iri])
            )
            graph_file_name = triple_file_name + ".graph"
            # output directory is created lazy
            Path(
                os.path.dirname(triple_file_name)
            ).mkdir(parents=True, exist_ok=True)
            # create and write the .ttl.graph meta data file
            graph_file = click.open_file(graph_file_name, "w")
            graph_file.write(iri + "\n")
            _get_graph_to_file(
                iri, triple_file_name,
                app,
                numbers=(current, count),
                mime_type=mime_type
            )
            current = current + 1
        if create_catalog:
            _create_xml_catalog_file(app, _names, output_dir)
    else:
        # no output directory set -> file export
        if output_file == "-":
            # in case a file is stdout,
            # all triples from all graphs go in and other output is suppressed
            app.echo_debug("output is stdout")
            for iri in iris:
                _get_graph_to_file(iri, output_file, app, mime_type=mime_type)
        else:
            # in case a file is given, all triples from all graphs go in
            app.echo_debug("output is file")
            for iri in iris:
                _get_graph_to_file(
                    iri, output_file,
                    app,
                    numbers=(current, count),
                    overwrite=False,
                    mime_type=mime_type
                )
                current = current + 1


@click.command(cls=CmemcCommand, name="import")  # noqa: C901
@click.option(
    "--replace",
    is_flag=True,
    help="Replace / overwrite the graph - instead of just adding new triples "
         "the graph."
)
@click.option(
    "--skip-existing",
    is_flag=True,
    help="Skip importing a file if the target graph already exists in "
         "the store. Note that the graph list is fetched once at the "
         "beginning of the process, so that you can still add multiple "
         "files to one single graph (if it does not exist)."
)
@click.argument(
    "input_path",
    required=True,
    autocompletion=completion.triple_files,
    type=click.Path(
        allow_dash=False,
        readable=True
    )
)
@click.argument(
    "iri",
    type=click.STRING,
    required=False,
    autocompletion=completion.graph_uris
)
@click.pass_obj
def import_command(app, input_path, replace, skip_existing, iri):
    """Import graph(s) to the store.

    If input is an directory, it scans for file-pairs such as xxx.ttl and
    xxx.ttl.graph where xxx.ttl is the actual triples file and xxx.ttl.graph
    contains the graph IRI as one string: "https://mygraph.de/xxx/".
    If input is a file, content will be uploaded to IRI.
    If --replace is set, the data will be overwritten,
    if not, it will be added.
    """
    # is an array of tuples like this [('path/to/triple.file', 'graph IRI')]
    if replace and skip_existing:
        raise ValueError(
            "The options --replace and --skip-existing are mutually "
            "exclusive, so please remove one of them."
        )
    graphs: list
    if os.path.isdir(input_path):
        if iri is not None:
            raise ValueError("Either specify an input file AND a graph IRI "
                             + "or an input directory ONLY.")
        # in case a directory is the source,
        # the graph/nt file structure is crawled
        graphs = read_rdf_graph_files(input_path)
    elif os.path.isfile(input_path):
        if iri is None:
            raise ValueError("Either specify an input file AND a graph IRI "
                             + "or an input directory ONLY.")
        graphs = [(input_path, iri)]
    else:
        # TODO: support for stdin stream
        raise NotImplementedError(
            "Input from special files "
            + "(socket, FIFO, device file) is not supported."
        )

    existing_graphs = get_graphs_as_dict()
    processed_graphs: set = set()
    count: int = len(graphs)
    current: int = 1
    for (triple_file, graph_iri) in graphs:
        app.echo_info(
            f"Import file {current}/{count}: "
            f"{graph_iri} from {triple_file} ... ",
            nl=False
        )
        if graph_iri in existing_graphs and skip_existing:
            app.echo_warning("skipped")
            continue
        # prevents re-replacing of graphs in a single run
        _replace = False if graph_iri in processed_graphs else replace
        graph_api.post_streamed(graph_iri, triple_file, replace=_replace)
        app.echo_success("replaced" if _replace else "added")
        # refresh access conditions in case of dropped AC graph
        if graph_iri == refresh.AUTHORIZATION_GRAPH_URI:
            refresh.get()
            app.echo_debug("Access conditions refreshed.")
        processed_graphs.add(graph_iri)
        current += 1


@click.command(cls=CmemcCommand, name="delete")
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Delete all writeable graphs."
)
@click.option(
    "--include-imports",
    is_flag=True,
    help="Delete selected graph(s) and all writeable graphs which are "
         "imported from these selected graph(s)."
)
@click.argument(
    "iris",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.writable_graph_uris
)
@click.pass_obj
def delete_command(app, all_, include_imports, iris):
    """Delete graph(s) from the store."""
    graphs = get_graphs_as_dict(writeable=True, readonly=False)
    iris = _check_and_extend_exported_graphs(
        iris, all_, include_imports, graphs
    )

    count: int = len(iris)
    current: int = 1
    for iri in iris:
        app.echo_info(
            f"Drop graph {current}/{count}: {iri} ... ",
            nl=False
        )
        graph_api.delete(iri)
        app.echo_success("done")
        # refresh access conditions in case of dropped AC graph
        if iri == refresh.AUTHORIZATION_GRAPH_URI:
            refresh.get()
            app.echo_debug("Access conditions refreshed.")
        current = current + 1


@click.command(cls=CmemcCommand, name="open")
@click.argument(
    "iri",
    type=click.STRING,
    autocompletion=completion.graph_uris
)
@click.pass_obj
def open_command(app, iri):
    """Open / explore a graph in the browser."""
    explore_uri = get_cmem_base_uri() + "/explore?graph=" + quote(iri)
    click.launch(explore_uri)
    app.echo_debug(explore_uri)


@click.command(cls=CmemcCommand, name="count")
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Count all graphs"
)
@click.option(
    "-s", "--summarize",
    is_flag=True,
    help="Display only a sum of all counted graphs together"
)
@click.argument(
    "iris",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.graph_uris
)
@click.pass_obj
def count_command(app, all_, summarize, iris):
    """Count triples in graph(s).

    This command lists graphs with their triple count.
    Counts are done without following imported graphs.
    """
    if iris == () and not all_:
        raise ValueError("Either specify at least one graph IRI "
                         + "or use the --all option to count all graphs.")
    if all_:
        # in case --all is given,
        # list of graphs is filled with all available graph IRIs
        iris = (
            [iri["iri"] for iri in get_graphs()]
        )

    count: int
    overall_sum: int = 0
    current: int = 1
    for iri in iris:
        count = count_graph(iri)
        overall_sum = overall_sum + count
        current = current + 1
        if not summarize:
            app.echo_result(f"{str(count)} {iri}")
    if summarize:
        app.echo_result(overall_sum)


@click.group(cls=CmemcGroup)
def graph():
    """List, import, export, delete, count, tree or open graphs.

    Graphs are identified by an IRI. The get a list of existing graphs,
    execute the list command or use tab-completion.
    """


graph.add_command(count_command)
graph.add_command(tree_command)
graph.add_command(list_command)
graph.add_command(export_command)
graph.add_command(delete_command)
graph.add_command(import_command)
graph.add_command(open_command)
