"""Utility functions for CLI auto-completion functionality."""
# pylint: disable=unused-argument, broad-except
import os

from natsort import natsorted, ns

from prometheus_client.parser import text_string_to_metric_families

from cmem.cmemc.cli.context import CONTEXT
from cmem.cmemc.cli.utils import (
    get_graphs,
    metric_get_labels,
    metrics_get_dict
)
from cmem.cmempy.dp.admin import get_prometheus_data
from cmem.cmempy.plugins.marshalling import get_marshalling_plugins
from cmem.cmempy.queries import QUERY_CATALOG
from cmem.cmempy.vocabularies import get_vocabularies
from cmem.cmempy.workflow.workflows import get_workflows_io
from cmem.cmempy.workspace import (
    get_task_plugin_description,
    get_task_plugins,
)
from cmem.cmempy.workspace.projects.project import get_projects
from cmem.cmempy.workspace.projects.resources import get_all_resources
from cmem.cmempy.workspace.python import list_packages
from cmem.cmempy.workspace.search import list_items

SORT_BY_KEY = 0
SORT_BY_DESC = 1


def _finalize_completion(
        candidates: list,
        incomplete: str = '',
        sort_by: int = SORT_BY_KEY,
        nat_sort: bool = False
) -> list:
    """Sort and filter candidates list.

    candidates are sorted with natsort library by sort_by key.

    Args:
        candidates (list):  completion dictionary to filter
        incomplete (str):   incomplete string at the cursor
        sort_by (str):      SORT_BY_KEY or SORT_BY_DESC
        nat_sort (bool):    if true, uses the natsort package for sorting

    Returns:
        filtered and sorted candidates list

    Raises:
        ValueError in case of wrong sort_by parameter
    """
    if sort_by not in (SORT_BY_KEY, SORT_BY_DESC):
        raise ValueError("sort_by should be 0 or 1.")
    incomplete = incomplete.lower()
    if len(candidates) == 0:
        return candidates
    # remove duplicates
    candidates = list(set(candidates))

    if isinstance(candidates[0], str):
        # list of strings filtering and sorting
        filtered_candidates = [
            element for element in candidates
            if element.lower().find(incomplete) != -1
        ]
        if nat_sort:
            return natsorted(
                seq=filtered_candidates,
                alg=ns.IGNORECASE
            )
        # this solves that case-insensitive sorting is not stable in ordering
        # of "equal" keys (https://stackoverflow.com/a/57923460)
        return sorted(
            filtered_candidates,
            key=lambda x: (x.casefold(), x)
        )
    if isinstance(candidates[0], tuple):
        # list of tuples filtering and sorting
        filtered_candidates = [
            element for element in candidates
            if element[0].lower().find(incomplete) != -1
            or element[1].lower().find(incomplete) != -1
        ]
        if nat_sort:
            return natsorted(
                seq=filtered_candidates,
                key=lambda k: k[sort_by],
                alg=ns.IGNORECASE
            )
        return sorted(
            filtered_candidates,
            key=lambda x: (x[sort_by].casefold(), x[sort_by])
        )
    raise ValueError(
        "candidates should be a list of strings or a list of tuples."
    )


def add_metadata_parameter(list_=None):
    """Extend a list with metadata keys and key descriptions."""
    if list_ is None:
        list_ = []
    list_.insert(
        0,
        ("description", "Metadata: A description.")
    )
    list_.insert(
        0,
        ("label", "Metadata: A name.")
    )
    return list_


def dataset_parameter(ctx, args, incomplete):
    """Prepare a list of dataset parameter for a dataset type."""
    CONTEXT.set_connection_from_args(args)
    incomplete = incomplete.lower()
    # look if cursor is in value position of the -p option and
    # return nothing in case it is (values are not completed atm)
    if args[len(args) - 2] in ("-p", "--parameter"):
        return []
    # try to determine the dataset type
    dataset_type = None
    for num, arg in enumerate(args):
        if arg == "--type":
            dataset_type = args[num + 1]
    # without type, we know nothing
    if dataset_type is None:
        return []
    plugin = get_task_plugin_description(dataset_type)
    properties = plugin["properties"]
    options = []
    for key in properties:
        title = properties[key]["title"]
        description = properties[key]["description"]
        option = f"{title}: {description}"
        options.append((key, option))
    # sorting: metadata on top, then parameter per key
    options = sorted(options, key=lambda k: k[0].lower())
    options = add_metadata_parameter(options)
    # restrict to search
    options = [
        key for key in options
        if (key[0].lower().find(incomplete.lower()) != -1
            or key[1].lower().find(incomplete.lower()) != -1
            )
    ]
    return options


def dataset_types(ctx, args, incomplete):
    """Prepare a list of dataset types."""
    CONTEXT.set_connection_from_args(args)
    incomplete = incomplete.lower()
    options = []
    plugins = get_task_plugins()
    for plugin_id in plugins:
        plugin = plugins[plugin_id]
        title = plugin["title"]
        description = plugin["description"].partition("\n")[0]
        option = f"{title}: {description}"
        if plugin["taskType"] == "Dataset" and (
                plugin_id.lower().find(incomplete.lower()) != -1
                or option.lower().find(incomplete.lower()) != -1):
            options.append(
                (
                    plugin_id,
                    option
                )
            )
    options = sorted(options, key=lambda k: k[1].lower())
    return options


def dataset_ids(ctx, args, incomplete):
    """Prepare a list of projectid:datasetid dataset identifier."""
    CONTEXT.set_connection_from_args(args)
    options = []
    results = list_items(item_type="dataset")
    datasets = results["results"]
    for _ in datasets:
        options.append(
            (
                _["projectId"] + r"\:" + _["id"],
                _["label"]
            )
        )
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_DESC
    )


def resource_ids(ctx, args, incomplete):
    """Prepare a list of projectid:resourceid resource identifier."""
    CONTEXT.set_connection_from_args(args)
    options = []
    for _ in get_all_resources():
        options.append(
            (
                _["id"]
            )
        )
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_DESC
    )


def scheduler_ids(ctx, args, incomplete):
    """Prepare a list of projectid:schedulerid scheduler identifier."""
    CONTEXT.set_connection_from_args(args)
    options = []
    schedulers = list_items(
        item_type="task",
        facets=[{
            "facetId": "taskType",
            "keywordIds": ["Scheduler"],
            "type": "keyword"
        }]
    )["results"]
    for _ in schedulers:
        if _["projectId"] + ":" + _["id"] in args:
            continue
        options.append(
            (
                _["projectId"] + r"\:" + _["id"],
                _["label"]
            )
        )
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_DESC
    )


def metric_ids(ctx, args, incomplete):
    """Prepare a list of metric identifier."""
    CONTEXT.set_connection_from_args(args)
    options = []

    data = get_prometheus_data().text
    for family in text_string_to_metric_families(data):
        options.append(
            (
                family.name,
                family.documentation
            )
        )
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_KEY
    )


def metric_label_filter(ctx, args, incomplete):
    """Prepare a list of label name or values."""
    # TODO: this completion does not take care of the --job option
    CONTEXT.set_connection_from_args(args)
    incomplete = incomplete.lower()
    options = []
    metric_id = args[3]
    labels = metric_get_labels(metrics_get_dict()[metric_id])
    if args[len(args) - 1] in "--filter":
        # we are in the name position
        options = labels.keys()
    if args[len(args) - 2] in "--filter":
        label_name = args[len(args) - 1]
        # we are in the value position
        options = labels[label_name]
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_KEY
    )


def vocabularies(ctx, args, incomplete, filter_="all"):
    """Prepare a list of vocabulary graphs for auto-completion."""
    CONTEXT.set_connection_from_args(args)
    options = []
    try:
        vocabs = get_vocabularies(filter_=filter_)
    except Exception:
        # if something went wrong, die silently
        return []
    for _ in vocabs:
        url = _["iri"]
        if url in args:
            continue
        url = _["iri"].replace(":", r"\:")
        try:
            label = _["label"]["title"]
        except (KeyError, TypeError):
            label = "Vocabulary in graph " + url
        options.append((url, label))
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_DESC
    )


def installed_vocabularies(ctx, args, incomplete):
    """Prepare a list of installed vocabulary graphs."""
    return vocabularies(ctx, args, incomplete, filter_="installed")


def installable_vocabularies(ctx, args, incomplete):
    """Prepare a list of installable vocabulary graphs."""
    return vocabularies(ctx, args, incomplete, filter_="installable")


def file_list(incomplete="", suffix="", description=""):
    """Prepare a list of files with specific parameter."""
    if os.path.isdir(incomplete):
        # given string is a directory, so we scan this directory and
        # add it as a prefix
        directory = incomplete
        incomplete = ""
        prefix = os.path.realpath(incomplete) + "/"
    else:
        # given string is NOT a directory so we just scan the current
        # directory
        directory = os.getcwd()
        prefix = ""
    options = []
    for file_name in os.listdir(directory):
        if os.path.isfile(file_name) \
                and file_name.endswith(suffix):
            options.append((prefix + file_name, description))
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_KEY
    )


def workflow_io_ids(ctx, args, incomplete):
    """Prepare a list of io workflows."""
    CONTEXT.set_connection_from_args(args)
    options = []
    for _ in get_workflows_io():
        workflow_id = _["projectId"] + r"\:" + _["id"]
        label = _["label"]
        options.append((workflow_id, label))
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_DESC
    )


def replay_files(ctx, args, incomplete):
    """Prepare a list of JSON replay files."""
    return file_list(
        incomplete=incomplete,
        suffix=".json",
        description="JSON query replay file"
    )


def installed_package_names(ctx, args, incomplete):
    """Prepare a list of installed packages."""
    CONTEXT.set_connection_from_args(args)
    options = []
    packages = list_packages()
    for _ in packages:
        options.append(
            (
                _["name"],
                _["version"]
            )
        )
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_DESC
    )


def python_package_files(ctx, args, incomplete):
    """Prepare a list of acceptable python package files."""
    return file_list(
        incomplete=incomplete,
        suffix=".tar.gz",
        description="Potential Python Package file"
    ) + file_list(
        incomplete=incomplete,
        suffix=".whl",
        description="WHL Python Package file"
    )


def workflow_io_input_files(ctx, args, incomplete):
    """Prepare a list of acceptable workflow io input files."""
    return file_list(
        incomplete=incomplete,
        suffix=".csv",
        description="CSV Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".xml",
        description="XML Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".json",
        description="JSON Dataset resource"
    )


def workflow_io_output_files(ctx, args, incomplete):
    """Prepare a list of acceptable workflow io output files."""
    return file_list(
        incomplete=incomplete,
        suffix=".csv",
        description="CSV Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".xml",
        description="XML Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".json",
        description="JSON Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".xlsx",
        description="Excel Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".ttl",
        description="RDF file Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".nt",
        description="RDF file Dataset resource"
    )


def dataset_files(ctx, args, incomplete):
    """Prepare a list of SPARQL files."""
    return file_list(
        incomplete=incomplete,
        suffix=".csv",
        description="CSV Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".xlsx",
        description="Excel Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".xml",
        description="XML Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".json",
        description="JSON Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".ttl",
        description="RDF file Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".zip",
        description="multiCsv Dataset resource"
    ) + file_list(
        incomplete=incomplete,
        suffix=".orc",
        description="Apache ORC Dataset resource"
    )


def graph_backup_files(ctx, args, incomplete):
    """Prepare a list of workspace files."""
    return file_list(
        incomplete=incomplete,
        suffix=".graphs.zip",
        description="eccenca Corporate Memory graph backup file"
    )


def project_files(ctx, args, incomplete):
    """Prepare a list of workspace files."""
    return file_list(
        incomplete=incomplete,
        suffix=".project.zip",
        description="eccenca Corporate Memory project backup file"
    )


def ini_files(ctx, args, incomplete):
    """Prepare a list of workspace files."""
    return file_list(
        incomplete=incomplete,
        suffix=".ini",
        description="INI file"
    )


def workspace_files(ctx, args, incomplete):
    """Prepare a list of workspace files."""
    return file_list(
        incomplete=incomplete,
        suffix=".workspace.zip",
        description="eccenca Corporate Memory workspace backup file"
    )


def sparql_files(ctx, args, incomplete):
    """Prepare a list of SPARQL files."""
    return file_list(
        incomplete=incomplete,
        suffix=".sparql",
        description="SPARQL query file"
    ) + file_list(
        incomplete=incomplete,
        suffix=".rq",
        description="SPARQL query file"
    )


def triple_files(ctx, args, incomplete):
    """Prepare a list of triple files."""
    return file_list(
        incomplete=incomplete,
        suffix=".ttl",
        description="RDF Turtle file"
    ) + file_list(
        incomplete=incomplete,
        suffix=".nt",
        description="RDF NTriples file"
    )


def placeholder(ctx, args, incomplete):
    """Prepare a list of placeholder from the to-be executed queries."""
    # look if cursor is in value position of the -p option and
    # return nothing in case it is (values are not completed atm)
    if args[len(args) - 2] in ("-p", "--parameter"):
        return []
    # setup configuration
    CONTEXT.set_connection_from_args(args)
    # extract placeholder from given queries in the command line
    options = []
    for num, arg in enumerate(args):
        query = QUERY_CATALOG.get_query(arg)
        if query is not None:
            options.extend(
                list(query.get_placeholder_keys())
            )
    # look for already given parameter in the arguments and remove them from
    # the available options
    for num, arg in enumerate(args):
        if num - 1 > 0 and args[num - 1] in ("-p", "--parameter"):
            options.remove(arg)
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete
    )


def remote_queries(ctx, args, incomplete):
    """Prepare a list of query URIs."""
    CONTEXT.set_connection_from_args(args)
    options = []
    for _, query in QUERY_CATALOG.get_queries().items():
        url = query.short_url.replace(":", r"\:")
        label = query.label
        options.append((url, label))
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_DESC
    )


def remote_queries_and_sparql_files(ctx, args, incomplete):
    """Prepare a list of named queries, query files and directories."""
    remote = remote_queries(ctx, args, incomplete)
    files = sparql_files(ctx, args, incomplete)
    return remote + files


def workflow_ids(ctx, args, incomplete):
    """Prepare a list of projectid:taskid workflow identifier."""
    CONTEXT.set_connection_from_args(args)
    workflows = list_items(item_type="workflow")["results"]
    options = []
    for _ in workflows:
        workflow = _["projectId"] + ":" + _["id"]
        label = _["label"]
        if workflow in args:
            continue
        options.append((workflow.replace(":", r"\:"), label))
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_DESC
    )


def marshalling_plugins(ctx, args, incomplete):
    """Prepare a list of supported workspace/project import/export plugins."""
    CONTEXT.set_connection_from_args(args)
    options = get_marshalling_plugins()
    if "description" in options[0].keys():
        return [(_["id"], _["description"]) for _ in options]
    # in case, no descriptions are available, labels are fine as well
    return [(_["id"], _["label"]) for _ in options]


def project_ids(ctx, args, incomplete):
    """Prepare a list of project IDs for auto-completion."""
    CONTEXT.set_connection_from_args(args)
    try:
        projects = get_projects()
    except Exception:
        # if something went wrong, die silently
        return []
    options = []
    for _ in projects:
        project_id = _["name"]
        label = _["metaData"]["label"]
        # do not add project if already in the command line
        if project_id in args:
            continue
        options.append((project_id, label))
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_DESC
    )


def graph_uris(ctx, args, incomplete, writeable=True, readonly=True):
    """Prepare a list of graphs for auto-completion."""
    CONTEXT.set_connection_from_args(args)
    try:
        graphs = get_graphs()
    except Exception:
        # if something went wrong, die silently
        return []
    options = []
    for _ in graphs:
        iri = _["iri"]
        label = _["label"]["title"]
        # do not add graph if already in the command line
        if iri in args:
            continue
        options.append((iri.replace(":", r"\:"), label))
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete,
        sort_by=SORT_BY_DESC
    )


def writable_graph_uris(ctx, args, incomplete):
    """Prepare a list of writable graphs for auto-completion."""
    return graph_uris(ctx, args, incomplete, writeable=True, readonly=False)


def connections(ctx, args, incomplete):
    """Prepare a list of config connections for auto-completion."""
    # since ctx does not have an obj here, we re-create the object
    CONTEXT.set_connection_from_args(args)
    options = []
    for section in CONTEXT.config.sections():
        options.append(section)
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete
    )


def graph_export_templates(ctx, args, incomplete):
    """Prepare a list of example templates for the graph export command."""
    examples = [
        (
            "{{hash}}",
            "Example: 6568a[...]00b08.ttl"
        ),
        (
            "{{iriname}}",
            "Example: https__ns_eccenca_com_data_config.ttl"
        ),
        (
            "{{date}}-{{iriname}}",
            "Example: 2021-11-29-https__ns_eccenca_com_data_config.ttl"
        ),
        (
            "{{date}}-{{connection}}-{{iriname}}",
            "Example: 2021-11-29-mycmem-https__ns_eccenca_com_data_config.ttl"
        ),
    ]
    return _finalize_completion(
        candidates=examples,
        incomplete=incomplete
    )


def project_export_templates(ctx, args, incomplete):
    """Prepare a list of example templates for the project export command."""
    examples = [
        (
            "{{id}}",
            "Example: a plain file name"
        ),
        (
            "{{date}}-{{connection}}-{{id}}.project",
            "Example: a more descriptive file name"),
        (
            "dumps/{{connection}}/{{id}}/{{date}}.project",
            "Example: a whole directory tree"
        )
    ]
    return _finalize_completion(
        candidates=examples,
        incomplete=incomplete
    )


def workspace_export_templates(ctx, args, incomplete):
    """Prepare a list of example templates for the workspace export command."""
    examples = [
        (
            "workspace",
            "Example: a plain file name"
        ),
        (
            "{{date}}-{{connection}}.workspace",
            "Example: a more descriptive file name"),
        (
            "dumps/{{connection}}/{{date}}.workspace",
            "Example: a whole directory tree"
        )
    ]
    return _finalize_completion(
        candidates=examples,
        incomplete=incomplete
    )


def query_status_filter(ctx, args, incomplete):
    """Prepare a list of filter names and values for query status filter."""
    filter_names = [
        (
            "status",
            "List only queries which have a certain status "
            "(running or finished)."
        ),
        (
            "slower-than",
            "List only queries which are slower than X miliseconds."
        ),
        (
            "type",
            "List only query of a certain query type."
        )
    ]
    filter_status = [
        (
            "running",
            "List only queries which are currently running or timeouted "
            "(see help text)."
        ),
        (
            "finished",
            "List only queries which were successfully executed."
        ),
        (
            "error",
            "List only queries which were NOT successfully executed."
        )
    ]
    filter_slower = [
        (
            "5",
            "List only queries which are executed slower than 5ms."
        ),
        (
            "100",
            "List only queries which are executed slower than 100ms."
        ),
        (
            "1000",
            "List only queries which are executed slower than 1000ms."
        ),
        (
            "5000",
            "List only queries which are executed slower than 5000ms."
        )
    ]
    filter_type = [
        (
            "ASK",
            "Queries, which return a boolean indicating whether a query "
            "pattern matches or not."
        ),
        (
            "SELECT",
            "Queries, which returns all, or a subset of, the variables "
            "bound in a query pattern match."
        ),
        (
            "DESCRIBE",
            "Queries, which return an RDF graph that describes the "
            "resources found."
        ),
        (
            "CONSTRUCT",
            "Queries, which return an RDF graph constructed by substituting "
            "variables in a set of triple templates."
        ),
        (
            "UPDATE", "Queries, which modify one or more graphs "
                      "(INSERT, DELETE, DROP, etc.)."
        ),
        (
            "UNKNOWN",
            "Queries of unknown type."
        )
    ]

    last_argument = args[len(args) - 1]
    if last_argument == "--filter":
        return _finalize_completion(
            candidates=filter_names,
            incomplete=incomplete
        )
    if last_argument == "status":
        return _finalize_completion(
            candidates=filter_status,
            incomplete=incomplete
        )
    if last_argument == "slower-than":
        return _finalize_completion(
            candidates=filter_slower,
            incomplete=incomplete,
            nat_sort=True
        )
    if last_argument == "type":
        return _finalize_completion(
            candidates=filter_type,
            incomplete=incomplete
        )
    raise ValueError(
        "Last argument unknown. Can not do completion."
    )


def graph_list_filter(ctx, args, incomplete):
    """Prepare a list of filter names and values for graph list filter."""
    filter_names = [
        (
            "access",
            "List only graphs which have a certain access condition "
            "(readonly or writeable)."
        ),
        (
            "imported-by",
            "List only graphs which are in the import tree of a "
            "specified graph."
        )
    ]
    filter_values_access = [
        (
            "readonly",
            "List only graphs which are NOT writable for the current user."
        ),
        (
            "writeable",
            "List only graphs which ARE writeable for the current user."
        )
    ]

    options = []
    if args[len(args) - 1] == "--filter":
        options = _finalize_completion(
            candidates=filter_names,
            incomplete=incomplete
        )
    if args[len(args) - 1] == "access":
        options = _finalize_completion(
            candidates=filter_values_access,
            incomplete=incomplete
        )
    if args[len(args) - 1] == "imported-by":
        options = graph_uris(ctx, args, incomplete)
    return options


def resource_list_filter(ctx, args, incomplete):
    """Prepare a list of filter names and values for resource list filter."""
    filter_names = [
        (
            "project",
            "Filter for file resources from a specific project."
        ),
        (
            "regex",
            "Filter for file resources with a regular expression search on "
            "the name field."
        )
    ]
    filter_values_regex = [
        (
            "csv$",
            "File resources which name ends with .csv"
        ),
        (
            "2021-10-[0-9][0-9]",
            "File resources which name has a date from 2021-10 in it"
        )
    ]

    if args[len(args) - 1] == "--filter":
        return filter_names
    if args[len(args) - 1] == "project":
        return _finalize_completion(
            candidates=project_ids(ctx, args, incomplete),
            incomplete=incomplete
        )
    if args[len(args) - 1] == "regex":
        return _finalize_completion(
            candidates=filter_values_regex,
            incomplete=incomplete
        )
    return []


def workflow_list_filter(ctx, args, incomplete):
    """Prepare a list of filter names and values for workflow list filter."""
    filter_names = [
        (
            "project",
            "List only workflows from a specific project."
        ),
        (
            "io",
            "List only workflows suitable for the workflow io command."
        )
    ]
    filter_values_io = [
        (
            "any",
            "List all workflows suitable for the io command."
        ),
        (
            "input-only",
            "List only worflows with a variable input dataset."
        ),
        (
            "output-only",
            "List only worflows with a variable output dataset."
        ),
        (
            "input-output",
            "List only worflows with a variable input and output dataset."
        ),
    ]

    options = []
    if args[len(args) - 1] == "--filter":
        options = filter_names
    if args[len(args) - 1] == "io":
        options = filter_values_io
    if args[len(args) - 1] == "project":
        options = project_ids(ctx, args, incomplete)
    return _finalize_completion(
        candidates=options,
        incomplete=incomplete
    )
