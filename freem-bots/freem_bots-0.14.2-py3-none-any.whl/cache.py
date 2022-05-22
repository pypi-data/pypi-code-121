from typing import Optional
import aiomcache
import aiomcache.client
import hashlib


class Cache:
	def __init__(self, host: str, port: int) -> None:
		self._client = aiomcache.Client(host, port)

	async def set(self, key: str, data: bytes) -> None:
		try:
			await self._client.set(self._get_key(key), data)  # pylint: disable=no-value-for-parameter
		except aiomcache.ClientException:
			return  # do nothing on cache failure
		except ConnectionResetError:
			return

	async def get(self, key: str) -> Optional[bytes]:
		try:
			return await self._client.get(self._get_key(key))  # type: ignore
		except aiomcache.ClientException:
			return None
		except ConnectionResetError:
			return None

	def _get_key(self, key: str) -> bytes:
		encoded = hashlib.md5(key.encode('utf-8')).hexdigest()  # nosec
		return encoded.encode('utf-8')
