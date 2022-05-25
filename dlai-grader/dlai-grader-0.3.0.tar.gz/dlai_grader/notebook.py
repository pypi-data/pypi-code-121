import re
import jupytext
from nbformat.notebooknode import NotebookNode
from .config import Config


def notebook_to_script(notebook: NotebookNode) -> str:
    """Converts a notebook into a python script serialized as a string.
    Args:
        notebook (NotebookNode): Notebook to convert into script.
    Returns:
        str: Python script representation as string.
    """
    return jupytext.writes(notebook, fmt="py:percent")


def filter_notebook(notebook: NotebookNode) -> NotebookNode:
    """Filters a notebook to exclude additional cells created by learners.
       Also used for partial grading if the tag has been provided.
    Args:
        notebook (NotebookNode): Notebook to filter.
    Returns:
        NotebookNode: The filtered notebook.
    """
    filtered_cells = []
    partial_grade_regex = "(grade)(.|[ \t]*)(up)(.|[ \t]*)(to)(.|[ \t]*)(here)"

    for cell in notebook["cells"]:
        if not "tags" in cell["metadata"] or not "graded" in cell["metadata"]["tags"]:
            continue
        filtered_cells.append(cell)

        if cell["cell_type"] == "code" and re.search(
            partial_grade_regex, cell["source"]
        ):
            break

    notebook["cells"] = filtered_cells
    return notebook


def get_named_cells(notebook: NotebookNode) -> dict:
    """Returns the named cells for cases when grading is done using cell's output.
    Args:
        nb_json (NotebookNode): The notebook from the learner.
    Returns:
        dict: All named cells encoded as a dictionary.
    """
    named_cells = {}
    for cell in notebook.get("cells"):
        metadata = cell.get("metadata")
        if not "name" in metadata:
            continue
        named_cells.update({metadata.get("name"): cell})
    return named_cells


def tag_code_cells(notebook: NotebookNode) -> NotebookNode:
    """Filters a notebook to exclude additional cells created by learners.
       Also used for partial grading if the tag has been provided.
    Args:
        notebook (NotebookNode): Notebook to filter.
    Returns:
        NotebookNode: The filtered notebook.
    """
    filtered_cells = []

    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            if not "tags" in cell["metadata"]:
                cell["metadata"]["tags"] = []

            tags = cell["metadata"]["tags"]
            tags.append("graded")
            cell["metadata"]["tags"] = tags

        filtered_cells.append(cell)

    notebook["cells"] = filtered_cells
    return notebook


def notebook_version(notebook: NotebookNode) -> str:
    """Returns dlai version of a notebook.

    Args:
        notebook (NotebookNode): A notebook.

    Returns:
        str: Version encoded as string.
    """
    return notebook.get("metadata").get("dlai_version")


def notebook_is_up_to_date(notebook: NotebookNode) -> bool:
    """Determines if a notebook is up-to-date with latest grader version.

    Args:
        notebook (NotebookNode): A notebook.

    Returns:
        bool: True if both versions match, False otherwise.
    """
    version = notebook_version(notebook)
    c = Config()
    if version != c.latest_version:
        return False
    return True
