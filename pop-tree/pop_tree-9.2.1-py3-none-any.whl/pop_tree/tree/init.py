from typing import Any
from typing import Dict

from dict_tools import data as data_

__func_alias__ = {"format_": "format"}


def __init__(hub):
    hub.pop.sub.add(dyne_name="rend", omit_class=False)
    hub.pop.sub.add(dyne_name="graph", omit_class=False)


def doc_cli(hub):
    hub.pop.config.load(["pop_doc", "pop_tree", "rend"], cli="pop_doc")
    hub.pop.loop.create()
    hub.tree.sub.load_all()

    tree = hub.pop.Loop.run_until_complete(hub.tree.init.traverse())
    tree = hub.tree.ref.get(tree, hub.OPT.pop_doc.ref)
    ret = hub.tree.ref.list(tree)

    if not (ret or tree):
        raise KeyError(f"Reference does not exist on the hub: {hub.OPT.pop_doc.ref}")

    result = ret[hub.OPT.pop_doc.ref]

    outputter = hub.OPT.rend.output or "nested"
    print(hub.output[outputter].display(result))


def cli(hub):
    hub.pop.config.load(["pop_tree", "rend"], cli="pop_tree")
    hub.pop.loop.create()
    hub.tree.sub.load_all(pypaths=hub.OPT.pop_tree.pypaths)

    tree = hub.pop.Loop.run_until_complete(hub.tree.init.traverse())
    result = hub.tree.ref.get(tree, hub.OPT.pop_tree.ref)

    if hub.OPT.pop_tree.graph:
        hub.graph.GRAPH = hub.OPT.pop_tree.graph
    else:
        # Find the first plugin that was loaded for graphing
        loaded_mods = hub.graph._loaded
        if "simple" in loaded_mods:
            hub.graph.GRAPH = "simple"
        else:
            iter_mods = iter(hub.graph._loaded)
            hub.graph.GRAPH = next(iter_mods)
            if hub.graph.GRAPH == "init":
                hub.graph.GRAPH = next(iter_mods)

    hub.graph.init.show(result)


async def traverse(hub) -> Dict[str, Any]:
    """
    :param hub: The redistributed pop central hub
    :return: A dictionary representation of all the subs on the hub. I.E:
        pprint(hub.pop.tree.traverse())
    """
    root = data_.NamespaceDict()
    for sub in hub._iter_subs:
        loaded_sub = getattr(hub, sub)
        root[sub] = await hub.tree.sub.recurse(loaded_sub)

        for loaded_mod in sorted(loaded_sub, key=lambda x: x.__name__):
            mod = loaded_mod.__name__
            root[sub][mod] = await hub.tree.mod.parse(loaded_mod, ref=f"{sub}.{mod}")
    return root
