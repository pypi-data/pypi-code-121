import configparser
import inspect
from pydantic import BaseSettings, ValidationError, validator, Field
import os
import sys
from typing import Optional, Literal, Any

from .errors import ConfigurationError, ConfigAlreadyExists, ConfigNotFound, InvalidScopeError
from .scope import resolve_scope


class Profile(BaseSettings):
	name: str
	server: str = "api.infuse.video"
	auth: Literal["m2m", "human", "human-oauth2-implicit"] = "human"
	scope_type: Literal["account", "global"] = "account"
	account: Optional[str] = Field(
		default=None,
		alias="organization",
	)
	m2m_id: Optional[str] = None
	m2m_secret: Optional[str] = None
	scope: Optional[str]
	auth_server: str = "infuse-video.eu.auth0.com"
	auth_client_id: str = "FZk0cmoF9orL9IJ9s3EQA5ZgT2IeOXRP"
	auth_audience: str = "infuse-api"

	class Config:
		allow_population_by_field_name = True

	@validator("scope_type")
	def global_no_m2m(cls, scope_type: str, values: dict[str, Any]) -> str:
		if scope_type == "global" and values.get("auth", None) == "m2m":
			raise AssertionError(
				"At this moment, scope_type = global is not compatible with auth = m2m. "
				"Use auth = human instead."
			)
		return scope_type

	@validator("account")
	def account_not_if_m2m(cls, account: Optional[str], values: dict[str, Any]) -> Optional[str]:
		if account is None:
			return account
		if values.get("scope_type", "account") == "global":
			print(
				(
					"You have specified an account with scope_type=global. The account setting "
					"will be ignored and the global account will be used instead."
				),
				file=sys.stderr,
			)
		if values.get("auth", None) == "m2m":
			print(
				(
					"You have specified an account in a profile with M2M auth. The account setting "
					"will be ignored, as the specified credentials are linked to a single account."
				),
				file=sys.stderr,
			)
		return account

	@validator("m2m_id", "m2m_secret")
	def m2m_if_m2m(cls, m2m_cred: Optional[str], values: dict[str, Any]) -> Optional[str]:
		if values.get("auth", None) == "m2m" and m2m_cred is None:
			raise ValueError("This field must be defined when auth = m2m")
		return m2m_cred

	@validator("scope")
	def scope_optional_resolve(cls, scope: Optional[str], values: dict[str, Any]) -> Optional[str]:
		if not scope:
			if values.get("auth", None) == "m2m":
				raise AssertionError(
					"For M2M auth, a scope needs to be defined explicitly in the profile.",
				)
			return scope
		try:
			resolved = resolve_scope(set(scope.split()))
			return " ".join(sorted(resolved))
		except InvalidScopeError as e:
			raise ValueError(str(e))


class Config:
	_configDir = os.path.join(os.path.expanduser("~"), ".infusevideo")
	_configFilename = "config"

	@classmethod
	def filename(cls, filename: str) -> str:
		return os.path.join(cls._configDir, filename)

	@staticmethod
	def sample_config_contents(account: Optional[str] = None) -> str:
		return inspect.cleandoc(f"""
			[settings]
			# Which profile to use when not specified
			defaultProfile = default

			[profile-default]
			# Default sample profile for human auth

			# The account to authenticate with.
			# Optional for human auth. Uses the default account for your user when omitted.
			# Ignored for M2M, the account is determined by the credentials.
			{'' if account else '#'}account = {account if account else 'change'}

			# What scope to request. Multiple may be specified, space-separated.
			# Optional for human auth, defaults to 'all' when omitted.
			# Mandatory for M2M auth.
			#scope = read write

			# What type of authentication to use. Options: human, m2m
			# Default: human
			#auth = human

			[profile-m2m]
			# Sample profile for m2m auth

			# What scope to request. Multiple may be specified, space-separated.
			# Mandatory for M2M auth.
			scope = read write

			# What type of authentication to use. Options: human, m2m
			auth = m2m

			# When using m2m auth, specify the id and secret here
			m2m_id = change
			m2m_secret = change
		""")

	@classmethod
	def generate_sample_config(cls, account: Optional[str] = None) -> str:
		# Check if config does not exist
		configPath = cls.filename(cls._configFilename)
		if os.path.exists(configPath):
			raise ConfigAlreadyExists(configPath)
		if not os.path.exists(cls._configDir):
			os.mkdir(cls._configDir)
		with open(configPath, "wt") as f:
			f.write(cls.sample_config_contents(account))
			f.write("\n")
		return configPath

	def __init__(self, disableHumanAuth: bool = False):
		self._configPath = self.filename(self._configFilename)
		self._config = configparser.ConfigParser()
		if not os.path.exists(self._configPath):
			if disableHumanAuth:
				raise ConfigNotFound(
					self._configPath,
					"A configuration file is required for non-interactive authentication.",
				)
			self._config.read_string(self.sample_config_contents())
		else:
			self._config.read(self.configPath)
		self._disableHumanAuth = disableHumanAuth

	@property
	def configPath(self) -> str:
		return self._configPath

	@property
	def defaultProfile(self) -> str:
		try:
			return self._config["settings"]["defaultProfile"]
		except KeyError:
			return "default"

	def get_profile(self, name: str) -> Profile:
		try:
			profile = Profile(name=name, **self._config[f"profile-{name}"])
			if self._disableHumanAuth and profile.auth == "human":
				raise ConfigurationError(
					f"Requested human auth be disabled, but profile {name} has human auth set.",
				)
			return profile
		except KeyError:
			raise ConfigurationError(f"Profile {name!r} not defined in configuration file")
		except ValidationError as e:
			raise ConfigurationError(f"Invalid profile {name!r}: {e}")
