from os.path import join
from django.template import Context, Template
from core_explore_tree_app.components.navigation.api import get_by_id
from core_explore_tree_app.components.data import query
from core_explore_tree_app.settings import BASE_DIR_EXPLORE_TREE
from core_explore_tree_app.utils.xml.projection import get_projection
import core_explore_tree_app.components.leaf.api as leaf_api

# FIXME: use template loader
TEMPLATES_PATH = join(
    BASE_DIR_EXPLORE_TREE,
    "core_explore_tree_app",
    "templates",
    "core_explore_tree_app",
    "user",
    "navigation",
    "parser",
)


def render_navigation_tree(navigation, template_id):
    """
    Render the navigation tree with the number of documents under each node
    Args: navigation:
        - navigation root
        - template id
    Return: navigation tree
    """
    nav = navigation
    tab = []
    nav_table = {}
    render_navigation(nav, template_id, tab, nav_table)
    return get_html_tree(nav, template_id, tab, nav_table)


def render_navigation(navigation, template_id, tab, nav_table):

    """
    Build the navigation tree with the number of documents under each node that directly contain documents
    Args: navigation:
        - navigation root
        - template id
        - tab :  table of node_id and the direct number of docs for this node
        - nav_table : table of node id and its related information (branch_id, branches)
    Return: navigation tree
    """
    nav_tree_html = ""

    for navigation_id in navigation.children:
        navigation_child = get_by_id(navigation_id)
        number_of_doc = 0
        with open(join(TEMPLATES_PATH, "li.html"), "r") as li_file:
            li_content = li_file.read()
            li_template = Template(li_content)
            name = (
                navigation_child.name.split("#")[1]
                if "#" in navigation_child.name
                else navigation_child.name
            )
            # there is a projection, get documents from database
            if (
                "projection" in navigation_child.options
                and navigation_child.options["projection"] is not None
            ):
                _branch, number_of_doc = render_documents(
                    navigation_child, template_id, number_of_doc
                )
                context = {
                    "branch_id": navigation_id,
                    "branches": _branch,
                    "branch_name": name,
                    "branch_docs_nb": str(number_of_doc),
                }
            else:
                context = {
                    "branch_id": navigation_id,
                    "branch_name": str(
                        get_number_of_node_doc(navigation_id, name, nav_table)
                    ),
                    "branches": render_navigation(
                        navigation_child, template_id, tab, nav_table
                    ),
                }
            tab.append((navigation_id, number_of_doc))

            if (
                "view" in navigation_child.options
                and navigation_child.options["view"] is not None
            ):
                context["branch_view"] = "true"
            if (
                "hidden" in navigation_child.options
                and navigation_child.options["hidden"]
            ):
                context["hidden"] = True
            nav_tree_html += li_template.render(Context(context))
            nav_table[navigation_id] = context
    return nav_tree_html


def get_html_tree(navigation, template_id, tab, nav_table):
    """
    Adding the number of documents under each node of the tree
    Args: request:
        - navigation root
        - template id
        - tab :  table of node_id and the direct number of docs for this node
        - nav_table : table of node id and its related information (branch_id, branches) used to build the html tree
    Return: navigation tree
    """
    doc_dict = {}
    dashtable = []
    # nav_tree_html=''
    for t in tab:
        # navigation_child = get_by_id(t[0])
        if t[0] in dashtable:
            doc_dict[t[0]] += t[1]
        else:
            doc_dict[t[0]] = t[1]
            dashtable.append(t[0])
    get_doc_by_nodes(navigation, doc_dict)
    for k, v in nav_table.items():
        try:
            if v["branch_docs_nb"]:
                # if no docs under the current node display the number of docs in black
                if str(v["branch_docs_nb"]) == str(0):
                    value = v["branch_name"] + " (" + str(doc_dict[k]) + ")"
                    v["branch_name"] = value
                    del v["branch_docs_nb"]
        except Exception as e:
            # if no docs under the current node display the number of docs in black
            if str(doc_dict[k]) != str(0):
                v["branch_docs_nb"] = str(doc_dict[k])
            else:
                value = v["branch_name"] + " (" + str(doc_dict[k]) + ")"
                v["branch_name"] = value

    nav_tree_html = render_html_tree(navigation, template_id, tab, nav_table)
    return nav_tree_html


def render_html_tree(navigation, template_id, tab, navigation_table):
    """
    Renders the navigation tree that contains the number of docs under each node of the tree
    Args: request:
        - navigation root
        - template id
        - tab: table of the id of the navigation nodes and the number of docs under each node
        - nav_table : table of node id and its related information (branch_id, branches) used to build the html tree
    Return: navigation tree
    """
    nav_tree_html = ""
    for navigation_id in navigation.children:
        navigation_child = get_by_id(navigation_id)

        with open(join(TEMPLATES_PATH, "li.html"), "r") as li_file:
            li_content = li_file.read()
            li_template = Template(li_content)
            # there is a projection, get documents from database
            if (
                "projection" in navigation_child.options
                and navigation_child.options["projection"] is not None
            ):
                x, y = render_documents(navigation_child, template_id)
                navigation_table[navigation_id]["branches"] = x
            else:
                navigation_table[navigation_id]["branches"] = render_html_tree(
                    navigation_child, template_id, tab, navigation_table
                )

            nav_tree_html += li_template.render(
                Context(navigation_table[navigation_id])
            )
    return nav_tree_html


def render_documents(navigation, template_id, number_of_docs=0):
    """
    Build the documents in the navigation tree
    Args: request:
        - navigation root
        - template id
        - number_of_docs : number of documents under a leaf node
    Return: html with the name of the doc
    """
    doc_tree_html = ""
    number_of_docs = 0
    leaf_name = navigation.name
    leaf_id = navigation.id
    try:
        # Get the navigation id
        navigation_id = str(navigation.id)

        # Get projection
        projection = navigation.options["projection"]

        # get filters from parents
        filters = []
        while True:
            # add filter to the list of filters
            if (
                "filter" in navigation.options
                and navigation.options["filter"] is not None
            ):
                filters.append(navigation.options["filter"])
            # if no parent, stops the filter lookup
            if navigation.parent is None:
                break
            else:  # if parent, continue the filter lookup at the parent level
                navigation = get_by_id(navigation.parent)

        # get the documents matching the query

        documents = query.execute_query(template_id, filters, projection)
        for document in documents:
            with open(join(TEMPLATES_PATH, "li_document.html"), "r") as li_file:
                li_content = li_file.read()
                li_template = Template(li_content)
                branch_name = get_projection(document)
                context = {
                    "branch_id": document.id,
                    "parent_id": navigation_id,
                    "branch_name": branch_name,
                }

                doc_tree_html += li_template.render(Context(context))
                number_of_docs += 1
            leaf_api.upsert_leaf_object(str(leaf_id), str(document.id))

    except Exception as e:
        with open(join(TEMPLATES_PATH, "li_error.html"), "r") as li_file:
            li_content = li_file.read()
            li_template = Template(li_content)

        context = {"error_message": str(e)}

        doc_tree_html = li_template.render(Context(context))
    return doc_tree_html, number_of_docs


def get_number_of_node_doc(id_node, name, nav_table):
    """
    Write the number of documents under a node that contains other nodes
    Args: request:
        - id node
        - name of the document
        - nav_table : table of node id and its related information (branch_id, branches) used to build the html tree
    Return: name of the node and the number of docs under this node
    """
    try:
        return " " + str(nav_table[id_node]["branch_name"])
    except Exception as e:
        return name


def get_doc_by_nodes(node, dico):
    """
    Recursive function that calculates the number of docs under each node of the tree
    Args: request:
        - node :navigation object
        - dico : dict of node and its associated number of docs
    Return: Dict[node,number of node under this node]
    """

    try:  # Type(node) = Navigation
        if node.children:
            node_doc = sum(
                [get_doc_by_nodes(child_id, dico) for child_id in node.children]
            )
            dico[node.id] = node_doc
            return node_doc
        else:
            return dico[node.id]

    except Exception as e:  # node = ID of a Navigation object
        nav_child = get_by_id(node)
        if nav_child.children:
            node_doc = sum(
                [get_doc_by_nodes(child_id, dico) for child_id in nav_child.children]
            )
            dico[node] = node_doc
            return node_doc
        else:
            return dico[node]
