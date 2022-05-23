from __future__ import annotations

import asyncio
import datetime
import json
import logging
import sys
import weakref
from collections import namedtuple
from typing import (
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    NoReturn,
    Optional,
    Set,
    Tuple,
    Union,
    overload,
)

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from coiled.context import track_context
from distributed.utils import Log, Logs

from ..core import Async
from ..core import Cloud as OldCloud
from ..core import IsAsynchronous, Sync, delete_docstring, list_docstring
from ..errors import DoesNotExist, ServerError
from ..utils import COILED_LOGGER_NAME, GatewaySecurity, validate_type
from .states import (
    InstanceStateEnum,
    ProcessStateEnum,
    flatten_log_states,
    get_process_instance_state,
    log_states,
)

logger = logging.getLogger(COILED_LOGGER_NAME)


def setup_logging(level=logging.INFO):
    # only set up logging if there's no log level specified yet on the coiled logger
    if logging.getLogger(COILED_LOGGER_NAME).level == 0:
        logging.getLogger(COILED_LOGGER_NAME).setLevel(level)
        logging.basicConfig()


async def handle_api_exception(response, exception_cls=ServerError) -> NoReturn:
    error_body = await response.json()
    if "message" in error_body:
        raise exception_cls(error_body["message"])
    if "detail" in error_body:
        raise exception_cls(error_body["detail"])
    raise exception_cls(error_body)


class FirewallOptions(TypedDict):
    """

    A dictionary with the following key/value pairs

    Parameters
    ----------
    ports
        List of ports to open to cidr on the scheduler.
        For example, ``[22, 8786]`` opens port 22 for SSH and 8786 for client to Dask connection.
    cidr
        CIDR block from which to allow access. For example ``0.0.0.0/0`` allows access from any IP address.
    """

    ports: List[int]
    cidr: str


class BackendOptions(TypedDict, total=False):
    """

    A dictionary with the following key/value pairs

    Parameters
    ----------
    region_name
        Region name to launch cluster in. For example: us-east-2
    zone_name
        Zone name to launch cluster in. For example: us-east-2a
    firewall
        Allows you to specify firewall for scheduler; see :py:class:`FirewallOptions` for details.
    ingress
        Allows you to specify multiple CIDR blocks (and corresponding ports) to open for ingress
        on the scheduler firewall.
    spot
        Whether to request spot instances.
    spot_on_demand_fallback
        If requesting spot, whether to request non-spot instances if we get fewer spot instances
        than desired.
    """

    region_name: Optional[str]
    zone_name: Optional[str]
    firewall: Optional[FirewallOptions]
    ingress: Optional[List[FirewallOptions]]
    spot: Optional[bool]
    spot_on_demand_fallback: Optional[bool]


class AWSOptions(BackendOptions, total=False):
    """

    A dictionary with the following key/value pairs plus any pairs in :py:class:`BackendOptions`

    Parameters
    ----------
    keypair_name
        AWS Keypair to assign worker/scheduler instances
    """

    keypair_name: Optional[str]
    # future: add stuff like "spot" when supported


class GCPOptions(BackendOptions, total=False):
    worker_accelerator_count: Optional[int]
    worker_accelerator_type: Optional[str]


BackendOptionTypes = [AWSOptions, GCPOptions]


class CloudBeta(OldCloud, Generic[IsAsynchronous]):
    _recent_sync: list[weakref.ReferenceType[CloudBeta[Sync]]] = list()
    _recent_async: list[weakref.ReferenceType[CloudBeta[Async]]] = list()

    # just overriding to get the right signature (CloudBeta, not Cloud)
    def __enter__(self: CloudBeta[Sync]) -> CloudBeta[Sync]:
        return self

    def __exit__(self: CloudBeta[Sync], typ, value, tb) -> None:
        self.close()

    # these overloads are necessary for the typechecker to know that we really have a CloudBeta, not a Cloud
    # without them, CloudBeta.current would be typed to return a Cloud
    #
    # https://www.python.org/dev/peps/pep-0673/ would remove the need for this.
    # That PEP also mentions a workaround with type vars, which doesn't work for us because type vars aren't
    # subscribtable
    @overload
    @classmethod
    def current(cls, asynchronous: Sync) -> CloudBeta[Sync]:
        ...

    @overload
    @classmethod
    def current(cls, asynchronous: Async) -> CloudBeta[Async]:
        ...

    @overload
    @classmethod
    def current(cls, asynchronous: bool) -> CloudBeta:
        ...

    @classmethod
    def current(cls, asynchronous: bool) -> CloudBeta:
        recent: list[weakref.ReferenceType[CloudBeta]]
        if asynchronous:
            recent = cls._recent_async
        else:
            recent = cls._recent_sync
        try:
            cloud = recent[-1]()
            while cloud is None or cloud.status != "running":
                recent.pop()
                cloud = recent[-1]()
        except IndexError:
            if asynchronous:
                return cls(asynchronous=True)
            else:
                return cls(asynchronous=False)
        else:
            return cloud

    @track_context
    async def _get_default_instance_types(self, account: str = None) -> List[str]:
        provider = await self.get_account_provider_name(account)
        if provider == "aws":
            return ["t3.medium"]
        elif provider == "gcp":
            return ["e2-standard-2"]
        else:
            raise ValueError(
                f"unexpected provider {provider}; cannot determine default instance types"
            )

    @track_context
    async def _list_clusters(self, account: str = None):
        return await self._depaginate_list(self._list_clusters_page, account=account)

    @overload
    def list_clusters(self: Cloud[Sync], account: str = None) -> list:
        ...

    @overload
    def list_clusters(self: Cloud[Async], account: str = None) -> Awaitable[list]:
        ...

    @list_docstring
    def list_clusters(self, account: str = None) -> Union[list, Awaitable[list]]:
        return self._sync(self._list_clusters, account)

    async def _list_clusters_page(
        self, page: int, account: str = None
    ) -> Tuple[list, bool]:
        page_size = 100
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            self.server + f"/api/v2/clusters/account/{account}/",
            params={"limit": page_size, "offset": page_size * page},
        )
        if response.status >= 400:
            await handle_api_exception(response)

        results = await response.json()
        has_more_pages = len(results) > 0
        return results, has_more_pages

    @staticmethod
    async def _depaginate_list(
        func: Callable[..., Awaitable[Tuple[list, bool]]],
        *args,
        **kwargs,
    ) -> list:
        results_all = []
        page = 0
        while True:
            kwargs["page"] = page
            results, next = await func(*args, **kwargs)
            results_all += results
            page += 1
            if (not results) or next is None:
                break
        return results_all

    @track_context
    async def _create_cluster(
        self,
        # todo: make name optional and pick one for them, like pre-declarative?
        # https://gitlab.com/coiled/cloud/-/issues/4305
        name: str,
        *,
        software_environment: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        worker_cpu: int = None,
        worker_memory: Union[str, List[str]] = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, List[str]] = None,
        account: str = None,
        workers: int = 0,
        environ: Optional[Dict] = None,
        scheduler_vm_types: Optional[list] = None,
        gcp_worker_gpu_type: str = None,
        gcp_worker_gpu_count: int = None,
        worker_vm_types: Optional[list] = None,
        backend_options: Optional[Union[AWSOptions, GCPOptions, dict]] = None,
    ) -> int:
        # TODO (Declarative): support these args, or decide not to
        # https://gitlab.com/coiled/cloud/-/issues/4305

        if scheduler_class is not None:
            raise ValueError("scheduler_class is not supported in beta/new Coiled yet")

        account = account or self.default_account
        account, name = self._normalize_name(
            name,
            context_account=account,
            allow_uppercase=True,
        )
        self._verify_account(account)

        data = {
            "name": name,
            "workers": workers,
            "worker_instance_types": worker_vm_types,
            "scheduler_instance_types": scheduler_vm_types,
            "software_environment": software_environment,
            "worker_options": worker_options,
            "worker_cpu": worker_cpu,
            "worker_class": worker_class,
            "worker_memory": worker_memory,
            "scheduler_options": scheduler_options,
            "scheduler_cpu": scheduler_cpu,
            "scheduler_memory": scheduler_memory,
            "environ": environ,
        }

        if gcp_worker_gpu_type is not None:
            # for backwards compatibility with v1 options
            backend_options = backend_options if backend_options else {}
            backend_options = {
                **backend_options,
                "worker_accelerator_count": gcp_worker_gpu_count or 1,
                "worker_accelerator_type": gcp_worker_gpu_type,
            }
        elif gcp_worker_gpu_count:
            # not ideal but v1 only supported T4 and `worker_gpu=1` would give you one
            backend_options = backend_options if backend_options else {}
            backend_options = {
                **backend_options,
                "worker_accelerator_count": gcp_worker_gpu_count,
                "worker_accelerator_type": "nvdia-tesla-t4",
            }

        if backend_options:
            # for backwards compatibility with v1 options
            if "region" in backend_options and "region_name" not in backend_options:
                backend_options["region_name"] = backend_options["region"]  # type: ignore
                del backend_options["region"]  # type: ignore
            if "zone" in backend_options and "zone_name" not in backend_options:
                backend_options["zone_name"] = backend_options["zone"]  # type: ignore
                del backend_options["zone"]  # type: ignore
            # firewall just lets you specify a single CIDR block to open for ingress
            # we want to support a list of ingress CIDR blocks
            if "firewall" in backend_options:
                backend_options["ingress"] = [backend_options.pop("firewall")]  # type: ignore

            # validate against TypedDicts -- should be better (especially better errors)
            if not any((validate_type(t, backend_options) for t in BackendOptionTypes)):
                raise ValueError(
                    "backend_options should be an instance of coiled.BackendOptions"
                )

            # convert the list of ingress rules to the FirewallSpec expected server-side
            if "ingress" in backend_options:
                fw_spec = {"ingress": backend_options.pop("ingress")}
                backend_options["firewall_spec"] = fw_spec  # type: ignore

            data["options"] = backend_options

        response = await self._do_request(
            "POST", self.server + f"/api/v2/clusters/account/{account}/", json=data
        )
        if response.status >= 400:
            await handle_api_exception(response)
        json = await response.json()
        return json["id"]

    @overload
    def create_cluster(
        self: Cloud[Sync],
        name: str = None,
        *,
        software: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        worker_cpu: int = None,
        worker_memory: int = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: int = None,
        account: str = None,
        workers: int = 0,
        environ: Optional[Dict] = None,
        scheduler_vm_types: Optional[list] = None,
        worker_gpu_type: str = None,
        worker_vm_types: Optional[list] = None,
        backend_options: Optional[dict | BackendOptions] = None,
    ) -> int:
        ...

    @overload
    def create_cluster(
        self: Cloud[Async],
        name: str = None,
        *,
        software: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        worker_cpu: int = None,
        worker_memory: int = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: int = None,
        account: str = None,
        workers: int = 0,
        environ: Optional[Dict] = None,
        scheduler_vm_types: Optional[list] = None,
        worker_gpu_type: str = None,
        worker_vm_types: Optional[list] = None,
        backend_options: Optional[dict | BackendOptions] = None,
    ) -> Awaitable[int]:
        ...

    def create_cluster(
        self,
        name: str = None,
        *,
        software: str = None,
        worker_class: str = None,
        worker_options: dict = None,
        worker_cpu: int = None,
        worker_memory: int = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: int = None,
        account: str = None,
        workers: int = 0,
        environ: Optional[Dict] = None,
        scheduler_vm_types: Optional[list] = None,
        worker_gpu_type: str = None,
        worker_vm_types: Optional[list] = None,
        backend_options: Optional[dict | BackendOptions] = None,
    ) -> Union[int, Awaitable[int]]:

        return self._sync(
            self._create_cluster,
            name=name,
            software_environment=software,
            worker_class=worker_class,
            worker_options=worker_options,
            worker_cpu=worker_cpu,
            worker_memory=worker_memory,
            scheduler_options=scheduler_options,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            account=account,
            workers=workers,
            environ=environ,
            scheduler_vm_types=scheduler_vm_types,
            worker_vm_types=worker_vm_types,
            gcp_worker_gpu_type=worker_gpu_type,
            backend_options=backend_options,
        )

    @track_context
    async def _delete_cluster(self, cluster_id: int, account: str = None) -> None:
        account = account or self.default_account

        route = f"/api/v2/clusters/account/{account}/id/{cluster_id}"

        response = await self._do_request(
            "DELETE",
            self.server + route,
        )
        if response.status >= 400:
            await handle_api_exception(response)
        else:
            # multiple deletes sometimes fail if we don't await response here
            await response.json()
            logger.info(f"Cluster {cluster_id} deleted successfully.")

    async def _get_cluster_details(self, cluster_id: int, account: str = None):
        account = account or self.default_account
        r = await self._do_request_idempotent(
            "GET", self.server + f"/api/v2/clusters/account/{account}/id/{cluster_id}"
        )
        if r.status >= 400:
            await handle_api_exception(r)
        return await r.json()

    def _get_cluster_details_synced(self, cluster_id: int, account: str = None):
        return self._sync(
            self._get_cluster_details,
            cluster_id=cluster_id,
            account=account,
        )

    def cluster_details(self, cluster_id: int, account: str = None):
        details = self._sync(
            self._get_cluster_details,
            cluster_id=cluster_id,
            account=account,
        )
        state_keys = ["state", "reason", "updated"]

        def get_state(state: dict):
            return {k: v for k, v in state.items() if k in state_keys}

        def get_instance(instance):
            if instance is None:
                return None
            else:
                return {
                    "created": instance["created"],
                    "name": instance["name"],
                    "public_ip_address": instance["public_ip_address"],
                    "private_ip_address": instance["private_ip_address"],
                    "current_state": get_state(instance["current_state"]),
                }

        def get_process(process: dict):
            if process is None:
                return None
            else:
                return {
                    "created": process["created"],
                    "name": process["name"],
                    "current_state": get_state(process["current_state"]),
                    "instance": get_instance(process["instance"]),
                }

        return {
            "id": details["id"],
            "workers": [get_process(w) for w in details["workers"]],
            "scheduler": get_process(details["scheduler"]),
            "current_state": get_state(details["current_state"]),
            "created": details["created"],
        }

    async def _get_workers_page(
        self, cluster_id: int, page: int, account: str = None
    ) -> Tuple[list, bool]:
        page_size = 100
        account = account or self.default_account

        response = await self._do_request(
            "GET",
            self.server + f"/api/v2/workers/account/{account}/cluster/{cluster_id}/",
            params={"limit": page_size, "offset": page_size * page},
        )
        if response.status >= 400:
            await handle_api_exception(response)

        results = await response.json()
        has_more_pages = len(results) > 0
        return results, has_more_pages

    @track_context
    async def _get_worker_names(
        self,
        account: str,
        cluster_id: int,
        statuses: Optional[List[ProcessStateEnum]] = None,
    ) -> Set[str]:

        worker_infos = await self._depaginate_list(
            self._get_workers_page, cluster_id=cluster_id, account=account
        )
        logger.debug(f"workers: {worker_infos}")
        return {
            w["name"]
            for w in worker_infos
            if statuses is None or w["current_state"]["state"] in statuses
        }

    @track_context
    async def _security(self, cluster_id: int, account: str = None):
        cluster = await self._get_cluster_details(
            cluster_id=cluster_id, account=account
        )
        if (
            ProcessStateEnum(cluster["scheduler"]["current_state"]["state"])
            != ProcessStateEnum.started
        ):
            raise RuntimeError(
                f"Cannot get security info for cluster {cluster_id} scheduler is ready"
            )

        public_ip = cluster["scheduler"]["instance"]["public_ip_address"]
        private_ip = cluster["scheduler"]["instance"]["private_ip_address"]
        tls_cert = cluster["cluster_options"]["tls_cert"]
        tls_key = cluster["cluster_options"]["tls_key"]
        scheduler_port = cluster["scheduler_port"]

        # TODO (Declarative): pass extra_conn_args if we care about proxying through Coiled to the scheduler
        security = GatewaySecurity(tls_key, tls_cert)

        return security, {
            # TODO (Declarative):
            #  if Declarative ever supports schedulers on other ports, stop hard-coding the portop
            "private_address": f"tls://{private_ip}:{scheduler_port}",
            "public_address": f"tls://{public_ip}:{scheduler_port}",
            "dashboard_address": f"http://{public_ip}:8787",
        }

    @track_context
    async def _requested_workers(
        self, cluster_id: int, account: str = None
    ) -> Set[str]:
        raise NotImplementedError("TODO")

    @track_context
    async def _get_cluster_by_name(self, name: str, account: str = None) -> int:
        account, name = self._normalize_name(
            name, context_account=account, allow_uppercase=True
        )

        response = await self._do_request(
            "GET",
            self.server + f"/api/v2/clusters/account/{account}/name/{name}",
        )
        if response.status == 404:
            raise DoesNotExist
        elif response.status >= 400:
            await handle_api_exception(response)

        cluster = await response.json()
        return cluster["id"]

    @track_context
    async def _cluster_status(
        self, cluster_id: int, account: str = None, exclude_stopped: bool = True
    ) -> dict:
        raise NotImplementedError("TODO?")

    @track_context
    async def _get_cluster_states_declarative(
        self,
        cluster_id: int,
        account: str = None,
        start_time: datetime.datetime = None,
    ) -> int:
        account = account or self.default_account

        params = (
            {"start_time": start_time.isoformat()} if start_time is not None else {}
        )

        response = await self._do_request_idempotent(
            "GET",
            self.server + f"/api/v2/clusters/account/{account}/id/{cluster_id}/states",
            params=params,
        )
        if response.status >= 400:
            await handle_api_exception(response)

        return await response.json()

    def get_cluster_states(
        self,
        cluster_id: int,
        account: str = None,
        start_time: datetime.datetime = None,
    ) -> Union[int, Awaitable[int]]:
        return self._sync(
            self._get_cluster_states_declarative,
            cluster_id=cluster_id,
            account=account,
            start_time=start_time,
        )

    @overload
    def cluster_logs(
        self,
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
        errors_only: bool = False,
    ) -> Logs:
        ...

    @overload
    def cluster_logs(
        self,
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
        errors_only: bool = False,
    ) -> Awaitable[Logs]:
        ...

    @track_context
    async def _cluster_logs(
        self,
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
        errors_only: bool = False,
    ) -> Logs:
        def is_errored(process):
            process_state, instance_state = get_process_instance_state(process)
            return (
                process_state == ProcessStateEnum.error
                or instance_state == InstanceStateEnum.error
            )

        account = account or self.default_account

        # hits endpoint in order to get scheduler and worker instance names
        cluster_info = await self._get_cluster_details(
            cluster_id=cluster_id, account=account
        )

        try:
            scheduler_name = cluster_info["scheduler"]["instance"]["name"]
        except (TypeError, KeyError):
            # no scheduler instance name in cluster info
            logger.warning(
                "No scheduler found when attempting to retrieve cluster logs."
            )
            scheduler_name = None

        worker_names = [
            worker["instance"]["name"]
            for worker in cluster_info["workers"]
            if worker["instance"] and (not errors_only or is_errored(worker))
        ]

        LabeledInstance = namedtuple("LabeledInstance", ("name", "label"))

        instances = []
        if (
            scheduler
            and scheduler_name
            and (not errors_only or is_errored(cluster_info["scheduler"]))
        ):
            instances.append(LabeledInstance(scheduler_name, "Scheduler"))
        if workers and worker_names:
            instances.extend(
                [
                    LabeledInstance(worker_name, worker_name)
                    for worker_name in worker_names
                ]
            )

        async def instance_log_with_semaphor(semaphor, **kwargs):
            async with semaphor:
                return await self._instance_logs(**kwargs)

        # only get 100 logs at a time; the limit here is redundant since aiohttp session already limits concurrent
        # connections but let's be safe just in case
        semaphor = asyncio.Semaphore(value=100)
        results = await asyncio.gather(
            *[
                instance_log_with_semaphor(
                    semaphor=semaphor, account=account, instance_name=inst.name
                )
                for inst in instances
            ]
        )

        out = {
            instance_label: instance_log
            for (_, instance_label), instance_log in zip(instances, results)
            if len(instance_log)
        }

        return Logs(out)

    def cluster_logs(
        self,
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
        errors_only: bool = False,
    ) -> Union[Logs, Awaitable[Logs]]:
        return self._sync(
            self._cluster_logs,
            cluster_id=cluster_id,
            account=account,
            scheduler=scheduler,
            workers=workers,
            errors_only=errors_only,
        )

    async def _instance_logs(self, account: str, instance_name: str, safe=True) -> Log:
        response = await self._do_request(
            "GET",
            self.server
            + "/api/v2/instances/{}/instance/{}/logs".format(account, instance_name),
        )
        if response.status >= 400:
            if safe:
                logger.warning(f"Error retrieving logs for {instance_name}")
                return Log()
            await handle_api_exception(response)

        data = await response.json()

        messages = "\n".join(logline.get("message", "") for logline in data)

        return Log(messages)

    @track_context
    async def _scale_up(self, cluster_id: int, n: int, account: str = None) -> Dict:
        """
        Increases the number of workers by ``n``.
        """
        account = account or self.default_account
        response = await self._do_request(
            "POST",
            f"{self.server}/api/v2/workers/account/{account}/cluster/{cluster_id}/",
            json={"n_workers": n},
        )
        if response.status >= 400:
            await handle_api_exception(response)

        workers_info = await response.json()

        return {"workers": {w["name"] for w in workers_info}}

    @track_context
    async def _scale_down(
        self, cluster_id: int, workers: Set[str], account: str = None
    ) -> None:
        pass
        account = account or self.default_account
        response = await self._do_request(
            "DELETE",
            f"{self.server}/api/v2/workers/account/{account}/cluster/{cluster_id}/",
            params={"name": workers},
        )
        if response.status >= 400:
            await handle_api_exception(response)


Cloud = CloudBeta


def cluster_logs(
    cluster_id: int,
    account: str = None,
    scheduler: bool = True,
    workers: bool = True,
    errors_only: bool = False,
):
    """
    Returns cluster logs as a dictionary, with a key for the scheduler and each worker.

    .. versionchanged:: 0.2.0
       ``cluster_name`` is no longer accepted, use ``cluster_id`` instead.
    """
    with Cloud() as cloud:
        return cloud.cluster_logs(cluster_id, account, scheduler, workers, errors_only)


def cluster_details(
    cluster_id: int,
    account: str = None,
) -> dict:
    """
    Get details of a cluster as a dictionary.
    """
    with CloudBeta() as cloud:
        return cloud.cluster_details(
            cluster_id=cluster_id,
            account=account,
        )


def log_cluster_debug_info(
    cluster_id: int,
    account: str = None,
):
    with CloudBeta() as cloud:
        details = cloud.cluster_details(cluster_id, account)
        logger.debug("Cluster details:")
        logger.debug(json.dumps(details, indent=2))

        states_by_type = cloud.get_cluster_states(cluster_id, account)

        logger.debug("cluster state history:")
        log_states(flatten_log_states(states_by_type), level=logging.DEBUG)

        # log the scheduler logs (if errored), and up to 1 errored worker
        instance_logs = cloud.cluster_logs(cluster_id, account, errors_only=True)
        logger.debug("Finding errored scheduler instance log:")
        try:
            logger.debug(instance_logs.pop("Scheduler"))
        except KeyError:
            logger.debug("Did not find any errored scheduler instance logs.")

        logger.debug("Finding errored worker instance log:")
        try:
            worker_log = next(iter(instance_logs.values()))
            logger.debug(worker_log)
        except StopIteration:
            logger.debug("Did not find any errored worker instance logs.")


def create_cluster(
    name: str = None,
    *,
    software: str = None,
    worker_options: dict = None,
    worker_cpu: int = None,
    worker_memory: int = None,
    scheduler_options: dict = None,
    scheduler_cpu: int = None,
    scheduler_memory: int = None,
    account: str = None,
    workers: int = 0,
    environ: Optional[Dict] = None,
    scheduler_vm_types: Optional[list] = None,
    worker_vm_types: Optional[list] = None,
    backend_options: Optional[dict | BackendOptions] = None,
) -> int:
    """Create a cluster

    Parameters
    ---------
    name
        Name of cluster.
    software
        Identifier of the software environment to use, in the format (<account>/)<name>. If the software environment
        is owned by the same account as that passed into "account", the (<account>/) prefix is optional.

        For example, suppose your account is "wondercorp", but your friends at "friendlycorp" have an environment
        named "xgboost" that you want to use; you can specify this with "friendlycorp/xgboost". If you simply
        entered "xgboost", this is shorthand for "wondercorp/xgboost".

        The "name" portion of (<account>/)<name> can only contain ASCII letters, hyphens and underscores.
    worker_cpu
        Number of CPUs allocated for each worker. Defaults to 2.
    worker_memory
        Amount of memory to allocate for each worker. Defaults to 8 GiB.
    worker_options
        Mapping with keyword arguments to pass to ``worker_class``. Defaults to ``{}``.
    scheduler_cpu
        Number of CPUs allocated for the scheduler. Defaults to 1.
    scheduler_memory
        Amount of memory to allocate for the scheduler. Defaults to 4 GiB.
    scheduler_options
        Mapping with keyword arguments to pass to ``scheduler_class``. Defaults to ``{}``.
    account
        Name of the Coiled account to create the cluster in.
        If not provided, will default to ``Cloud.default_account``.
    workers
        Number of workers we to launch.
    environ
        Dictionary of environment variables.

    See Also
    --------
    coiled.Cluster
    """
    with CloudBeta(account=account) as cloud:
        return cloud.create_cluster(
            name=name,
            software=software,
            worker_options=worker_options,
            worker_cpu=worker_cpu,
            worker_memory=worker_memory,
            scheduler_options=scheduler_options,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            account=account,
            workers=workers,
            environ=environ,
            backend_options=backend_options,
            worker_vm_types=worker_vm_types,
            scheduler_vm_types=scheduler_vm_types,
        )


@list_docstring
def list_clusters(account=None):
    with CloudBeta() as cloud:
        return cloud.list_clusters(account=account)


@delete_docstring
def delete_cluster(name: str, account: str = None):
    with CloudBeta() as cloud:
        cluster_id = cloud.get_cluster_by_name(name=name, account=account)
        if cluster_id is not None:
            return cloud.delete_cluster(cluster_id=cluster_id, account=account)
