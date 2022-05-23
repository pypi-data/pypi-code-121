import asyncio
from typing import Any
from typing import Dict
from typing import List

import dict_tools.update


async def unlock(
    hub,
    profiles: Dict[str, Dict[str, Any]],
    backend_key: str = None,
    allowed_backend_profiles: List[str] = None,
):
    """
    Read the raw profiles and search for externally defined profiles.
    """
    # Allow custom specification of a backend key per acct_file
    if backend_key is None:
        backend_key = profiles.get("backend_key", hub.acct.BACKEND_KEY)

    coros = []
    ret = {}
    for backend, backend_profile_data in profiles.get(backend_key, {}).items():
        if backend not in hub.acct.backend:
            hub.log.error(f"acct backend '{backend}' is not available")
            continue
        # The keys are irrelevant for backend profiles
        for backend_profile_name, ctx in backend_profile_data.items():
            if (
                allowed_backend_profiles
                and backend_profile_name not in allowed_backend_profiles
            ):
                hub.log.info(
                    f"acct backend profile not on allow-list from {'backend'}: {backend_profile_name}"
                )
                continue
            try:
                hub.log.info(
                    f"Reading acct backend profiles from '{backend}': {backend_profile_name}"
                )
                backend_profiles = hub.acct.backend[backend].unlock(**ctx)
                # Collect a coroutine for processing the backend
                coros.append(hub.pop.loop.unwrap(backend_profiles))
            except Exception as e:
                hub.log.error(f"{e.__class__}: {e}")

    # process all the backends simultaneously
    for result in asyncio.as_completed(coros):
        try:
            backend_profiles = await result
            dict_tools.update.update(ret, backend_profiles)
        except Exception as e:
            hub.log.error(f"{e.__class__}: {e}")

    return ret
