from typing import Any
from typing import Dict
from typing import List

from dict_tools import data as data_


def load_all(hub, pypaths: List[str] = None):
    """
    Load the named pypaths and all available dynes onto the hub
    """
    if pypaths:
        for pypath in pypaths:
            try:
                hub.pop.sub.add(
                    pypath=pypath,
                    omit_class=False,
                    omit_func=False,
                    omit_vars=False,
                    stop_on_failures=False,
                )
            except ModuleNotFoundError as e:
                hub.log.error(e)
                raise

    for dyne in hub._dynamic:
        if not hasattr(hub, dyne):
            hub.pop.sub.add(
                dyne_name=dyne,
                omit_class=False,
                omit_func=False,
                omit_vars=False,
                stop_on_failures=False,
            )
        try:
            hub.pop.sub.load_subdirs(hub[dyne], recurse=True)
        except (AttributeError or TypeError):
            ...


async def recurse(hub, sub, ref: str = None) -> Dict[str, Any]:
    """
    Find all of the loaded subs in a Sub. I.E:
        pprint(hub.pop.tree.recurse(hub.pop))
    :param hub: The redistributed pop central hub
    :param sub: The pop object that contains the loaded module data
    :param ref: The current reference on the hub
    """
    sub_name = sub._dyne_name
    if sub_name:
        if ref:
            ref = f"{ref}.{sub_name}"
        else:
            ref = sub_name
    ret = data_.NamespaceDict()
    for loaded in sorted(sub._subs):
        loaded_ref = f"{ref}.{loaded}"
        try:
            loaded_sub = getattr(sub, loaded)
        except AttributeError:
            continue
        if not (
            getattr(loaded_sub, "_virtual", False)
            and getattr(loaded_sub, "_sub_virtual", True)
        ):
            # Bail early if the sub's virtual isn't True
            continue
        recursed_sub = await hub.tree.sub.recurse(loaded_sub, ref=loaded_ref)

        for mod in sorted(loaded_sub._loaded):
            loaded_mod = getattr(loaded_sub, mod)
            recursed_sub[mod] = await hub.tree.mod.parse(
                loaded_mod, ref=f"{ref}.{loaded}.{mod}"
            )

        if recursed_sub:
            ret[loaded] = recursed_sub

    return ret
