import logging
from typing import Optional

import qiskit
from qiskit.providers import BaseBackend
from qiskit.providers.ibmq import IBMQ
from qiskit.providers.aer import Aer
from qiskit.providers.basicaer import BasicAer

LOG = logging.getLogger(__name__)


def to_backend(backend_provider: str, backend_name: str, hub: Optional[str] = None, group: Optional[str] = None,
               project: Optional[str] = None) -> Optional[BaseBackend]:
    if backend_provider == type(Aer).__name__ and backend_name in [b.name() for b in Aer.backends()]:
        return Aer.get_backend(backend_name)
    elif backend_provider == type(BasicAer).__name__ and backend_name in [b.name() for b in BasicAer.backends()]:
        return BasicAer.get_backend(backend_name)
    else:
        # This only works if an account is enabled for the session!
        providers = IBMQ.providers(hub=hub, group=group, project=project)
        if len(providers) == 0:
            LOG.error(f'No providers found. Have you enabled an account?')
        if len(providers) > 1:
            LOG.warning(f'There are more than on valid provider of hub={hub}, group={group} and project={project}: '
                        f'{", ".join([str(p) for p in providers])}')
        ibmqx_provider = providers[0]
        if ibmqx_provider and backend_provider == type(ibmqx_provider).__name__ \
                and backend_name in [b.name() for b in ibmqx_provider.backends()]:
            return ibmqx_provider.get_backend(backend_name)
        return None
