import asyncio
import re
import sys
import warnings
from typing import Any
from typing import Awaitable
from typing import Dict
from typing import Iterable
from typing import List

import dict_tools.update
from dict_tools.data import NamespaceDict

__func_alias__ = {"profiles_": "profiles"}


def __init__(hub):
    hub.acct.PROFILES = NamespaceDict()
    hub.acct.UNLOCKED = False
    hub.acct.DEFAULT = "default"
    hub.acct.BACKEND_KEY = "acct-backends"
    hub.acct.SERIAL_PLUGIN = "msgpack"

    hub.pop.sub.add(dyne_name="crypto")
    hub.pop.sub.load_subdirs(hub.acct, recurse=True)
    hub.pop.sub.add(dyne_name="rend")
    hub.pop.sub.add(dyne_name="output")
    hub.pop.sub.add(dyne_name="serial")


def cli(hub):
    hub.pop.config.load(["acct", "rend"], cli="acct")
    hub.pop.loop.create()
    coro = hub.acct.init.cli_apply()
    retcode = hub.pop.Loop.run_until_complete(coro)
    sys.exit(retcode)


async def cli_apply(hub) -> int:
    hub.acct.SERIAL_PLUGIN = hub.OPT.acct.serial_plugin
    if hub.SUBPARSER == "encrypt":
        created_new_acct_key = False
        if not hub.OPT.acct.acct_key:
            created_new_acct_key = True
            hub.log.info(
                f"New acct_key generated with '{hub.OPT.acct.crypto_plugin}' plugin"
            )

        new_key = await hub.crypto.init.encrypt_file(
            crypto_plugin=hub.OPT.acct.crypto_plugin,
            acct_file=hub.OPT.acct.input_file,
            acct_key=hub.OPT.acct.acct_key,
            output_file=hub.OPT.acct.output_file,
            render_pipe=hub.OPT.acct.render_pipe,
        )
        hub.log.info(
            f"Encrypted {hub.OPT.acct.input_file} with the {hub.OPT.acct.crypto_plugin} algorithm"
        )
        if created_new_acct_key:
            # Print this to the terminal, and only this -- for easier scripting
            # Do not log it or put it in log files
            print(new_key)

        return 0
    elif hub.SUBPARSER == "decrypt":
        acct_key = hub.OPT.acct.acct_key
        if not acct_key:
            raise KeyError(
                f"encryption key not found in ACCT_KEY environment variable or --acct-key flag"
            )
        ret = await hub.crypto.init.decrypt_file(
            crypto_plugin=hub.OPT.acct.crypto_plugin,
            acct_file=hub.OPT.acct.input_file,
            acct_key=acct_key,
            render_pipe=hub.OPT.acct.render_pipe,
        )
        outputter = hub.OPT.rend.output or "yaml"
        out = hub.output[outputter].display(ret)
        print(out)
        return 0


async def profiles_(
    hub,
    acct_file: str,
    acct_key: str,
    crypto_plugin: str = "fernet",
    render_pipe: str = "yaml",
    allowed_backend_profiles: List[str] = None,
) -> Dict[str, Any]:
    """
    Read profile information from a file and return the raw data
    """
    raw_profiles = await hub.crypto.init.decrypt_file(
        crypto_plugin=crypto_plugin,
        acct_file=acct_file,
        acct_key=acct_key,
        render_pipe=render_pipe,
    )
    backend_profiles = await hub.acct.backend.init.unlock(
        profiles=raw_profiles, allowed_backend_profiles=allowed_backend_profiles
    )
    dict_tools.update.update(raw_profiles, backend_profiles)
    return raw_profiles


async def unlock(
    hub,
    acct_file: str,
    acct_key: str,
    crypto_plugin: str = "fernet",
    render_pipe: str = "yaml",
):
    """
    Initialize the file read, then store the authentication data on the hub as hub.acct.PROFILES
    """
    if hub.acct.UNLOCKED:
        return

    raw_profiles = await hub.acct.init.profiles(
        acct_file, acct_key, crypto_plugin, render_pipe=render_pipe
    )
    hub.acct.BACKEND_KEY = raw_profiles.pop("backend_key", hub.acct.BACKEND_KEY)
    hub.acct.DEFAULT = raw_profiles.pop("default", hub.acct.DEFAULT)
    dict_tools.update.update(hub.acct.PROFILES, raw_profiles)
    hub.acct.UNLOCKED = True


async def unlock_blob(
    hub,
    acct_file_contents: str,
    acct_key: str,
    crypto_plugin: str = "fernet",
    backend_key: str = None,
    default_profile: str = None,
    allowed_backend_profiles: List[str] = None,
):
    """
    Read acct data from a byte string
    """
    profiles = await hub.crypto.init.decrypt(
        plugin=crypto_plugin, data=acct_file_contents, key=acct_key
    )
    if backend_key is None:
        backend_key = profiles.get("backend_key", hub.acct.BACKEND_KEY)

    if default_profile is None:
        default_profile = profiles.get("default", hub.acct.DEFAULT)

    backend_profiles = await hub.acct.backend.init.unlock(
        profiles=profiles,
        backend_key=backend_key,
        allowed_backend_profiles=allowed_backend_profiles,
    )

    dict_tools.update.update(profiles, backend_profiles)

    return NamespaceDict(
        default_profile=default_profile,
        backend_key=backend_key,
        profiles=profiles,
        sub_profiles=None,
    )


async def single(
    hub,
    profile_name: str,
    subs: Iterable[str],
    sub_profiles: None,
    profiles: Dict[str, Dict[str, Any]],
):
    """
    Retrieve a specific named profile for the given subs and profiles
    """
    if sub_profiles is not None:
        warnings.warn(
            "sub_profiles is no longer used, remove it from the call",
            DeprecationWarning,
        )
    ret = None
    for sub in subs:
        if sub in profiles:
            if profile_name in profiles[sub]:
                if ret is None:
                    ret = NamespaceDict(profiles[sub][profile_name])
                else:
                    raise ValueError(
                        f"Multiple profiles named '{profile_name}' across subs: {', '.join(subs)}"
                    )

    if ret is None:
        clean_profiles = {
            provider: list(profiles)
            for provider, profiles in profiles.items()
            if provider in subs
        }
        hub.log.debug(f"Could not find profile '{profile_name}' in: {clean_profiles}")
        ret = {}

    return ret


async def gather(
    hub,
    subs: Iterable[str],
    profile: str,
    profiles=None,
    sub_profiles=None,
    allowed_backend_profiles: List[str] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    :param hub:
    :param subs: The subs to check for a profile
    :param profile: The name of the acct_profile to retrieve
    :param profiles: raw profiles to use if not unlocking acct first
    :param sub_profiles: Unused
    :return: The named profile
    """
    if sub_profiles is not None:
        warnings.warn(
            "sub_profiles is no longer used, remove it from the call",
            DeprecationWarning,
        )

    # If acct is locked and we don't have new profiles then return right away
    if profiles is None:
        if hub.acct.UNLOCKED:
            profiles = hub.acct.PROFILES
        else:
            profiles = {}

    # Collect any other profiles from backends
    backend_profiles = await hub.acct.backend.init.unlock(
        profiles, allowed_backend_profiles=allowed_backend_profiles
    )
    dict_tools.update.update(profiles, backend_profiles)

    # Run the profiles through the gather plugins and update them with any changes
    processed_profiles = await hub.acct.init.process(subs, profiles)
    dict_tools.update.update(profiles, processed_profiles)

    return await hub.acct.init.single(
        profile_name=profile,
        subs=subs,
        profiles=profiles,
        sub_profiles=sub_profiles,
    )


async def process(hub, subs: Iterable[str], profiles: Dict[str, Any]):
    """
    Process the given profiles through acct plugins.
    Acct plugins turn static profile data into connections to a server etc...
    """
    processed = NamespaceDict()
    coros = []

    for sub in subs:
        if not hasattr(hub.acct, sub):
            hub.log.trace(f"{sub} does not extend acct")
            continue

        processed[sub] = {}
        for plug in hub.acct[sub]:
            try:
                if "profiles" in plug.gather.signature.parameters:
                    regex = re.compile(f"{sub}(\\.{plug.__name__})?$")
                    relevant_profiles = {
                        k: v for k, v in profiles.items() if regex.match(k)
                    }
                    if not relevant_profiles:
                        continue
                    ret = plug.gather(relevant_profiles)
                else:
                    # It either doesn't need to know about existing profiles or will get them from hub.acct.PROFILES
                    ret = plug.gather()

                coros.append(_keyed_coroutine(sub, hub.pop.loop.unwrap(ret)))
            except Exception as e:
                hub.log.error(
                    f"{e.__class__.__name__} gathering profiles from hub.acct.{sub}.{plug.__name__}: {e}"
                )

    for ret in asyncio.as_completed(coros):
        sub = None
        try:
            sub, val = await ret
            processed[sub].update(val)
        except Exception as e:
            hub.log.error(f"{e.__class__.__name__}: {sub}: await gather profiles: {e}")

    return processed


async def _keyed_coroutine(sub: str, coro: Awaitable):
    """
    :param sub:
    :param coro:
    :return:
    """
    return sub, await coro
