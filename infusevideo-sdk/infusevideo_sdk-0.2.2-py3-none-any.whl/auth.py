import configparser
from getpass import getpass
import os
import requests
import secrets
import sys
import time
from typing import Optional, Any
import urllib.parse
import webbrowser

from .authserver import AuthHTTPServer
from .config import Config, Profile
from .errors import AuthenticationError, ListenerBindError, Error


class Auth:
	def __init__(self, profile: Profile) -> None:
		self._cacheFile = Config.filename(f"cache-{profile.name}")
		self._cache = configparser.ConfigParser()
		self._cache.read(self._cacheFile)
		self._profile = profile

	@property
	def token(self) -> str:
		try:
			return self._cache["oauth2"]["token"]
		except KeyError:
			self.refresh()
		try:
			return self._cache["oauth2"]["token"]
		except KeyError:
			raise AuthenticationError("Unable to obtain access_token")

	@property
	def profileScope(self) -> set[str]:
		if not self._profile.scope:
			return set()
		return set(self._profile.scope.split())

	@property
	def requestedScope(self) -> set[str]:
		return set(self._cache["oauth2"]["requested"].split())

	@property
	def grantedScope(self) -> set[str]:
		return set(self._cache["oauth2"]["granted"].split())

	def refresh(self) -> None:
		if self._profile.auth == "human":
			self._refresh_human()
		elif self._profile.auth == "m2m":
			self._refresh_m2m()
		elif self._profile.auth == "human-oauth2-implicit":
			self._refresh_oauth2_implicit()
		else:
			raise NotImplementedError(f"Unknown auth type {self._profile.auth!r}")
		with open(self._cacheFile, "w") as f:
			self._cache.write(f)

	def _refresh_oauth2_implicit(self) -> None:
		"""Refresh the access token using the OAuth2 Implicit flow. Credentials are entered using
		a web browser that's automatically opened if required.
		"""
		# Generate state
		state = secrets.token_urlsafe(32)

		# Start listener
		for port in [19564, 29564]:
			try:
				server = AuthHTTPServer(port, state)
				break
			except OSError:
				# Port in use, ignore and keep trying
				pass
		else:
			raise ListenerBindError("Unable to bind the listener on localhost:19564 or :29564")

		# Open browser / redirect
		params = {
			"response_type": "token",
			"response_mode": "form_post",
			"client_id": self._profile.auth_client_id,
			"redirect_uri": f"http://localhost:{port}/authcallback",
			"scope": self._profile.scope,
			"audience": self._profile.auth_audience,
			"state": state,
		}
		if self._profile.scope_type != "global" and self._profile.account is not None:
			params["organization"] = self._profile.account
		url = f"https://{self._profile.auth_server}/authorize?{urllib.parse.urlencode(params)}"
		print(
			"Refreshing the auth token. Your web browser should open automatically. If you",
			"are already authenticated, the window should immediately close again. Otherwise,",
			"you will be presented with a login form.",
			file=sys.stderr,
		)
		try:
			webbrowser.open_new_tab(url)
		except webbrowser.Error:
			print(
				"It seems the SDK is unable to open a web browser for you. Please open the",
				"following URL manually in your browser:",
				url,
				file=sys.stderr,
			)

		# Wait for auth to complete
		print("Waiting for authentication to complete...", file=sys.stderr)
		authData = server.await_auth_data()
		self._store_cache(authData)
		print("Authentication complete.", file=sys.stderr)

	def _refresh_human(self) -> None:
		"""Refresh the access token using the OAuth2 Client Credentials flow, directly on the API.
		Credentials are entered in the console.
		"""
		username = input("Username: ")
		password = getpass("Password: ")

		data={
			"grant_type": "client_credentials",
		}
		if self._profile.scope is not None:
			data["scope"] = self._profile.scope
		if self._profile.scope_type == "global":
			data["account"] = None
		elif self._profile.account is not None:
			data["account"] = self._profile.account

		response = requests.post(
			f"https://{self._profile.server}/token",
			json=data,
			auth=requests.auth.HTTPBasicAuth(username, password),
		)
		if response.ok:
			authData = response.json()
			self._store_cache(authData)
		else:
			try:
				errorData = response.json()
				raise AuthenticationError(errorData["type"], errorData["message"])
			except (requests.JSONDecodeError, KeyError):
				raise Error(f"Unable to authenticate using human credentials: {response.text}")

	def _refresh_m2m(self) -> None:
		"""Refresh the access token using the OAuth2 Client Credentials flow, directly on the API.
		Special M2M credentials are stored in the configuration file.
		"""
		response = requests.post(
			f"https://{self._profile.server}/token/m2m",
			data={
				"grant_type": "client_credentials",
				"scope": self._profile.scope,
			},
			auth=requests.auth.HTTPBasicAuth(self._profile.m2m_id, self._profile.m2m_secret),
		)
		if response.ok:
			authData = response.json()
			self._store_cache(authData)
		else:
			try:
				errorData = response.json()
				raise AuthenticationError(errorData["type"], errorData["message"])
			except requests.JSONDecodeError:
				raise Error(f"Unable to authenticate using M2M credentials: {response.text}")

	def _store_cache(self, authData: dict[str, Any]) -> None:
		self._cache["oauth2"] = {
			"token": authData["access_token"],
			"expiry": str(int(time.time()) + int(authData["expires_in"])),
			"requested": self._profile.scope or "",
			"granted": authData["scope"]
		}

	def clear_cache(self) -> None:
		try:
			os.unlink(self._cacheFile)
		except FileNotFoundError:
			pass
