from strangeworks.errors.error import StrangeworksError
from strangeworks.rest_client.rest_client import StrangeworksRestClient
from typing import List, Union


class Backend:
    __plugin_urls = {
        "aws": "/plugins/aws",
        "rigetti": "/plugins/rigetti",
        "ibm": "/plugins/ibmq",
        "azure": "/plugins/azure",
        "dwave": "/plugins/dwave",
    }

    def __init__(
        self,
        id: str = None,
        provider_id: str = None,
        name: str = None,
        provider_slug: str = None,
        remote_backend_id: str = None,
        plugin_url: str = None,
        backend_type: str = None,
        selector_id: str = None,
        backend_data: dict = None,
    ):
        self.__id = id
        self.__provider_id = provider_id
        self.__name = name
        self.__provider_slug = provider_slug
        self.__remote_backend_id = remote_backend_id
        self.__plugin_url = plugin_url
        self.__backend_type = backend_type
        self.__selector_id = selector_id
        self.__backend_data = backend_data

    @classmethod
    def from_cgw(cls, backend: dict) -> "Backend":
        id = backend.get("id", "")
        provider_id = backend.get("providerId", "")
        name = backend.get("name", "")
        provider_slug = backend.get("providerName", "")
        remote_backend_id = backend.get("remoteBackendId", "")
        backend_type = backend.get("backendType", "")
        backend_data = backend.get("backendData", {})
        return Backend(
            id=id,
            provider_id=provider_id,
            name=name,
            provider_slug=provider_slug,
            remote_backend_id=remote_backend_id,
            plugin_url=cls.__plugin_urls.get(provider_slug, ""),
            backend_type=backend_type,
            selector_id=f"{provider_slug}.{name}",
            backend_data=backend_data,
        )

    def name(self) -> str:
        return self.__name

    def backend_type(self) -> str:
        return self.__backend_type

    def plugin_url(self) -> str:
        return self.__plugin_url

    def provider(self) -> str:
        return self.__provider_slug

    def selector_id(self) -> str:
        return self.__selector_id

    def backend_data(self) -> dict:
        return self.__backend_data

    def backend_data(self) -> dict:
        return self.__backend_data

    def __repr__(self):
        return self.selector_id()

    def __str__(self):
        return self.selector_id()


class BackendService:
    def __init__(
        self,
        sw_rest_client,
        backend: Union[str, Backend] = None,
        backends: List[Backend] = [],
    ) -> None:
        self.__rest_client = sw_rest_client
        self.__backends = backends
        self.__selected_backend = BackendService.__obj_to_backend(backend)

    @classmethod
    def __obj_to_backend(cls, b: Union[str, "Backend"]) -> "Backend":
        if b and isinstance(b, str):
            b = Backend(selector_id=b)
        return b

    def __fetch_backends(
        self,
        url: str,
        selected_backend: Union[str, "Backend"],
        pprint: bool,
        filters=None,
    ):
        response = self.__rest_client.get(url)
        backends = []
        for account_slug, values in response.items():
            for value in values:
                b = value.get("backends", [])
                provider_backends = map(Backend.from_cgw, b)
                backends.extend(provider_backends)
        backends = list(filter(filters, backends))
        backends = list(
            filter(
                # TODO: include ibm as circuit runner target
                lambda b: not (b.provider() == "ibm"),
                backends,
            )
        )

        seen = set()
        for existing_backends in self.__backends:
            seen.add(existing_backends.selector_id())

        selected_backend = BackendService.__obj_to_backend(selected_backend)
        for backend in backends:
            if backend.selector_id() in seen:
                continue

            self.__backends.append(backend)
            if (
                selected_backend is not None
                and selected_backend.selector_id() == backend.selector_id()
            ):
                self.__selected_backend = backend
        # pprint backends if user sets option to true
        if pprint:
            for backend in self.__backends:
                print("=" * 50)
                print(f"Backend ID: {backend.selector_id()}")
                print(f"Backend provider: {backend.provider()}")

    def get_backends(
        self,
        selected_backend: Union[str, "Backend"] = None,
        pprint: bool = True,
        filters=None,
    ) -> List["Backend"]:
        # if len(self.__backends) == 0:
        self.__fetch_backends("/backends", selected_backend, pprint, filters)
        return self.__backends

    def select_backend(
        self, selected_backend: Union[str, "Backend"] = None
    ) -> "Backend":
        if not selected_backend:
            raise StrangeworksError.invalid_argument(
                "Specify a backend name or backend object"
            )
        if len(self.__backends) == 0:
            self.get_backends(pprint=False)
        selected_backend = BackendService.__obj_to_backend(selected_backend)
        selected = next(
            filter(
                lambda b: b.selector_id() == selected_backend.selector_id(),
                self.__backends,
            ),
            None,
        )
        if not selected:
            raise StrangeworksError.invalid_argument(
                f"Backend {selected_backend.name()} not available"
            )
        self.__selected_backend = selected
        return self.__selected_backend

    def selected_backend(self) -> "Backend":
        if not self.__selected_backend:
            raise StrangeworksError.invalid_argument(
                f"No backend selected. Use select_backend to set one"
            )
        return self.__selected_backend

    def _new_client(self, rest_client: StrangeworksRestClient = None):
        self.__rest_client = rest_client
