import hyperthought as ht


def from_json(pkg):
    """
    Parse the contents of a HyperThought full JSON representation
    of an Element (or derived class). This is the format returned
    by calls to `WorkflowAPI.get_children([UUID])`.

    _predecessors and _successors in Elements are stored as dictionaries
    where `Element`s are keyed to their IDs. However, this maps ID to ID
    to avoid extraneous downloads while still supporting `Element.to_json`.

    Parameters
    ----------
    pkg : JSON
        Full JSON representation returned from HyperThought API.

    Returns
    -------
    hyperthought.api.workflow.Element
        Instance of an Element or subclass of Element.
    """
    kwds = {
        "name": pkg["content"]["name"],
        "assignee": pkg["content"]["assignee"],
        "notes": pkg["content"]["notes"],
        "parent_id": pkg["content"]["parent_process"]
    }
    obj = {
        "process": ht.api.workflow.Process,
        "workflow": ht.api.workflow.Workflow
    }[pkg["content"]["process_type"]](**kwds)
    # set some hidden variables that are typically generated
    # by construction of a HyperThought object.
    obj._id = pkg["content"]["pk"]
    obj._client_id = pkg["content"]["client_id"]
    obj._successors = {_: _ for _ in pkg["content"]["successors"]}
    obj._predecessors = {_: _ for _ in pkg["content"]["predecessors"]}
    return obj
