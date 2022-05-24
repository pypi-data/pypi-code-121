from typing import Any, Optional, Union

from . import filterwarnings
from .client import Client
from .config import Config, Profile
from .errors import Error


__all__ = (
	"Config",
	"Error",
	"InfuseVideo",
)


class InfuseVideo:
	def __init__(self, profile: Optional[str] = None, disableHumanAuth: bool = False) -> None:
		self._profile: Optional[Profile] = None
		self._disableHumanAuth = disableHumanAuth
		self._client: Optional[Client] = None
		self._config = config.Config(disableHumanAuth=disableHumanAuth)
		if profile is None:
			profile = self._config.defaultProfile
		self.profile = profile

	@property
	def profile(self) -> Profile:
		assert self._profile is not None
		return self._profile

	@profile.setter
	def profile(self, newProfile: Union[str, Profile]) -> None:
		if isinstance(newProfile, str):
			self._profile = self._config.get_profile(newProfile)
		else:
			self._profile = newProfile
		self._client = Client(self._profile)

	@property
	def client(self) -> Client:
		assert self._client is not None
		return self._client

	def get(self, *args: Any, **kwargs: Any) -> Client.Response:
		return self.client.request("GET", *args, **kwargs)

	def post(self, *args: Any, **kwargs: Any) -> Client.Response:
		return self.client.request("POST", *args, **kwargs)

	def patch(self, *args: Any, **kwargs: Any) -> Client.Response:
		return self.client.request("PATCH", *args, **kwargs)

	def put(self, *args: Any, **kwargs: Any) -> Client.Response:
		return self.client.request("PUT", *args, **kwargs)

	def delete(self, *args: Any, **kwargs: Any) -> Client.Response:
		return self.client.request("DELETE", *args, **kwargs)
