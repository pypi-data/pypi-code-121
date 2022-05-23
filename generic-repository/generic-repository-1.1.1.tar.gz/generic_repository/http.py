import cgi
import functools
import math
import typing
from http import HTTPStatus

import httpx

from .base import GenericBaseRepository
from .exceptions import InvalidPayloadException, ItemNotFoundException
from .mapper import LambdaMapper, Mapper


class HttpRepository(
    GenericBaseRepository[str, typing.Any, typing.Any, typing.Any, typing.Any]
):
    """An http repository.

    To use it, you must provide an httpx async client.

    For example:
    >>> import asyncio
    >>> from httpx import AsyncClient
    >>> client = AsyncClient(base_url='https://jsonplaceholder.typicode.com')
    >>> repo = HttpRepository(client, base_url='/posts')
    >>> repo
    <generic_repository.http.HttpRepository object at ...>
    >>>
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        base_url: typing.Optional[str] = None,
        request_params: typing.Optional[typing.Dict[str, typing.Any]] = None,
        count_mapper: typing.Optional[Mapper[typing.Any, int]] = None,
        list_mapper: typing.Optional[
            Mapper[typing.Any, typing.List[typing.Any]]
        ] = None,
        add_slash: bool = True,
    ) -> None:
        super().__init__()
        self.client = client
        self._base_url = base_url
        self._request_params = request_params
        self.count_mapper = count_mapper or LambdaMapper(
            lambda x: len(typing.cast(typing.List[typing.Any], x))
        )

        self.list_mapper = list_mapper or LambdaMapper(
            lambda x: typing.cast(typing.List[typing.Any], x)
        )
        self.add_slash = add_slash

    @functools.cached_property
    def base_url(self):
        if self._base_url is not None:  # pragma: nocover
            return self._base_url
        return ""

    @functools.cached_property
    def request_params(self):
        params = {}

        if self._request_params is not None:  # pragma nocover
            params.update(self._request_params)

        return params

    async def process_response(self, response: httpx.Response):
        self._ensure_success(response)

        if response.status_code == HTTPStatus.NO_CONTENT:
            return None
        elif (
            response.status_code >= 300 and response.status_code < 400
        ):  # pragma nocover
            raise RuntimeError("A redirect found.")

        try:
            if self.is_json(response):
                return response.json()
            else:  # pragma nocover
                # Return the response text representation:
                return response.text
        finally:
            await response.aclose()

    @classmethod
    def _ensure_success(cls, response):
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as ex:
            if response.status_code == HTTPStatus.NOT_FOUND:
                raise ItemNotFoundException("Cannot find the remote resource.") from ex
            elif response.status_code in (
                HTTPStatus.BAD_REQUEST,
                HTTPStatus.UNPROCESSABLE_ENTITY,
            ):
                raise InvalidPayloadException() from ex
            else:
                raise

    @classmethod
    def is_json(cls, response: httpx.Response):
        content_type, options = cgi.parse_header(response.headers.get("content-type"))
        main_type, sub_type = content_type.split("/")
        is_json = sub_type.startswith("json")
        return is_json

    async def get_by_id(self, id):
        """Return a resource by it's ID.

        Args:
            id (str): The ID of the resource to retrieve.

        Returns:
            typing.Dict[str, Any]: The resource as Json.

        >>> import asyncio
        >>> import httpx
        >>> loop = asyncio.new_event_loop()
        >>> repo = HttpRepository(
        ...     httpx.AsyncClient(base_url='https://jsonplaceholder.typicode.com/posts')
        ... )
        >>> loop.run_until_complete(repo.get_by_id('1'))
        {...}
        >>> loop.run_until_complete(repo.get_by_id(200))
        Traceback (most recent call last):
          ...
        generic_repository.exceptions.ItemNotFoundException: ...
        >>> loop.close()
        >>>
        """
        return await self.process_response(await self.client.get(self.get_id_url(id)))

    async def _get_list(self, *, offset=None, size=None, **query_filters):
        params = {
            **self.request_params,
            **query_filters,
        }
        if size is not None:
            params.update(size=size)
            if offset is not None:
                params.update(page=math.ceil(offset / size))

        return await self.process_response(
            await self.client.get(
                self.list_url,
                params=params,
            )
        )

    @property
    def list_url(self):
        """Retrieve the real base_url.

        Returns:
            str: The base URL built from the passed base url in the constructor.

        >>> base_url = 'https://example.com/resource'
        >>> repo = HttpRepository(
        ...     httpx.AsyncClient(),
        ...     base_url=base_url,
        ...     add_slash=False,
        ... )
        >>> repo.list_url
        'https://example.com/resource'
        >>> repo2 = HttpRepository(
        ...     repo.client, base_url=base_url, add_slash=True
        ... )
        >>> repo2.list_url
        'https://example.com/resource/'
        >>>
        """
        list_url = self.base_url
        if self.add_slash:
            list_url = f"{list_url}/"
        return list_url

    async def get_list(self, *, offset=None, size=None, **query_filters):
        """Return a list of items.

        Args:
            offset (int, optional): Where to start from.. Defaults to None.
            size (int, optional): How many items to retrieve. Defaults to None.

        Returns:
            list: Items from the remote source.

        >>> import asyncio
        >>> import httpx
        >>> loop = asyncio.new_event_loop()
        >>> repo = HttpRepository(
        ...     httpx.AsyncClient(base_url='https://jsonplaceholder.typicode.com/posts')
        ... )
        >>> loop.run_until_complete(repo.get_list(offset=10, size=3))
        [...]
        >>> loop.run_until_complete(repo.get_list(offset=10))
        [...]
        >>> loop.run_until_complete(repo.get_list(size=3))
        [...]
        >>> loop.close()
        >>>
        """
        return self.list_mapper(
            await self._get_list(size=size, offset=offset, **query_filters)
        )

    async def get_count(self, **query_filters):
        """Return how many items the remote source have in it's database.

        Returns:
            int: How many items.

        >>> import asyncio
        >>> import httpx
        >>> loop = asyncio.new_event_loop()
        >>> repo = HttpRepository(
        ...     httpx.AsyncClient(base_url='https://jsonplaceholder.typicode.com/posts')
        ... )
        >>> loop.run_until_complete(repo.get_count())
        100
        >>> loop.close()
        >>>
        """
        return self.count_mapper(await self._get_list(**query_filters))

    async def add(self, payload) -> typing.Any:
        """Add a new item to the remote resource.

        Args:
            payload (typing.Any): A payload to use as the data source.

        Returns:
            typing.Any: The newly created item.


        >>> import asyncio
        >>> import httpx
        >>> loop = asyncio.new_event_loop()
        >>> repo = HttpRepository(
        ...     httpx.AsyncClient(base_url='https://jsonplaceholder.typicode.com/posts')
        ... )
        >>> payload = {
        ...     'userId': 1,
        ...     'title': 'Test title',
        ...     'body': 'Just a body...',
        ... }
        >>> result = loop.run_until_complete(repo.add(payload))
        >>> result
        {...}
        >>> result['title']
        'Test title'
        >>> payload2 = [
        ...     'userId',
        ...     'title',
        ...     'body',
        ... ]
        >>> loop.close()
        >>>
        """
        return await self.process_response(
            await self.client.post(self.list_url, json=payload)
        )

    async def update(self, id, payload):
        """Update the remote resource.

        Args:
            id (str): The resource ID.
            payload (Any): The payload to send. Must be json-compatible.

        Returns:
            Any: Json-compatibel updated data.

        >>> from asyncio import new_event_loop
        >>> loop = new_event_loop()
        >>> repo = HttpRepository(
        ...     httpx.AsyncClient(),
        ...     base_url='https://jsonplaceholder.cypress.io/posts'
        ... )
        >>> result = loop.run_until_complete(
        ...     repo.update('2', {'title': 'Another title.'})
        ... )
        >>> result['title']
        'Another title.'
        >>> loop.close()
        >>>
        """
        return await self.process_response(
            await self.client.patch(self.get_id_url(id), json=payload)
        )

    def get_id_url(self, id):
        return f"{self.base_url}/{id}"

    async def replace(self, id, payload):
        """Send a replace request.

        Args:
            id (str): The resource ID to replace.
            payload (Any): The new data for the resource.

        Returns:
            Any: The newly updated resource.


        >>> from asyncio import new_event_loop
        >>> loop = new_event_loop()
        >>> repo = HttpRepository(
        ...     httpx.AsyncClient(),
        ...     base_url='https://jsonplaceholder.cypress.io/posts'
        ... )
        >>> loop.run_until_complete(
        ...     repo.replace('1', {'userId': 2, 'title': 'Other title.'})
        ... )
        {... 'title': 'Other title.'...}
        >>> loop.close()
        >>>
        """
        return await self.process_response(
            await self.client.put(self.get_id_url(id), json=payload)
        )

    async def remove(self, id: str):
        """Remove the specified remote resource.

        Args:
            id (str): The resource ID to remove.

        >>> from asyncio import new_event_loop
        >>> loop = new_event_loop()
        >>> repo = HttpRepository(
        ...     httpx.AsyncClient(),
        ...     base_url='https://jsonplaceholder.cypress.io/posts'
        ... )
        >>> loop.run_until_complete(repo.remove('1'))

        >>> loop.run_until_complete(repo.remove('200'))
        Traceback (most recent call last):
          ...
        generic_repository.exceptions.ItemNotFoundException: ...
        >>> loop.close()
        >>>
        >>>
        """
        await self.process_response(await self.client.delete(self.get_id_url(id)))
