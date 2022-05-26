"""vocabularies commands for cmem command line interface."""
from datetime import date

from six.moves.urllib.parse import quote

import click

from rdflib import Graph
from rdflib.plugins.parsers.notation3 import BadSyntax

from cmem.cmemc.cli import completion
from cmem.cmemc.cli.commands import CmemcCommand, CmemcGroup
from cmem.cmempy.config import get_cmem_base_uri
from cmem.cmempy.dp.proxy import graph as graph_api
from cmem.cmempy.dp.titles import resolve
from cmem.cmempy.queries import SparqlQuery
from cmem.cmempy.vocabularies import (
    get_global_vocabs_cache,
    get_vocabularies,
    install_vocabulary,
    uninstall_vocabulary
)
from cmem.cmempy.workspace import (
    reload_prefixes,
    update_global_vocabulary_cache
)

GET_ONTOLOGY_IRI_QUERY = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?iri
WHERE {
    ?iri a owl:Ontology;
}
"""

GET_PREFIX_DECLARATION = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX vann: <http://purl.org/vocab/vann/>
SELECT DISTINCT ?prefix ?namespace
WHERE {{
    <{}> a owl:Ontology;
        vann:preferredNamespacePrefix ?prefix;
        vann:preferredNamespaceUri ?namespace.
}}
"""

INSERT_CATALOG_ENTRY = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX voaf: <http://purl.org/vocommons/voaf#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX vann: <http://purl.org/vocab/vann/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
WITH <https://ns.eccenca.com/example/data/vocabs/>
INSERT {{
    <{iri}> a voaf:Vocabulary ;
        skos:prefLabel "{label}"{language} ;
        rdfs:label "{label}"{language} ;
        dct:description "{description}" ;
        vann:preferredNamespacePrefix "{prefix}" ;
        vann:preferredNamespaceUri "{namespace}" ;
        dct:modified "{date}"^^xsd:date .
}}
WHERE {{}}
"""


def _insert_catalog_entry(iri, prefix, namespace, label, language=None):
    """Insert a cmem vocabulary catalog entry.

    This executes an INSERT WHERE query to the vocabulary catalog graph in
    order to list the new vocabulary graph as vocab in the catalog.

    Args:
        iri (str): The IRI of the vocabulary graph.
        prefix (str): The prefix of the vocabulary.
        namespace (str): The namespace IRI of the vocabulary.
        label (str): The title of the vocabulary to add to the entry.
        language (str): Optional language tag of the title.

    Returns:
        None
    """
    if "@" + str(language).strip() != "@":
        language = "@" + str(language).strip()
    else:
        language = ""

    if not label.startswith(prefix + ":"):
        label = prefix + ": " + label

    query_text = INSERT_CATALOG_ENTRY.format(
        iri=iri,
        prefix=prefix,
        namespace=namespace,
        date=date.today().strftime("%Y-%m-%d"),
        label=label,
        language=language,
        description="vocabulary imported with cmemc"
    )
    query = SparqlQuery(text=query_text, origin="cmemc")
    query.get_results()


def _get_vocabulary_metadata_from_file(file):
    """Get potential graph iri and prefix/namespace from a turtle file."""
    metadata = {
        "iri": None,
        "prefix": None,
        "namespace": None
    }
    try:
        graph = Graph().parse(file, format="ttl")
    except BadSyntax as error:
        raise ValueError(
            "File {file} could not be parsed as turtle."
        ) from error

    ontology_iris = graph.query(GET_ONTOLOGY_IRI_QUERY)
    if len(ontology_iris) == 0:
        raise ValueError(
            "There is no owl:Ontology resource described "
            "in the turtle file."
        )
    if len(ontology_iris) > 1:
        ontology_iris_str = [str(iri[0]) for iri in ontology_iris]
        raise ValueError(
            "There are more than one owl:Ontology resources described "
            f"in the turtle file: {ontology_iris_str}"
        )
    iri = str(next(iter(ontology_iris))[0])
    metadata["iri"] = iri
    vann_data = graph.query(GET_PREFIX_DECLARATION.format(iri))
    if len(vann_data) == 0:
        raise ValueError(
            "There is no namespace defined "
            f"for the ontology '{iri}'.\n"
            "Please add a prefix and namespace to the sources.\n"
            "Refer to the documentation at "
            "https://vocab.org/vann/ for more information."
        )
    if len(vann_data) > 1:
        raise ValueError(
            "There is more than one vann namespace defined "
            f"for the ontology: {iri}"
        )
    namespace = next(iter(vann_data))
    metadata["prefix"] = str(namespace[0])
    metadata["namespace"] = str(namespace[1])
    return metadata


def _transform_cache_to_table(cache_category, table):
    """Transform a cache category dict to a tabulate table."""
    for item in cache_category:
        uri = item["genericInfo"]["uri"]
        try:
            label = item["genericInfo"]["label"]
        except KeyError:
            label = ""
        row = [uri, "class", label]
        table.append(row)
    return table


@click.command(cls=CmemcCommand, name="open")
@click.argument(
    "iri",
    type=click.STRING,
    autocompletion=completion.installed_vocabularies
)
@click.pass_obj
def open_command(app, iri):
    """Open / explore a vocabulary graph in the browser.

    Vocabularies are identified by their graph IRI.
    Installed vocabularies can be listed with the "vocabulary list" command.
    """
    explore_uri = get_cmem_base_uri() + "/explore?graph=" + quote(iri)
    click.launch(explore_uri)
    app.echo_debug(explore_uri)


@click.command(cls=CmemcCommand, name="list")
@click.option(
    "--id-only",
    is_flag=True,
    help="Lists only vocabulary identifier (IRIs) and no labels or other "
         "meta data. This is useful for piping the ids into other cmemc "
         "commands."
)
@click.option(
    "--filter", "filter_",
    type=click.Choice(
        ["all", "installed", "installable"],
        case_sensitive=True
    ),
    default="installed",
    show_default=True,
    help="Filter list based on status."
)
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON."
)
@click.pass_obj
def list_command(app, id_only, filter_, raw):
    """Output a list of vocabularies.

    Vocabularies are graphs (see 'cmemc graph' command group) which consists
    of class and property descriptions.
    """
    vocabs = get_vocabularies(filter_=filter_)
    if raw:
        app.echo_info_json(vocabs)
    elif id_only:
        for _ in vocabs:
            app.echo_info(_["iri"])
    else:
        table = []
        for _ in vocabs:
            iri = _["iri"]
            try:
                label = _["label"]["title"]
            except (KeyError, TypeError):
                if _["vocabularyLabel"]:
                    label = _["vocabularyLabel"]
                else:
                    label = "[no label given]"
            table.append((iri, label))
        app.echo_info_table(
            table,
            headers=["Vocabulary Graph IRI", "Label"],
            sort_column=1
        )


@click.command(cls=CmemcCommand, name="install")
@click.argument(
    "iris",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.installable_vocabularies
)
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Install all vocabularies from the catalog."
)
@click.pass_obj
def install_command(app, iris, all_):
    """Install one or more vocabularies from the catalog.

    Vocabularies are identified by their graph IRI.
    Installable vocabularies can be listed with the
    "vocabulary list --filter installable" command.
    """
    if iris == () and not all_:
        raise ValueError("Either specify at least one vocabulary "
                         + "IRI or use the --all option to install all "
                           "vocabularies from the catalog.")
    if all_:
        iris = (
            [iri["iri"] for iri in get_vocabularies(filter_="installable")]
        )
    count: int = len(iris)
    current: int = 1
    for iri in iris:
        app.echo_info(
            f"Install vocabulary {current}/{count}: {iri} ... ",
            nl=False
        )
        install_vocabulary(iri)
        app.echo_success("done")
        current = current + 1


@click.command(cls=CmemcCommand, name="uninstall")
@click.argument(
    "iris",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.installed_vocabularies
)
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Uninstall all installed vocabularies."
)
@click.pass_obj
def uninstall_command(app, iris, all_):
    """Uninstall one or more vocabularies.

    Vocabularies are identified by their graph IRI.
    Already installed vocabularies can be listed with the
    "vocabulary list --filter installed" command.
    """
    if iris == () and not all_:
        raise ValueError("Either specify at least one vocabulary "
                         + "IRI or use the --all option to uninstall all "
                           "installed vocabularies.")
    if all_:
        iris = (
            [iri["iri"] for iri in get_vocabularies(filter_="installed")]
        )
    count: int = len(iris)
    current: int = 1
    for iri in iris:
        app.echo_info(
            f"Uninstall vocabulary {current}/{count}: {iri} ... ",
            nl=False
        )
        uninstall_vocabulary(iri)
        app.echo_success("done")
        current = current + 1


@click.command(cls=CmemcCommand, name="import")
@click.argument(
    "FILE",
    required=True,
    autocompletion=completion.triple_files,
    type=click.Path(
        allow_dash=False,
        readable=True
    )
)
@click.option(
    "--replace",
    is_flag=True,
    help="Replace (overwrite) existing vocabulary, if present."
)
@click.pass_obj
def import_command(app, file, replace):
    """Import a turtle file as a vocabulary.

    With this command, you can import a local ontology file as a named graph.
    and create a corresponding vocabulary catalog entry.

    The uploaded ontology file is analysed locally in order to discover the
    named graph and the prefix declaration. This requires an OWL ontology
    description which correctly uses the vann:preferredNamespacePrefix and
    vann:preferredNamespaceUri properties.
    """
    # fetch meta data
    meta_data = _get_vocabulary_metadata_from_file(file)
    iri = meta_data["iri"]
    prefix = meta_data["prefix"]
    namespace = meta_data["namespace"]

    success_message = "done"
    if iri in [_["iri"] for _ in graph_api.get_graphs_list()]:
        if replace:
            success_message = "replaced"
        else:
            raise ValueError(
                f"Proposed graph {iri} does already exist."
            )
    app.echo_info(
        f"Import {file} as vocabulary to {iri} ... ",
        nl=False
    )
    # upload graph
    graph_api.post(iri, file, replace=True)

    # resolve label
    resolved_label_object = resolve([iri], graph=iri)[iri]
    label = resolved_label_object["title"]
    language = resolved_label_object["lang"]
    app.echo_debug(resolved_label_object)

    # insert catalog entry
    _insert_catalog_entry(
        iri=iri,
        prefix=prefix,
        namespace=namespace,
        label=label,
        language=language
    )
    # reload DI prefix
    reload_prefixes()
    # update cache
    update_global_vocabulary_cache(iri)
    app.echo_success(success_message)


@click.command(cls=CmemcCommand, name="update")
@click.argument(
    "iris",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.installed_vocabularies
)
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Update cache for all installed vocabularies."
)
@click.pass_obj
def cache_update_command(app, iris, all_):
    """Reload / updates the data integration cache for a vocabulary."""
    if iris == () and not all_:
        raise ValueError("Either specify at least one vocabulary "
                         + "IRI or use the --all option to update the "
                           "cache for all installed vocabularies.")
    if all_:
        iris = (
            [iri["iri"] for iri in get_vocabularies(filter_="installed")]
        )
    count: int = len(iris)
    current: int = 1
    for iri in iris:
        app.echo_info(
            f"Update cache {current}/{count}: {iri} ... ",
            nl=False
        )
        update_global_vocabulary_cache(iri)
        app.echo_success("done")
        current = current + 1


@click.command(cls=CmemcCommand, name="list")
@click.option(
    "--id-only",
    is_flag=True,
    help="Lists only vocabulary term identifier (IRIs) and no labels or other "
         "meta data. This is useful for piping the ids into other cmemc "
         "commands."
)
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON."
)
@click.pass_obj
def cache_list_command(app, id_only, raw):
    """Output the content of the global vocabulary cache."""
    cache_ = get_global_vocabs_cache()
    if raw:
        app.echo_info_json(cache_)
    elif id_only:
        for vocab in cache_["vocabularies"]:
            for class_ in vocab["classes"]:
                app.echo_info(class_["genericInfo"]["uri"])
            for property_ in vocab["properties"]:
                app.echo_info(property_["genericInfo"]["uri"])
    else:
        table = []
        for vocab in cache_["vocabularies"]:
            table = _transform_cache_to_table(vocab["classes"], table)
            table = _transform_cache_to_table(vocab["properties"], table)
        app.echo_info_table(
            table,
            headers=["IRI", "Type", "Label"],
            sort_column=0
        )


@click.group(cls=CmemcGroup)
def cache():
    """List und update the vocabulary cache."""


cache.add_command(cache_update_command)
cache.add_command(cache_list_command)


@click.group(cls=CmemcGroup)
def vocabulary():
    """List, (un-)install, import or open vocabs / manage cache."""


vocabulary.add_command(open_command)
vocabulary.add_command(list_command)
vocabulary.add_command(install_command)
vocabulary.add_command(uninstall_command)
vocabulary.add_command(import_command)
vocabulary.add_command(cache)
