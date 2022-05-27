# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from collections import defaultdict
from importlib import import_module

from contrast.assess_extensions import smart_setattr
from contrast.utils import Namespace
from contrast.utils.object_utils import get_name

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class module(Namespace):
    # map from id(orig_attr_as_func) -> patch
    patch_map = {}
    # map from id(patch_as_func) -> orig_attr
    inverse_patch_map = {}
    # allows lookup of patches by owner ID
    # this is what enables reverse patching
    patches_by_owner = defaultdict(set)
    # allows lookup of patches by owner name
    patches_by_name = defaultdict(set)


def get_patch(obj_as_func):
    return module.patch_map.get(id(obj_as_func))


def patch(owner, name, patch=None):
    """
    Set attribute `name` of `owner` to `patch`.

    If `patch` is not provided, we look up the appropriate existing patch in
    the patch book and apply it. This behavior is used during repatching.

    :param owner: module or class that owns the original attribute
    :param name: str name of the attribute being patched
    :param patch: object replacing owner.name, or None to use an existing patch
    """
    orig_attr = getattr(owner, name, None)
    orig_attr_as_func = as_func(orig_attr)

    if orig_attr_as_func is None:
        # TODO: PYT-692 investigate unexpected patching
        logger.debug(
            "WARNING: failed to patch %s of %s: no such attribute", name, owner
        )
        return
    if patch is None:
        patch = get_patch(orig_attr_as_func)
        if patch is None:
            # TODO: PYT-692 investigate unexpected patching
            logger.debug(
                "WARNING: failed to repatch %s of %s: no entry in the patch map",
                name,
                owner,
            )
            return

    if id(orig_attr_as_func) in module.inverse_patch_map:
        # TODO: PYT-692 investigate unexpected patching
        logger.debug(
            "WARNING: patching over already patched method %s of %s", name, owner
        )

    smart_setattr(owner, name, patch)
    register_patch(owner, name, orig_attr)


def _reverse_patch(owner, name):
    """
    Restore a patched attribute back to its original

    :param owner: module or class that owns the attribute being reverse patched
    :param name: name of the attribute as a string
    """
    patch = getattr(owner, name)
    patch_as_func = as_func(patch)

    if not is_patched(patch):
        return

    orig_attr = module.inverse_patch_map[id(patch_as_func)]

    smart_setattr(owner, name, orig_attr)
    _deregister_patch(patch_as_func, owner, name, orig_attr)


def reverse_patches_by_owner(owner):
    """
    Restore all patched attributes that belong to the owning module/class

    If the owner is a module, any patched classes in this module will not be
    automatically reversed by this method. For example, if the following are patched:

        foo.a
        foo.b
        foo.FooClass.foo_method

    in order to reverse the patches, it will be necessary to call this method twice:

        reverse_patches_by_owner(foo)
        reverse_patches_by_owner(foo.FooClass)

    :param owner: module or class that owns the attribute being reverse patched
    """
    if id(owner) not in module.patches_by_owner:
        return

    for name in list(module.patches_by_owner[id(owner)]):
        _reverse_patch(owner, name)


def reverse_all_patches():
    """
    Reverse every patch managed by the patch_manager.

    Currently, this only reverses direct references to attributes we've patched. It's
    still possible that this doesn't cover cases where we patched an extra reference to
    an attribute via repatching.
    """
    for owner_name in module.patches_by_name.copy():
        try:
            owner = import_module(owner_name)
        except ImportError:
            module_name, _, attr_name = owner_name.rpartition(".")
            owner = getattr(import_module(module_name), attr_name)

        reverse_patches_by_owner(owner)


def register_patch(owner, name, orig_attr):
    """
    Register patch in the patch map to prevent us from patching twice

    :param owner: module or class that owns the original function
    :param name: name of the patched attribute
    :param orig_attr: original attribute, which is being replaced
    """
    patch = getattr(owner, name)
    patch_as_func = as_func(patch)
    orig_as_func = as_func(orig_attr)

    if id(as_func(module.patch_map.get(id(orig_as_func)))) == id(patch_as_func):
        # this is the case for repatching: the original attribute already has a
        # registered patch and that patch matches the one we just applied to it
        return

    if patch_as_func is orig_as_func:
        # TODO: PYT-692 investigate unexpected patching
        logger.debug(
            "WARNING: attempt to register %s as a patch for itself - "
            "skipping patch map registration",
            orig_attr,
        )
        return

    module.patch_map[id(orig_as_func)] = patch
    module.inverse_patch_map[id(patch_as_func)] = orig_attr
    module.patches_by_owner[id(owner)].add(name)
    module.patches_by_name[get_name(owner)].add(name)


def _deregister_patch(patch_as_func, owner, name, orig_attr):
    """
    Remove the patch from all locations in the patch manager.
    """
    owner_name = get_name(owner)
    orig_as_func = as_func(orig_attr)
    module.patches_by_owner[id(owner)].discard(name)
    module.patches_by_name[owner_name].discard(name)
    # if by removing the `name` value from id(owner) set the set becomes
    # empty, remove the key from the dict, too.
    if not module.patches_by_owner[id(owner)]:
        del module.patches_by_owner[id(owner)]
        del module.patches_by_name[owner_name]

    # Safety check for the case where we actually have two different patches that
    # correspond to the same original function (e.g. some of the codecs patches). In
    # these cases, there are two entries in the inverse_patch_map, but only one in the
    # patch_map. This isn't ideal, but it prevents errors when reverse patching.
    if id(orig_as_func) in module.patch_map:
        del module.patch_map[id(orig_as_func)]

    del module.inverse_patch_map[id(patch_as_func)]

    from contrast.agent.policy.applicator import remove_patch_location

    remove_patch_location(owner, name)


def is_patched(attr):
    """
    If the given attribute is a key in the inverse patch map, it means that it is being
    used as a patch.

    :param attr: attribute in question
    :return: True if the attribute is a key in the inverse patch map, False otherwise
    """
    return id(as_func(attr)) in module.inverse_patch_map


def has_associated_patch(attr):
    """
    If we come across an attribute that's a value in the patch_map (a key in
    the inverse patch map), it should be patched. This is most useful during
    re-patching, where we might see an old reference to the unpatched original
    attribute.

    :param attr: attribute in question
    :return: True if the attribute is a key in the patch map, False otherwise
    """
    return id(as_func(attr)) in module.patch_map


def as_func(attr):
    """
    We can't trust the id of unbound methods. For example, if we have class Foo with
    instance method bar, Foo.bar returns a wrapper around the actual function object,
    and that wrapper may change between accesses to Foo.bar. This is accomplished with
    descriptors.

    Luckily, unbound methods should have a __func__ attribute, which references the
    raw underlying function. This value does not change, so we want to enter its id
    in the patch map.

    If we can't get a __func__ attribute, we try to use the _self_wrapper attribute,
    which our wrapt wrappers use
    """
    if not hasattr(attr, "__func__"):
        attr = getattr(attr, "_self_wrapper", attr)
    return getattr(attr, "__func__", attr)
